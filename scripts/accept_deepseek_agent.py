"""Zero-cost preflight by default. --live --authorize-paid-calls permits one A/B/C run."""

import argparse
import inspect
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import httpx  # noqa: E402
from fastapi.encoders import jsonable_encoder  # noqa: E402

from backend.app.agents import deepseek  # noqa: E402
from backend.app.agents.llm import TOOL_MODELS, LLMError, configured  # noqa: E402
from backend.app.agents.planner import interpret  # noqa: E402
from backend.app.agents.workflow import run_research  # noqa: E402
from backend.app.data.ingest import Repository  # noqa: E402
from backend.app.reports.audit import code_version  # noqa: E402
from backend.app.science.decision_schemas import AgentRequest  # noqa: E402
from scripts.accept_real_agent import SCENARIOS, independently_check  # noqa: E402


def load_key_from_user_scope():
    """Read only on explicit CLI invocation; never modifies the permanent environment."""
    if os.getenv("DEEPSEEK_API_KEY"):
        return True
    if os.name == "nt":
        import winreg

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                value, _ = winreg.QueryValueEx(key, "DEEPSEEK_API_KEY")
            if isinstance(value, str) and value:
                os.environ["DEEPSEEK_API_KEY"] = value
                return True
        except OSError:
            pass
    return False


def check_schema(schema):
    allowed = {"type", "enum", "properties", "required", "additionalProperties", "items", "anyOf"}
    assert set(schema) <= allowed
    if "properties" in schema:
        assert schema["type"] == "object" and schema["additionalProperties"] is False
        assert set(schema["required"]) == set(schema["properties"])
        for value in schema["properties"].values():
            check_schema(value)
    if "items" in schema:
        check_schema(schema["items"])
    for value in schema.get("anyOf", []):
        check_schema(value)


def preflight(repository=None):
    repo = repository or Repository()
    checks = {}
    payload = deepseek.request_payload(SCENARIOS["A"], repo.classes())
    checks["key_present"] = bool(os.getenv("DEEPSEEK_API_KEY"))
    checks["explicit_configuration"] = (
        configured()
        and os.getenv("OXYPROOF_LLM_PROVIDER") == "deepseek"
        and os.getenv("OXYPROOF_LLM_MODEL") == deepseek.MODEL
    )
    checks["official_endpoint"] = deepseek.ENDPOINT == "https://api.deepseek.com/responses"
    checks["three_tools"] = set(TOOL_MODELS) == {
        "screen_published_records",
        "analyze_temperature_interval",
        "inspect_scientific_evidence",
    }
    for tool in payload["tools"]:
        check_schema(tool["parameters"])
    checks["schemas_reviewed"] = len(payload["tools"]) == 3
    checks["bounded_non_thinking_request"] = (
        payload["reasoning"] == {"effort": "none"}
        and payload["max_output_tokens"] == 1200
        and payload["stream"] is False
    )
    checks["no_ignored_parallel_limit_reliance"] = not (
        {"parallel_tool_calls", "max_tool_calls", "store", "previous_response_id"} & payload.keys()
    )
    checks["no_transport_retries"] = (
        inspect.signature(httpx.HTTPTransport).parameters["retries"].default == 0
    )
    checks["cloud_not_disabled"] = os.getenv("OXYPROOF_DISABLE_CLOUD") != "1"
    ledger = deepseek.read_ledger()
    checks["fresh_sprint_budget"] = not ledger["attempts"] and not ledger.get("halted")
    offline = []
    for name, question in SCENARIOS.items():
        execution = run_research(
            AgentRequest(goal=question, row_ids=[] if name == "B" else [1, 2, 3]), repo
        )
        offline.append(
            {
                "scenario": name,
                "status": independently_check(name, execution, repo),
                "trace": execution["execution_trace"].model_dump(),
            }
        )
    checks["offline_independent_assertions"] = all(s["status"] == "PASS" for s in offline)
    coverage = interpret(SCENARIOS["C"], repo.classes()).coverage
    text = " ".join(s.text for s in coverage.unresolved)
    checks["humidity_and_lifetime_fail_closed"] = (
        not coverage.complete and "humidity" in text and "10,000 operating hours" in text
    )
    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "offline_scenarios": offline,
        "reviewed_request": payload,
        "prior_model_requests": len(ledger["attempts"]),
        "source": repo.source.model_dump(),
        "code_version": code_version(),
        "executed_at_utc": datetime.now(UTC).isoformat(),
    }


def acceptance(*, live=False, authorized=False, progress=None):
    """No discovery, connectivity ping, automatic retries, second generation or resume."""
    repo = Repository()
    report = {
        "phase": "2.6.2",
        "provider": "DeepSeek",
        "requested_model": deepseek.MODEL,
        "actual_models": [],
        "endpoint": deepseek.ENDPOINT,
        "executed_at_utc": datetime.now(UTC).isoformat(),
        "status": "NOT_RUN",
        "real_provider_requests_attempted": 0,
        "real_provider_requests_succeeded": 0,
        "maximum_requests": 3,
        "automatic_retries": 0,
        "live_requested": live,
        "paid_calls_authorized": authorized,
        "key_status": "PRESENT" if os.getenv("DEEPSEEK_API_KEY") else "MISSING",
        "code_version": code_version(),
        "source": repo.source.model_dump(),
        "selection_scope": "A explicitly supplies evaluation rows [1,2,3]; B uses the named published Huang group. Neither is autonomous material discovery.",
        "live_scenarios": [
            {"scenario": n, "request": q, "status": "NOT_RUN"} for n, q in SCENARIOS.items()
        ],
    }
    try:
        report["preflight"] = preflight(repo)
    except (ValueError, AssertionError, LLMError) as exc:
        report["preflight"] = {
            "status": "FAIL",
            "error": type(exc).__name__ + ": local preflight failed",
        }
    if not (live and authorized and report["preflight"]["status"] == "PASS"):
        report["blocker"] = (
            "PREFLIGHT_FAILED"
            if report["preflight"]["status"] != "PASS"
            else "EXPLICIT_LIVE_AND_PAID_AUTHORIZATION_REQUIRED"
        )
        return report
    systemic = False
    for scene in report["live_scenarios"]:
        if systemic:
            scene["blocker"] = (
                "SYSTEMIC_PROVIDER_FAILURE: no more requests without new owner authorization"
            )
            continue
        name, question = scene["scenario"], scene["request"]
        telemetry = {}
        try:
            execution = run_research(
                AgentRequest(
                    goal=question, row_ids=[] if name == "B" else [1, 2, 3], mode="REAL_LLM"
                ),
                repo,
                provider_metadata=telemetry,
            )
            scene["execution"] = jsonable_encoder(execution)
            scene["status"] = independently_check(name, execution, repo)
            trace = execution["execution_trace"]
            assert (
                trace.response_id
                and trace.model_selected_tool == trace.deterministically_expected_tool
                and trace.tool_agreement
            )
            assert trace.provider_metadata["provider"] == "DeepSeek"
            scene["independent_scientific_assertions"] = "PASS"
            scene["scientific_audit_verdict"] = trace.evidence_verdicts
            scene["refusal_origin"] = trace.refusal_origin
        except (LLMError, ValueError, AssertionError, StopIteration) as exc:
            scene.update(
                status="FAIL",
                error=str(exc)
                if isinstance(exc, LLMError)
                else type(exc).__name__ + ": independent acceptance failed",
            )
            systemic = bool(telemetry.get("systemic_failure"))
        scene["provider_evidence"] = telemetry
        report["real_provider_requests_attempted"] += int(telemetry.get("request_attempted", False))
        report["real_provider_requests_succeeded"] += int(scene["status"] == "PASS")
        returned = telemetry.get("returned_model")
        if returned and returned not in report["actual_models"]:
            report["actual_models"].append(returned)
        assert report["real_provider_requests_attempted"] <= 3
        if progress:
            progress(report)
        print(
            f"DEEPSEEK_SCENARIO_{name}={scene['status']} tool={telemetry.get('model_selected_tool')} latency={telemetry.get('wall_seconds')}s",
            flush=True,
        )
    successes = report["real_provider_requests_succeeded"]
    report["status"] = "VERIFIED" if successes == 3 else "PARTIAL" if successes else "FAILED"
    report["ledger"] = deepseek.read_ledger()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--authorize-paid-calls", action="store_true")
    args = parser.parse_args()
    load_key_from_user_scope()
    # These are process-scoped choices, never permanent Windows settings.
    with patch.dict(
        os.environ, {"OXYPROOF_LLM_PROVIDER": "deepseek", "OXYPROOF_LLM_MODEL": deepseek.MODEL}
    ):
        path = ROOT / (
            "artifacts/deepseek_live_acceptance.json"
            if args.live and args.authorize_paid_calls
            else "artifacts/deepseek_preflight.json"
        )
        if (
            args.live
            and args.authorize_paid_calls
            and (deepseek.read_ledger()["attempts"] or path.exists())
        ):
            raise SystemExit(
                "DEEPSEEK_LIVE_RUN_REFUSED: existing sprint evidence/budget; do not start a replacement run"
            )

        def persist(report):
            path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

        report = acceptance(live=args.live, authorized=args.authorize_paid_calls, progress=persist)
        persist(report)
        print("DEEPSEEK_KEY_STATUS=" + report["key_status"])
        print(
            f"REAL_LLM_STATUS={report['status']} requests={report['real_provider_requests_attempted']} succeeded={report['real_provider_requests_succeeded']}"
        )
        return int(
            (args.live and args.authorize_paid_calls and report["status"] != "VERIFIED")
            or report["preflight"]["status"] != "PASS"
        )


if __name__ == "__main__":
    raise SystemExit(main())
