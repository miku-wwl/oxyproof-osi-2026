"""Three-scene acceptance: offline by default; --local-live opts into local inference.

Live execution makes exactly one bounded provider request per scenario, no retries,
at most three requests. Paid OpenAI calls require BOTH --live --authorize-paid-calls.
"""

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fastapi.encoders import jsonable_encoder  # noqa: E402

from backend.app.agents.llm import LLMError, configured, provider  # noqa: E402
from backend.app.agents.workflow import run_research  # noqa: E402
from backend.app.data.ingest import Repository  # noqa: E402
from backend.app.reports.audit import code_version  # noqa: E402
from backend.app.science.decision_schemas import AgentExecution, AgentRequest  # noqa: E402
from benchmarks.reference_v2 import root_decimal, sigma_decimal  # noqa: E402

SCENARIOS = {
    "A": "Find promising published bulk oxygen-ion conductors around 600 degrees Celsius, show their conductivity estimates, and tell me what evidence supports the comparison.",
    "B": "How does the ranking of the three comparable Huang materials change from 700 K to 1000 K? Explain the change using their published activation energies.",
    "C": "Find oxygen-ion conductors at 600 °C that survive 10% humidity and remain stable for 10,000 operating hours.",
}


def independently_check(name, execution, repository):
    import math

    AgentExecution.model_validate(execution)
    trace, result = execution["execution_trace"], execution["result"]
    assert trace.research_question == SCENARIOS[name]
    assert trace.tool_name == execution["tool_name"]
    assert (
        trace.validated_arguments == execution["validated_arguments"] == result.validated_arguments
    )
    assert trace == result.execution_trace
    if name == "A":
        assert trace.tool_name == "screen_published_records"
        assert result.resolved_plan.temperature_k == 873.15
        assert [c.row_id for c in result.candidates] == [3, 2, 1]
        for c in result.candidates:
            raw = repository.by_id[c.row_id].raw
            suffix = "HT" if 873.15 > float(raw["T*"]) else ""
            assert c.raw_source_record == raw
            assert c.computed_values_with_units["conductivity"].unit == "S/cm"
            assert math.isclose(
                c.computed_values_with_units["conductivity"].value,
                float(sigma_decimal(raw, 873.15, suffix)),
                rel_tol=2e-14,
            )
    elif name == "B":
        assert trace.tool_name == "analyze_temperature_interval"
        assert result.resolved_plan["row_ids"] == [1, 2, 3]
        assert [p.temperature_k for p in result.selected_rankings] == [700, 1000]
        assert [p.ordering for p in result.selected_rankings] == [[1, 2, 3], [3, 2, 1]]
        for point, suffix in zip(result.selected_rankings, ["", "HT"], strict=True):
            for value in point.values:
                assert math.isclose(
                    value.conductivity_s_cm,
                    float(
                        sigma_decimal(
                            repository.by_id[value.row_id].raw, point.temperature_k, suffix
                        )
                    ),
                    rel_tol=2e-14,
                )
        for i, j, si, sj in [(1, 2, "", ""), (1, 3, "HT", ""), (2, 3, "HT", "")]:
            event = next(
                e for e in result.events if e.exact_continuous_crossing and e.row_ids == [i, j]
            )
            assert math.isclose(
                event.temperature_k,
                float(root_decimal(repository.by_id[i].raw, repository.by_id[j].raw, si, sj)),
                rel_tol=2e-13,
            )
        assert "uncertainty bounds unavailable" in result.crossover_qualification
    else:
        assert trace.execution_status == "ABSTAINED" and not result.candidates
        assert (
            not result.validated_arguments and result.evidence_verdict == "UNVERIFIED_CONSTRAINTS"
        )
        unresolved = " ".join(s.text for s in result.request_coverage.unresolved)
        assert "humidity" in unresolved and "10,000 operating hours" in unresolved
    return "PASS"


def acceptance(*, live=False, authorized=False):
    repository = Repository()
    runnable_live = live and authorized and configured() and provider() == "openai"
    output = {
        "phase": "2.6",
        "executed_at_utc": datetime.now(UTC).isoformat(),
        "status": "NOT_CONFIGURED" if not configured() else "PARTIAL",
        "provider": "OpenAI Responses",
        "model_used": None,
        "configuration": {
            "key_present": bool(os.getenv("OPENAI_API_KEY")),
            "model_present": bool(os.getenv("OXYPROOF_LLM_MODEL")),
        },
        "live_requested": live,
        "paid_calls_authorized_for_this_run": authorized,
        "real_provider_requests_attempted": 0,
        "max_requests_this_run": 3,
        "source": repository.source.model_dump(),
        "code_version": code_version(),
        "live_scenarios": [],
        "offline_scenarios": [],
        "live_traces": [],
        "limitations": [
            "Mock provider tests are not live acceptance.",
            "Conditional curated-fit results; original sample conditions and uncertainty remain unverified.",
            "Independent coverage is bounded English; extra unknown conditions still fail closed.",
        ],
    }
    for name, question in SCENARIOS.items():
        request = AgentRequest(goal=question, row_ids=[] if name == "B" else [1, 2, 3])
        offline_result = {"scenario": name, "mode": "OFFLINE_DETERMINISTIC"}
        try:
            execution = run_research(request, repository)
            offline_result["execution"] = jsonable_encoder(execution)
            offline_result["status"] = independently_check(name, execution, repository)
        except (ValueError, AssertionError, StopIteration) as exc:
            offline_result.update(
                status="FAIL", error=type(exc).__name__ + ": independent acceptance failed"
            )
        output["offline_scenarios"].append(offline_result)
        live_result = {"scenario": name, "request": question, "status": "NOT_RUN"}
        if runnable_live:
            output["real_provider_requests_attempted"] += 1
            assert output["real_provider_requests_attempted"] <= 3
            try:
                execution = run_research(
                    request.model_copy(update={"mode": "REAL_LLM"}), repository
                )
                live_result["execution"] = jsonable_encoder(execution)
                checked = independently_check(name, execution, repository)
                trace = execution["execution_trace"]
                assert trace.planning_source == "REAL_LLM" and trace.response_id and trace.model
                live_result.update(status=checked)
                output["live_traces"].append(trace.model_dump())
                output["model_used"] = trace.provider_metadata.get("returned_model") or trace.model
            except (LLMError, ValueError, AssertionError, StopIteration) as exc:
                live_result.update(
                    status="FAIL",
                    error=type(exc).__name__
                    + (
                        ": " + str(exc)
                        if isinstance(exc, LLMError)
                        else ": independent acceptance failed"
                    ),
                )
        output["live_scenarios"].append(live_result)
    if runnable_live:
        passes = sum(s["status"] == "PASS" for s in output["live_scenarios"])
        output["status"] = "VERIFIED" if passes == 3 else "PARTIAL" if passes else "FAILED"
    else:
        output["live_blocker"] = (
            "NOT_CONFIGURED"
            if not configured()
            else "EXPLICIT_LIVE_AND_PAID_AUTHORIZATION_FLAGS_REQUIRED"
        )
    return output


def local_acceptance():
    """Explicit owner-authorized localhost-only mode; three sequential calls, no retry."""
    from backend.app.agents.ollama import local_endpoint

    repository = Repository()
    output = {
        "phase": "2.6.1",
        "executed_at_utc": datetime.now(UTC).isoformat(),
        "status": "NOT_RUN",
        "provider": "Ollama Local",
        "model": "phi4-mini:latest",
        "endpoint": "http://127.0.0.1:11434/api/chat",
        "real_provider_requests_attempted": 0,
        "real_provider_requests_succeeded": 0,
        "max_primary_requests": 3,
        "automatic_retries": 0,
        "source": repository.source.model_dump(),
        "code_version": code_version(),
        "live_scenarios": [],
        "preflight": {},
        "selection_scope": "A uses owner-defined evaluation rows [1,2,3]; B uses the named published Huang demonstration, not autonomous material discovery.",
        "limitations": [
            "Curated-fit comparisons remain conditional; no validated uncertainty, humidity or lifetime evidence.",
            "Local invocation IDs are application-generated, never provider Response IDs.",
        ],
    }
    overrides = {
        "OXYPROOF_LLM_PROVIDER": "ollama",
        "OXYPROOF_LLM_MODEL": "phi4-mini:latest",
        "OXYPROOF_OLLAMA_BASE_URL": "http://127.0.0.1:11434",
    }
    with patch.dict(os.environ, overrides):
        assert local_endpoint() == output["endpoint"]
        try:
            with httpx.Client(timeout=5, trust_env=False, follow_redirects=False) as client:
                for name in ("version", "tags", "ps"):
                    response = client.get("http://127.0.0.1:11434/api/" + name)
                    response.raise_for_status()
                    output["preflight"][name] = response.json()
            installed = next(
                m for m in output["preflight"]["tags"]["models"] if m["name"] == output["model"]
            )
            assert "tools" in installed.get("capabilities", [])
            output["model_digest"] = installed["digest"]
        except (httpx.HTTPError, ValueError, KeyError, StopIteration, AssertionError) as exc:
            output.update(status="FAILED", preflight_error=type(exc).__name__)
            return output
        systemic = False
        for name, question in SCENARIOS.items():
            scene = {"scenario": name, "request": question, "status": "NOT_RUN"}
            output["live_scenarios"].append(scene)
            if systemic:
                scene["blocker"] = (
                    "SYSTEMIC_PROVIDER_FAILURE: diagnostic required before more calls"
                )
                continue
            telemetry = {}
            scene["code_version"] = code_version()
            output["real_provider_requests_attempted"] += 1
            try:
                execution = run_research(
                    AgentRequest(
                        goal=question, row_ids=[] if name == "B" else [1, 2, 3], mode="REAL_LLM"
                    ),
                    repository,
                    provider_metadata=telemetry,
                )
                scene["execution"] = jsonable_encoder(execution)
                trace = execution["execution_trace"]
                assert (
                    trace.model == "phi4-mini:latest"
                    and trace.local_invocation_id
                    and trace.response_id is None
                )
                assert (
                    trace.model_selected_tool == trace.deterministically_expected_tool
                    and trace.tool_agreement
                )
                scene["status"] = independently_check(name, execution, repository)
                scene["independent_scientific_assertions"] = "PASS"
            except (LLMError, ValueError, AssertionError, StopIteration) as exc:
                scene.update(
                    status="FAIL",
                    error=str(exc)
                    if isinstance(exc, LLMError)
                    else type(exc).__name__ + ": independent acceptance failed",
                )
                systemic = isinstance(exc, LLMError) and (
                    "HTTP_" in str(exc)
                    or "RESPONSE_FAILED" in str(exc)
                    or "NATIVE_TOOL_CALL_REQUIRED" in str(exc)
                )
            scene["provider_evidence"] = telemetry
            if telemetry.get("http_status") == 200 and telemetry.get("native_tool_call_count") == 1:
                output["real_provider_requests_succeeded"] += 1
            print(
                f"LOCAL_SCENARIO_{name}={scene['status']} {telemetry.get('wall_seconds')}s tool={telemetry.get('model_selected_tool')}",
                flush=True,
            )
        passes = sum(s["status"] == "PASS" for s in output["live_scenarios"])
        output["status"] = "VERIFIED" if passes == 3 else "PARTIAL" if passes else "FAILED"
        with httpx.Client(timeout=5, trust_env=False) as client:
            try:
                output["postflight_ps"] = client.get("http://127.0.0.1:11434/api/ps").json()
            except (httpx.HTTPError, ValueError):
                output["postflight_ps"] = {"status": "UNAVAILABLE"}
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--authorize-paid-calls", action="store_true")
    parser.add_argument(
        "--local-live",
        action="store_true",
        help="Exactly three local Phi4-mini acceptance scenarios, no cloud calls",
    )
    args = parser.parse_args()
    if args.local_live:
        if args.live or args.authorize_paid_calls:
            parser.error("--local-live cannot be mixed with paid-provider flags")
        result = local_acceptance()
        (ROOT / "artifacts/ollama_real_agent_acceptance.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )
        performance = {
            "executed_at_utc": result["executed_at_utc"],
            "provider": result["provider"],
            "model": result["model"],
            "model_digest": result.get("model_digest"),
            "preflight_ps": result["preflight"].get("ps"),
            "postflight_ps": result.get("postflight_ps"),
            "measurements": [
                {"scenario": s["scenario"], **s.get("provider_evidence", {})}
                for s in result["live_scenarios"]
            ],
            "note": "Warm resident model as observed before the run; wall time includes local HTTP, no cold-start benchmark or intrusive peak profiling.",
        }
        (ROOT / "artifacts/ollama_performance.json").write_text(
            json.dumps(performance, indent=2) + "\n", encoding="utf-8"
        )
        print("LOCAL_LLM_STATUS=" + result["status"])
        raise SystemExit(result["status"] != "VERIFIED")
    result = acceptance(live=args.live, authorized=args.authorize_paid_calls)
    (ROOT / "artifacts/real_agent_acceptance.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    offline_passed = sum(s["status"] == "PASS" for s in result["offline_scenarios"])
    print(
        f"REAL_AGENT_STATUS={result['status']} real_requests={result['real_provider_requests_attempted']} offline_scenarios={offline_passed}/3 live_scenarios="
        + ",".join(s["status"] for s in result["live_scenarios"])
    )
    raise SystemExit(
        result["status"] == "FAILED"
        or any(s["status"] != "PASS" for s in result["offline_scenarios"])
    )
