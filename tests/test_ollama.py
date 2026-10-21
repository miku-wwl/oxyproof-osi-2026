"""MOCK TRANSPORT ONLY. These contracts never count as real model acceptance."""

import json
from uuid import UUID

import httpx
import pytest

from backend.app.agents.llm import LLMError, call_tools, configured, provider
from backend.app.agents.workflow import run_research
from backend.app.science.decision_schemas import AgentExecution, AgentRequest
from scripts.accept_real_agent import SCENARIOS, independently_check
from tests.test_real_agent_acceptance import interval_plan, screen_plan


def envelope(name="screen_published_records", arguments=None):
    return {
        "model": "phi4-mini:latest",
        "done": True,
        "done_reason": "stop",
        "message": {
            "role": "assistant",
            "content": "INVENTED_PROSE_999_S_CM",
            "tool_calls": [
                {
                    "function": {
                        "name": name,
                        "arguments": arguments if arguments is not None else screen_plan(),
                    }
                }
            ],
        },
        "prompt_eval_count": 111,
        "eval_count": 33,
        "eval_duration": 9000000,
    }


def transport(monkeypatch, body=None, *, status=200, error=None):
    original = httpx.Client
    requests = []

    def handler(request):
        requests.append(request)
        assert str(request.url) == "http://127.0.0.1:11434/api/chat"
        if error:
            raise error("SENSITIVE_PROVIDER_TEXT")
        return httpx.Response(status, json=body)

    def client(**kwargs):
        assert kwargs["trust_env"] is False and kwargs["follow_redirects"] is False
        assert kwargs["timeout"].read == 180
        return original(transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(httpx, "Client", client)
    monkeypatch.setenv("OXYPROOF_LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OXYPROOF_LLM_MODEL", "phi4-mini:latest")
    return requests


def test_explicit_provider_and_backward_configuration(monkeypatch):
    assert provider() == "openai" and not configured()
    monkeypatch.setenv("OXYPROOF_LLM_MODEL", "SYNTHETIC")
    monkeypatch.setenv("OPENAI_API_KEY", "SYNTHETIC_TEST_ONLY")
    assert configured()
    monkeypatch.setenv("OXYPROOF_LLM_PROVIDER", "ollama")
    monkeypatch.delenv("OPENAI_API_KEY")
    assert configured()
    monkeypatch.setenv("OXYPROOF_LLM_PROVIDER", "unknown")
    assert not configured()
    with pytest.raises(LLMError, match="UNSUPPORTED_PROVIDER"):
        call_tools("Find conductors at 600 C", [])


@pytest.mark.parametrize(
    "endpoint",
    [
        "https://127.0.0.1:11434",
        "http://example.com",
        "http://localhost:11434",
        "http://127.0.0.1:11434/api",
        "http://user@127.0.0.1:11434",
        "http://127.0.0.1:11434?x=1",
        "http://127.0.0.1:80",
        "http://127.0.0.1:bad",
    ],
)
def test_local_endpoint_fails_before_network(monkeypatch, endpoint):
    requests = transport(monkeypatch, envelope())
    monkeypatch.setenv("OXYPROOF_OLLAMA_BASE_URL", endpoint)
    assert not configured()
    with pytest.raises(LLMError, match="INVALID_LOCAL_ENDPOINT"):
        call_tools(SCENARIOS["A"], [])
    assert requests == []


@pytest.mark.parametrize("name", ["A", "B", "C"])
def test_native_tool_workflow_without_provider_id(repo, monkeypatch, name):
    args = (
        interval_plan()
        if name == "B"
        else screen_plan(conductivity_type=None if name == "C" else "bulk")
    )
    tool = "analyze_temperature_interval" if name == "B" else "screen_published_records"
    requests = transport(monkeypatch, envelope(tool, args))
    execution = run_research(
        AgentRequest(
            goal=SCENARIOS[name], row_ids=[] if name == "B" else [1, 2, 3], mode="REAL_LLM"
        ),
        repo,
    )
    independently_check(name, execution, repo)
    AgentExecution.model_validate(execution)
    trace = execution["execution_trace"]
    assert trace.response_id is None and UUID(trace.local_invocation_id)
    assert trace.provider_metadata["provider"] == "Ollama Local"
    assert trace.model_selected_tool == trace.deterministically_expected_tool == tool
    assert trace.tool_agreement and trace.executed_scientific_tool == tool
    assert "INVENTED_PROSE" not in trace.model_dump_json()
    assert len(requests) == 1
    payload = json.loads(requests[0].content)
    assert payload["keep_alive"] == -1 and not payload["stream"]
    assert payload["options"] == {"temperature": 0, "num_predict": 512, "num_ctx": 4096}
    assert len(payload["tools"]) == 3
    if name == "C":
        assert trace.refusal_origin == "INDEPENDENT_VALIDATOR"


def test_native_string_arguments_are_normalized(monkeypatch):
    transport(monkeypatch, envelope(arguments=json.dumps(screen_plan())))
    _, plan, model, identity = call_tools(SCENARIOS["A"], [])
    assert plan.temperature == 600 and model == "phi4-mini:latest" and identity is None


@pytest.mark.parametrize("interval", [False, True])
def test_fixed_endpoints_do_not_claim_model_discovered_tool(repo, monkeypatch, interval):
    from backend.app.agents.workflow import run_temperature
    from backend.app.reports.audit import screen
    from backend.app.schemas import ScreenRequest
    from backend.app.science.decision_schemas import TemperatureRequest

    transport(
        monkeypatch,
        envelope(
            "analyze_temperature_interval" if interval else "screen_published_records",
            interval_plan() if interval else screen_plan(),
        ),
    )
    result = (
        run_temperature(
            TemperatureRequest(
                goal=SCENARIOS["B"],
                row_ids=[1, 2, 3],
                temperature_min=700,
                temperature_max=1000,
                mode="REAL_LLM",
            ),
            repo,
        )
        if interval
        else screen(ScreenRequest(goal=SCENARIOS["A"], row_ids=[1, 2, 3], mode="REAL_LLM"), repo)
    )
    assert result.execution_trace.tool_selection == "FIXED_ENDPOINT"
    assert result.execution_trace.model_selected_tool is None
    assert result.execution_trace.response_id is None
    assert result.execution_trace.local_invocation_id


@pytest.mark.parametrize(
    "kind",
    [
        "missing",
        "multiple",
        "unknown",
        "invalid_unit",
        "invalid_rows",
        "extra_source",
        "missing_field",
        "malformed_arguments",
        "json_prose_only",
        "incomplete",
        "model_mismatch",
        "invalid_envelope",
    ],
)
def test_native_failure_contracts(monkeypatch, kind):
    body = envelope()
    function = body["message"]["tool_calls"][0]["function"]
    if kind == "missing":
        body["message"].pop("tool_calls")
    elif kind == "multiple":
        body["message"]["tool_calls"] *= 2
    elif kind == "unknown":
        function["name"] = "execute_shell"
    elif kind == "invalid_unit":
        function["arguments"]["temperature_unit"] = "F"
    elif kind == "invalid_rows":
        function.update(name="analyze_temperature_interval", arguments=interval_plan(row_ids=[484]))
    elif kind == "extra_source":
        function["arguments"]["source_doi"] = "INVENTED_SOURCE"
    elif kind == "missing_field":
        function["arguments"].pop("temperature")
    elif kind == "malformed_arguments":
        function["arguments"] = "{broken"
    elif kind == "json_prose_only":
        body["message"] = {"content": json.dumps(function)}
    elif kind == "incomplete":
        body["done_reason"] = "length"
    elif kind == "model_mismatch":
        body["model"] = "other_model"
    else:
        body = []
    requests = transport(monkeypatch, body)
    with pytest.raises(LLMError) as exc:
        call_tools(SCENARIOS["A"], [])
    assert len(requests) == 1 and "INVENTED_SOURCE" not in str(exc.value)
    assert exc.value.telemetry["execution_status"] == "FAILED"


@pytest.mark.parametrize("status", [302, 400, 500])
def test_provider_http_failure_without_fallback(monkeypatch, status):
    requests = transport(monkeypatch, {"error": "SENSITIVE_PROVIDER_TEXT"}, status=status)
    with pytest.raises(LLMError, match=f"OLLAMA_HTTP_{status}"):
        call_tools(SCENARIOS["A"], [])
    assert len(requests) == 1


def test_timeout_is_single_attempt_with_evidence(monkeypatch):
    requests = transport(monkeypatch, error=httpx.ReadTimeout)
    with pytest.raises(LLMError, match="ReadTimeout") as exc:
        call_tools(SCENARIOS["A"], [])
    assert len(requests) == 1 and "SENSITIVE_PROVIDER_TEXT" not in str(exc.value)
    assert exc.value.telemetry["wall_seconds"] >= 0


def test_wrong_tool_is_recorded_and_never_executed(repo, monkeypatch):
    transport(
        monkeypatch,
        envelope("inspect_scientific_evidence", {"row_id": 1, "unsupported_constraints": []}),
    )
    meta = {}
    with pytest.raises(LLMError, match="MODEL_TOOL_CONFLICT"):
        run_research(
            AgentRequest(goal=SCENARIOS["A"], mode="REAL_LLM"), repo, provider_metadata=meta
        )
    assert meta["model_selected_tool"] == "inspect_scientific_evidence"
    assert meta["deterministically_expected_tool"] == "screen_published_records"
    assert meta["tool_agreement"] is False and meta["executed_scientific_tool"] is None


def test_both_model_and_independent_refusal(repo, monkeypatch):
    transport(
        monkeypatch,
        envelope(
            arguments=screen_plan(
                conductivity_type=None,
                unsupported_constraints=["10% humidity", "10,000 operating hours"],
            )
        ),
    )
    result = run_research(AgentRequest(goal=SCENARIOS["C"], mode="REAL_LLM"), repo)
    assert result["execution_trace"].refusal_origin == "BOTH_MODEL_PLAN_AND_INDEPENDENT_VALIDATOR"
    assert not result["result"].candidates


def test_normal_acceptance_never_activates_ollama(repo, monkeypatch):
    from scripts.accept_real_agent import acceptance

    monkeypatch.setenv("OXYPROOF_LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OXYPROOF_LLM_MODEL", "phi4-mini:latest")

    def forbidden(*a, **kw):
        raise AssertionError("Unrequested inference")

    monkeypatch.setattr(httpx, "Client", forbidden)
    assert (
        run_research(AgentRequest(goal=SCENARIOS["A"], row_ids=[1, 2, 3]), repo)["runtime_mode"]
        == "OFFLINE_DETERMINISTIC"
    )
    for live, authorized in [(False, False), (True, True)]:
        assert acceptance(live=live, authorized=authorized)["real_provider_requests_attempted"] == 0


def test_malformed_wire_json_is_a_bounded_failure(monkeypatch):
    original = httpx.Client
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, content=b"not-json")

    monkeypatch.setattr(
        httpx, "Client", lambda **kwargs: original(transport=httpx.MockTransport(handler), **kwargs)
    )
    monkeypatch.setenv("OXYPROOF_LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OXYPROOF_LLM_MODEL", "phi4-mini:latest")
    with pytest.raises(LLMError, match="JSONDecodeError"):
        call_tools(SCENARIOS["A"], [])
    assert len(requests) == 1


@pytest.mark.parametrize("systemic_failure", [False, True])
def test_local_runner_budget_and_systemic_stop(monkeypatch, systemic_failure):
    from scripts.accept_real_agent import local_acceptance

    original = httpx.Client
    calls = []

    def handler(request):
        if request.method == "GET":
            if request.url.path == "/api/tags":
                return httpx.Response(
                    200,
                    json={
                        "models": [
                            {
                                "name": "phi4-mini:latest",
                                "digest": "SYNTHETIC_DIGEST",
                                "capabilities": ["tools"],
                            }
                        ]
                    },
                )
            return httpx.Response(200, json={"version": "SYNTHETIC_TEST", "models": []})
        calls.append(request)
        body = json.loads(request.content)
        question = body["messages"][-1]["content"]
        if systemic_failure:
            return httpx.Response(
                200,
                json={
                    "model": "phi4-mini:latest",
                    "done": True,
                    "message": {"content": "ordinary text"},
                },
            )
        b, c = question == SCENARIOS["B"], question == SCENARIOS["C"]
        return httpx.Response(
            200,
            json=envelope(
                "analyze_temperature_interval" if b else "screen_published_records",
                interval_plan() if b else screen_plan(conductivity_type=None if c else "bulk"),
            ),
        )

    monkeypatch.setattr(
        httpx, "Client", lambda **kwargs: original(transport=httpx.MockTransport(handler), **kwargs)
    )
    report = local_acceptance()
    assert (
        len(calls) == report["real_provider_requests_attempted"] == (1 if systemic_failure else 3)
    )
    assert report["status"] == ("FAILED" if systemic_failure else "VERIFIED")
    assert [s["status"] for s in report["live_scenarios"]] == (
        ["FAIL", "NOT_RUN", "NOT_RUN"] if systemic_failure else ["PASS"] * 3
    )
    assert provider() == "openai"
