"""Read-only replay of the fixed genuine acceptance artifact. Never invokes a planner."""

import json
from pathlib import Path

from backend.app.schemas import AuditReport
from backend.app.science.decision_schemas import AgentExecution, TemperatureReport

CAPTURE = Path(__file__).resolve().parents[3] / "artifacts/deepseek_live_acceptance.json"


def recorded_deepseek():
    if CAPTURE.stat().st_size > 2_000_000:
        raise ValueError("Recorded evidence exceeds the replay size bound")
    captured = json.loads(CAPTURE.read_text(encoding="utf-8"))
    if not (
        captured.get("status") == "VERIFIED"
        and captured.get("provider") == "DeepSeek"
        and captured.get("real_provider_requests_attempted") == 3
        and captured.get("real_provider_requests_succeeded") == 3
    ):
        raise ValueError("All three genuine acceptance scenarios must be verified")
    scenes = captured["live_scenarios"]
    if [s["scenario"] for s in scenes] != ["A", "B", "C"]:
        raise ValueError("Recorded scenario set is incomplete")
    runs = []
    identities = set()
    for scene in scenes:
        execution = AgentExecution.model_validate(scene["execution"])
        trace = execution.execution_trace
        result = execution.result
        if not (
            scene["status"] == "PASS"
            and execution.runtime_mode == "REAL_LLM"
            and trace.provider_metadata.get("provider") == "DeepSeek"
            and trace.response_id
            and trace.response_id not in identities
            and trace.tool_selection == "MODEL_SELECTED"
            and trace.tool_agreement is True
            and trace.tool_name
            == trace.model_selected_tool
            == trace.deterministically_expected_tool
            and isinstance(result, (AuditReport, TemperatureReport))
            and result.execution_trace == trace
            and result.validated_arguments
            == trace.validated_arguments
            == execution.validated_arguments
        ):
            raise ValueError("Recorded trace consistency check failed")
        identities.add(trace.response_id)
        runs.append({"scenario": scene["scenario"], "execution": execution})
    return {
        "presentation_mode": "RECORDED_TRACE_REPLAY",
        "fresh_model_request": False,
        "recorded_at_utc": captured["executed_at_utc"],
        "source_file": "artifacts/deepseek_live_acceptance.json",
        "runs": runs,
    }
