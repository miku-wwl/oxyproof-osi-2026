"""MOCK_TRANSPORT_CONTRACT_ONLY; no call here is live-model evidence."""

import json

import httpx
import pytest

from backend.app.agents.llm import LLMError
from backend.app.agents.workflow import run_research, run_temperature
from backend.app.science.decision_schemas import AgentRequest, TemperatureRequest

ORIGINAL_CLIENT = httpx.Client


def model_transport(monkeypatch, name, arguments, *, extra_message=False):
    calls = []
    original = ORIGINAL_CLIENT

    def handler(request):
        payload = json.loads(request.content)
        assert payload["parallel_tool_calls"] is False
        assert payload["max_output_tokens"] == 2000
        assert all(
            t["strict"]
            and t["parameters"]["additionalProperties"] is False
            and set(t["parameters"]["required"]) == set(t["parameters"]["properties"])
            for t in payload["tools"]
        )
        calls.append(payload)
        output = [{"type": "function_call", "name": name, "arguments": json.dumps(arguments)}]
        if extra_message:
            output.append(
                {"type": "message", "content": "INVENTED_CITATION_AND_999_S_CM_DO_NOT_DISPLAY"}
            )
        return httpx.Response(
            200, json={"status": "completed", "id": "SYNTHETIC_CONTRACT_RESPONSE", "output": output}
        )

    monkeypatch.setattr(
        httpx, "Client", lambda **kwargs: original(transport=httpx.MockTransport(handler), **kwargs)
    )
    monkeypatch.setenv("OPENAI_API_KEY", "SYNTHETIC_TEST_ONLY")
    monkeypatch.setenv("OXYPROOF_LLM_MODEL", "SYNTHETIC_TEST_ONLY_MODEL")
    return calls


@pytest.mark.parametrize(
    "tool,goal,arguments",
    [
        (
            "screen_published_records",
            "Find bulk conductors at 600 C",
            {
                "temperature": 600,
                "temperature_unit": "C",
                "conductivity_type": "bulk",
                "material_class": None,
                "formula_query": None,
                "unsupported_constraints": [],
            },
        ),
        (
            "analyze_temperature_interval",
            "Compare bulk conductors between 600 K and 1100 K",
            {
                "temperature_min": 600,
                "temperature_max": 1100,
                "temperature_unit": "K",
                "conductivity_type": "bulk",
                "unsupported_constraints": [],
            },
        ),
        (
            "inspect_scientific_evidence",
            "Inspect scientific evidence row 1",
            {"row_id": 1, "unsupported_constraints": []},
        ),
    ],
)
def test_real_mode_tool_selection_contract_only(repo, monkeypatch, tool, goal, arguments):
    calls = model_transport(monkeypatch, tool, arguments, extra_message=True)
    report = run_research(AgentRequest(goal=goal, row_ids=[1, 2, 3], mode="REAL_LLM"), repo)
    assert len(calls) == 1 and calls[0]["tool_choice"] == "required"
    assert {t["name"] for t in calls[0]["tools"]} == {
        "screen_published_records",
        "analyze_temperature_interval",
        "inspect_scientific_evidence",
    }
    assert report["tool_name"] == tool
    assert report["response_id"] == "SYNTHETIC_CONTRACT_RESPONSE"
    result = report["result"]
    serialized = result.model_dump_json() if hasattr(result, "model_dump_json") else str(result)
    assert "INVENTED_CITATION_AND_999" not in serialized


def test_interval_model_cannot_drop_humidity(repo, monkeypatch):
    calls = model_transport(
        monkeypatch,
        "analyze_temperature_interval",
        {
            "temperature_min": 600,
            "temperature_max": 1100,
            "temperature_unit": "K",
            "conductivity_type": "bulk",
            "unsupported_constraints": [],
        },
    )
    report = run_temperature(
        TemperatureRequest(
            goal="Compare bulk conductors between 600 K and 1100 K that survive 10% humidity",
            row_ids=[1, 2, 3],
            mode="REAL_LLM",
        ),
        repo,
    )
    assert len(calls) == 1
    assert report.status == "INSUFFICIENT_EVIDENCE"
    assert report.evidence_verdicts == ["UNVERIFIED_CONSTRAINTS"]
    assert not report.curve_points


def test_model_cannot_change_tool_or_bounds(repo, monkeypatch):
    model_transport(
        monkeypatch, "inspect_scientific_evidence", {"row_id": 1, "unsupported_constraints": []}
    )
    with pytest.raises(LLMError, match="MODEL_TOOL_CONFLICT"):
        run_research(AgentRequest(goal="Find bulk conductors at 600 C", mode="REAL_LLM"), repo)
    model_transport(
        monkeypatch,
        "analyze_temperature_interval",
        {
            "temperature_min": 600,
            "temperature_max": 1200,
            "temperature_unit": "K",
            "conductivity_type": "bulk",
            "unsupported_constraints": [],
        },
    )
    with pytest.raises(LLMError, match="MODEL_PLAN_CONFLICT"):
        run_temperature(
            TemperatureRequest(
                goal="Compare bulk conductors between 600 K and 1100 K",
                row_ids=[1, 2, 3],
                mode="REAL_LLM",
            ),
            repo,
        )


def test_nonphysical_goals_return_typed_api_error(client):
    result = client.post("/api/screen", json={"goal": "Find bulk conductors at -300 C"}).json()
    assert result["evidence_verdict"] == "INVALID_TEMPERATURE"
    response = client.post(
        "/api/research",
        json={"goal": "Compare bulk conductors between -300 C and 1100 K", "row_ids": [1, 2, 3]},
    )
    assert (
        response.status_code == 422 and response.json()["detail"]["code"] == "INVALID_TEMPERATURE"
    )


def test_expanded_benchmark_is_reproducible():
    from benchmarks.evaluate_v2 import evaluate

    result = evaluate()
    assert result["sample_size"] >= 30 and result["failed"] == 0
    assert result["real_model_calls"] == 0
