"""Archived genuine evidence revalidation and replay failure contracts; ZERO inference."""

import json

import pytest

from backend.app.agents import recorded
from backend.app.science.decision_schemas import AgentExecution
from scripts.accept_real_agent import independently_check


@pytest.fixture
def capture():
    return json.loads(recorded.CAPTURE.read_text(encoding="utf-8"))


def test_captured_real_science_still_passes_independent_checks(repo):
    archive = recorded.recorded_deepseek()
    assert archive["presentation_mode"] == "RECORDED_TRACE_REPLAY"
    assert archive["fresh_model_request"] is False
    for run in archive["runs"]:
        execution = run["execution"]
        independently_check(
            run["scenario"],
            {name: getattr(execution, name) for name in AgentExecution.model_fields},
            repo,
        )
        trace = execution.execution_trace
        assert trace.provider_metadata["executed_scientific_tool"] == trace.executed_scientific_tool


@pytest.mark.parametrize(
    "kind",
    [
        "partial",
        "missing_scenario",
        "duplicate_identity",
        "wrong_provider",
        "wrong_runtime",
        "inconsistent_arguments",
    ],
)
def test_replay_rejects_invalid_capture(capture, tmp_path, monkeypatch, kind):
    if kind == "partial":
        capture["status"] = "PARTIAL"
    elif kind == "missing_scenario":
        capture["live_scenarios"].pop()
    elif kind == "duplicate_identity":
        trace = capture["live_scenarios"][1]["execution"]["execution_trace"]
        trace["response_id"] = capture["live_scenarios"][0]["execution"]["execution_trace"][
            "response_id"
        ]
    elif kind == "wrong_provider":
        capture["provider"] = "Synthetic"
    elif kind == "wrong_runtime":
        capture["live_scenarios"][0]["execution"]["runtime_mode"] = "OFFLINE_DETERMINISTIC"
    else:
        capture["live_scenarios"][0]["execution"]["validated_arguments"] = {}
    path = tmp_path / "mutated.json"
    path.write_text(json.dumps(capture), encoding="utf-8")
    monkeypatch.setattr(recorded, "CAPTURE", path)
    with pytest.raises(ValueError):
        recorded.recorded_deepseek()


def test_replay_endpoint_is_read_only_and_explicit(client):
    response = client.get("/api/research/recorded-deepseek")
    assert response.status_code == 200
    assert response.json()["fresh_model_request"] is False
    assert len(response.json()["runs"]) == 3


def test_missing_replay_is_a_typed_404(client, monkeypatch, tmp_path):
    monkeypatch.setattr(recorded, "CAPTURE", tmp_path / "absent.json")
    response = client.get("/api/research/recorded-deepseek")
    assert response.status_code == 404
    assert "RECORDED_DEEPSEEK_EVIDENCE_UNAVAILABLE" in response.text
