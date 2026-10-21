"""Three-scene acceptance: offline by default; real calls require BOTH explicit flags.

Live execution makes exactly one bounded provider request per scenario, no retries,
at most three requests. Never run --live --authorize-paid-calls without owner approval.
"""

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fastapi.encoders import jsonable_encoder  # noqa: E402

from backend.app.agents.llm import LLMError, configured  # noqa: E402
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
    runnable_live = live and authorized and configured()
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--authorize-paid-calls", action="store_true")
    args = parser.parse_args()
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
