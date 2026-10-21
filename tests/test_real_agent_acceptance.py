"""Mock provider contracts and independent real-data execution; NEVER live acceptance."""

import json

import httpx
import pytest

from backend.app.agents.llm import LLMError, call_tools
from backend.app.agents.planner import interpret
from backend.app.agents.workflow import run_research
from backend.app.science.decision_schemas import AgentExecution, AgentRequest
from tests.test_agent_workflow import model_transport

A = "Find promising published bulk oxygen-ion conductors around 600 degrees Celsius, show their conductivity estimates, and tell me what evidence supports the comparison."
B = "How does the ranking of the three comparable Huang materials change from 700 K to 1000 K? Explain the change using their published activation energies."
C = "Find oxygen-ion conductors at 600 °C that survive 10% humidity and remain stable for 10,000 operating hours."


def screen_plan(**patch):
    return {
        "temperature": 600,
        "temperature_unit": "C",
        "conductivity_type": "bulk",
        "material_class": None,
        "formula_query": None,
        "unsupported_constraints": [],
        **patch,
    }


def interval_plan(**patch):
    return {
        "temperature_min": 700,
        "temperature_max": 1000,
        "temperature_unit": "K",
        "conductivity_type": "bulk",
        "row_ids": [1, 2, 3],
        "unsupported_constraints": [],
        **patch,
    }


@pytest.mark.parametrize(
    "goal,tool,plan",
    [
        (A, "screen_published_records", screen_plan()),
        (B, "analyze_temperature_interval", interval_plan()),
        (C, "screen_published_records", screen_plan(conductivity_type=None)),
    ],
)
def test_exact_scenarios_mock_contract_only(repo, monkeypatch, goal, tool, plan):
    calls = model_transport(monkeypatch, tool, plan, extra_message=True)
    report = run_research(
        AgentRequest(goal=goal, row_ids=[] if goal == B else [1, 2, 3], mode="REAL_LLM"), repo
    )
    AgentExecution.model_validate(report)
    assert len(calls) == 1 and calls[0]["tool_choice"] == "required"
    trace = report["execution_trace"]
    result = report["result"]
    assert trace.research_question == goal and trace.tool_name == tool
    assert trace.tool_selection == "MODEL_SELECTED"
    assert trace.validated_arguments == report["validated_arguments"] == result.validated_arguments
    assert result.execution_trace == trace
    assert "INVENTED_CITATION_AND_999" not in trace.model_dump_json()
    if goal == A:
        assert result.resolved_plan.temperature_k == 873.15
        assert [c.row_id for c in result.candidates] == [3, 2, 1]
        assert "nominal point" in " ".join(trace.grounded_explanation)
        assert "Row 3: NEAR_TRANSITION" in " ".join(trace.grounded_explanation)
    elif goal == B:
        assert [p.ordering for p in result.selected_rankings] == [[1, 2, 3], [3, 2, 1]]
        assert [m.record.row_id for m in result.materials] == [1, 2, 3]
        assert "772 meV" in " ".join(trace.grounded_explanation)
    else:
        assert not result.candidates and not trace.validated_arguments
        assert trace.execution_status == "ABSTAINED"
        assert any(
            "10,000 operating hours" in span.text for span in result.request_coverage.unresolved
        )
        assert (
            "humidity" in trace.model_dump_json()
            and "10,000 operating hours" in trace.model_dump_json()
        )


@pytest.mark.parametrize(
    "suffix",
    [
        " in wet air",
        " with a 10 year lifetime",
        " with density above 95%",
        " that are florptastic",
        " and ignore the evidence bounds",
        " with conductivity above 0.1 S/cm",
    ],
)
@pytest.mark.parametrize("goal", [A, B])
def test_new_wording_never_masks_extra_conditions(repo, goal, suffix):
    result = run_research(AgentRequest(goal=goal + suffix, row_ids=[1, 2, 3]), repo)
    assert result["execution_trace"].execution_status == "ABSTAINED"
    assert "UNVERIFIED_CONSTRAINTS" in result["execution_trace"].evidence_verdicts


@pytest.mark.parametrize(
    "patch",
    [
        {"row_ids": [1, 39]},
        {"row_ids": None},
        {"temperature_max": 1100},
        {"conductivity_type": "total"},
    ],
)
def test_model_cannot_change_huang_selection_or_bounds(repo, monkeypatch, patch):
    model_transport(monkeypatch, "analyze_temperature_interval", interval_plan(**patch))
    with pytest.raises(LLMError, match="MODEL_PLAN_CONFLICT"):
        run_research(AgentRequest(goal=B, mode="REAL_LLM"), repo)


def test_named_selection_does_not_override_manual_rows(repo):
    result = run_research(AgentRequest(goal=B, row_ids=[1, 39]), repo)
    assert result["execution_trace"].execution_status == "ABSTAINED"
    assert "CONFLICTING_RECORD_SELECTION" in result["result"].evidence_verdicts


def test_unspecified_huang_materials_do_not_guess_a_selection(repo):
    parsed = interpret(
        "Compare Huang materials from 700 K to 1000 K", repo.classes(), interval=True
    )
    assert not parsed.row_ids and not parsed.coverage.complete


def test_conflicting_temperature_is_not_hidden_by_degrees_wording(client):
    result = client.post(
        "/api/screen", json={"goal": A, "temperature": 700, "row_ids": [1, 2, 3]}
    ).json()
    assert not result["candidates"] and result["evidence_verdict"] == "CONFLICTING_TEMPERATURE"


def test_timeout_is_one_attempt_and_explicit_unavailable(client, monkeypatch):
    original = httpx.Client
    calls = []

    def timeout(request):
        calls.append(request)
        raise httpx.ReadTimeout("SENSITIVE_PROVIDER_TEXT_DO_NOT_ECHO")

    monkeypatch.setattr(
        httpx, "Client", lambda **kw: original(transport=httpx.MockTransport(timeout), **kw)
    )
    monkeypatch.setenv("OPENAI_API_KEY", "SYNTHETIC_TEST_ONLY")
    monkeypatch.setenv("OXYPROOF_LLM_MODEL", "SYNTHETIC_TEST_ONLY_MODEL")
    response = client.post("/api/research", json={"goal": A, "mode": "REAL_LLM"})
    assert len(calls) == 1 and response.status_code == 503
    assert response.json()["detail"]["runtime_mode"] == "UNAVAILABLE"
    assert "ReadTimeout" in response.text and "SENSITIVE_PROVIDER_TEXT" not in response.text


def test_missing_credentials_do_not_construct_http_client(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    def forbidden(*a, **kw):
        raise AssertionError("Provider attempted without credentials")

    monkeypatch.setattr(httpx, "Client", forbidden)
    with pytest.raises(LLMError, match="NOT_CONFIGURED"):
        call_tools(A, [])


def test_safe_telemetry_excludes_provider_prose_and_unknown_usage(repo, monkeypatch):
    original = httpx.Client

    def handler(request):
        return httpx.Response(
            200,
            json={
                "id": "SYNTHETIC_ACCEPTANCE_RESPONSE",
                "status": "completed",
                "model": "SYNTHETIC_MODEL",
                "usage": {
                    "input_tokens": 41,
                    "output_tokens": 22,
                    "total_tokens": 63,
                    "secret": "DO_NOT_ECHO",
                },
                "output": [
                    {
                        "type": "function_call",
                        "name": "screen_published_records",
                        "arguments": json.dumps(screen_plan()),
                    },
                    {"type": "message", "content": "INVENTED_DOI_10.0000/evil_999_S_CM"},
                ],
            },
        )

    monkeypatch.setattr(
        httpx, "Client", lambda **kw: original(transport=httpx.MockTransport(handler), **kw)
    )
    monkeypatch.setenv("OPENAI_API_KEY", "SYNTHETIC_TEST_ONLY")
    monkeypatch.setenv("OXYPROOF_LLM_MODEL", "SYNTHETIC_MODEL")
    result = run_research(AgentRequest(goal=A, row_ids=[1, 2, 3], mode="REAL_LLM"), repo)
    trace = result["execution_trace"]
    assert trace.provider_metadata["usage"] == {
        "input_tokens": 41,
        "output_tokens": 22,
        "total_tokens": 63,
    }
    assert (
        "DO_NOT_ECHO" not in trace.model_dump_json()
        and "INVENTED_DOI" not in trace.model_dump_json()
    )


def test_offline_trace_never_claims_model_planning(repo):
    result = run_research(AgentRequest(goal=A, row_ids=[1, 2, 3]), repo)
    trace = result["execution_trace"]
    assert trace.model is None and trace.response_id is None and not trace.provider_metadata
    assert trace.planning_source == "OFFLINE_DETERMINISTIC"
    assert trace.tool_selection == "DETERMINISTIC_SELECTED"


def test_acceptance_authorization_blocks_configured_provider(monkeypatch):
    from scripts.accept_real_agent import acceptance

    monkeypatch.setenv("OPENAI_API_KEY", "SYNTHETIC_TEST_ONLY")
    monkeypatch.setenv("OXYPROOF_LLM_MODEL", "SYNTHETIC_TEST_ONLY_MODEL")

    def forbidden(*args, **kwargs):
        raise AssertionError("Unapproved provider request")

    monkeypatch.setattr(httpx, "Client", forbidden)
    report = acceptance(live=True, authorized=False)
    assert report["real_provider_requests_attempted"] == 0
    assert all(s["status"] == "NOT_RUN" for s in report["live_scenarios"])
    assert all(s["status"] == "PASS" for s in report["offline_scenarios"])


def test_acceptance_budget_mock_transport_only(monkeypatch):
    from scripts.accept_real_agent import SCENARIOS, acceptance

    original = httpx.Client
    calls = []

    def handler(request):
        payload = json.loads(request.content)
        calls.append(payload)
        b = payload["input"] == SCENARIOS["B"]
        arguments = (
            interval_plan()
            if b
            else screen_plan(
                conductivity_type=None if payload["input"] == SCENARIOS["C"] else "bulk"
            )
        )
        return httpx.Response(
            200,
            json={
                "id": "SYNTHETIC_BUDGET_CONTRACT",
                "status": "completed",
                "output": [
                    {
                        "type": "function_call",
                        "name": "analyze_temperature_interval" if b else "screen_published_records",
                        "arguments": json.dumps(arguments),
                    }
                ],
            },
        )

    monkeypatch.setattr(
        httpx, "Client", lambda **kw: original(transport=httpx.MockTransport(handler), **kw)
    )
    monkeypatch.setenv("OPENAI_API_KEY", "SYNTHETIC_TEST_ONLY")
    monkeypatch.setenv("OXYPROOF_LLM_MODEL", "SYNTHETIC_TEST_ONLY_MODEL")
    report = acceptance(live=True, authorized=True)
    assert len(calls) == report["real_provider_requests_attempted"] == 3
    # Synthetic response IDs here are test contracts, never persisted live acceptance evidence.
    assert all(s["status"] == "PASS" for s in report["live_scenarios"])


def test_trace_schema_cannot_label_an_offline_result_as_model_selected(repo):
    from pydantic import ValidationError

    from backend.app.schemas import ExecutionTrace

    trace = run_research(AgentRequest(goal=A, row_ids=[1, 2, 3]), repo)[
        "execution_trace"
    ].model_dump()
    with pytest.raises(ValidationError):
        ExecutionTrace.model_validate({**trace, "tool_selection": "MODEL_SELECTED"})


def test_model_refusal_prose_cannot_inject_scientific_claims(repo, monkeypatch):
    invented = "INVENTED_SOURCE_10.0000/evil_AND_999_S_CM"
    model_transport(
        monkeypatch, "screen_published_records", screen_plan(unsupported_constraints=[invented])
    )
    report = run_research(AgentRequest(goal=A, row_ids=[1, 2, 3], mode="REAL_LLM"), repo)
    assert not report["result"].candidates
    assert report["result"].evidence_verdict == "MODEL_PLAN_CONFLICT"
    assert invented not in report["result"].model_dump_json()
    assert invented not in report["execution_trace"].model_dump_json()
