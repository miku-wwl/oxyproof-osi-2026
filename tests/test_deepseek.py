"""Synthetic transport/ledger contracts only. No genuine cloud inference in pytest."""

import json
import os
import subprocess
import sys

import httpx
import pytest

from backend.app.agents import deepseek
from backend.app.agents.llm import LLMError, call_tools, configured
from backend.app.agents.workflow import run_research
from backend.app.science.decision_schemas import AgentRequest
from scripts.accept_deepseek_agent import acceptance, check_schema, preflight
from scripts.accept_real_agent import SCENARIOS, independently_check
from tests.test_real_agent_acceptance import interval_plan, screen_plan


@pytest.fixture
def local_config(monkeypatch, tmp_path):
    monkeypatch.setenv("OXYPROOF_LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("OXYPROOF_LLM_MODEL", "deepseek-flash")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "SYNTHETIC_DEEPSEEK_UNIT_ONLY")
    monkeypatch.setattr(deepseek, "LEDGER", tmp_path / "budget.json")


def envelope(tool="screen_published_records", arguments=None):
    return {
        "id": "SYNTHETIC_PROVIDER_RESPONSE",
        "model": "deepseek-flash",
        "status": "completed",
        "output": [
            {
                "type": "function_call",
                "name": tool,
                "arguments": json.dumps(screen_plan() if arguments is None else arguments),
            },
            {"type": "reasoning", "content": "PRIVATE_REASONING_DO_NOT_RETAIN"},
            {"type": "message", "content": "INVENTED_SOURCE_999_S_CM"},
        ],
        "usage": {
            "input_tokens": 105,
            "output_tokens": 67,
            "total_tokens": 172,
            "input_tokens_details": {"cached_tokens": 64},
            "secret": "DO_NOT_RETAIN",
        },
    }


def mock_transport(monkeypatch, body=None, status=200, error=None, raw=None):
    original = httpx.Client
    calls = []

    def handler(request):
        assert str(request.url) == deepseek.ENDPOINT
        calls.append(json.loads(request.content))
        if error:
            raise error("SENSITIVE_PROVIDER_TEXT")
        if raw is not None:
            return httpx.Response(status, content=raw)
        return httpx.Response(status, json=body)

    def client(**kwargs):
        assert kwargs["timeout"].read == 60
        assert kwargs["follow_redirects"] is False and kwargs["trust_env"] is False
        return original(transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(httpx, "Client", client)
    return calls


def test_explicit_deepseek_configuration_no_openai_key(local_config, monkeypatch):
    assert configured()
    monkeypatch.delenv("DEEPSEEK_API_KEY")
    assert not configured()
    monkeypatch.setenv("OPENAI_API_KEY", "SYNTHETIC_OTHER_PROVIDER_KEY")
    assert not configured()
    with pytest.raises(LLMError, match="NOT_CONFIGURED"):
        call_tools(SCENARIOS["A"], [])
    assert not deepseek.LEDGER.exists()


def test_reviewed_basic_schemas_preserve_server_bounds(local_config):
    payload = deepseek.request_payload(SCENARIOS["A"], [])
    assert len(payload["tools"]) == 3 and payload["tool_choice"] == "required"
    assert payload["reasoning"] == {"effort": "none"}
    assert (
        not {"store", "parallel_tool_calls", "max_tool_calls", "previous_response_id"}
        & payload.keys()
    )
    for tool in payload["tools"]:
        assert "strict" not in tool
        check_schema(tool["parameters"])
        assert set(tool["parameters"]["required"]) == set(tool["parameters"]["properties"])
    schema = payload["tools"][0]["parameters"]
    assert schema["properties"]["material_class"] == {
        "anyOf": [{"type": "string"}, {"type": "null"}]
    }
    assert (
        deepseek.TOOL_MODELS["screen_published_records"].model_json_schema()["properties"][
            "material_class"
        ]["anyOf"][0]["maxLength"]
        == 100
    )


@pytest.mark.parametrize("name", ["A", "B", "C"])
def test_real_data_execution_through_synthetic_responses(repo, local_config, monkeypatch, name):
    args = (
        interval_plan()
        if name == "B"
        else screen_plan(
            conductivity_type=None if name == "C" else "bulk",
            unsupported_constraints=["10% humidity", "10,000 operating hours"]
            if name == "C"
            else [],
        )
    )
    tool = "analyze_temperature_interval" if name == "B" else "screen_published_records"
    calls = mock_transport(monkeypatch, envelope(tool, args))
    result = run_research(
        AgentRequest(
            goal=SCENARIOS[name], row_ids=[] if name == "B" else [1, 2, 3], mode="REAL_LLM"
        ),
        repo,
    )
    independently_check(name, result, repo)
    trace = result["execution_trace"]
    assert (
        trace.provider_metadata["provider"] == "DeepSeek"
        and trace.response_id == "SYNTHETIC_PROVIDER_RESPONSE"
    )
    assert trace.provider_metadata["usage"]["cached_input_tokens"] == 64
    assert trace.model_selected_tool == trace.deterministically_expected_tool == tool
    assert trace.executed_scientific_tool == (None if name == "C" else tool)
    assert trace.provider_metadata["executed_scientific_tool"] == trace.executed_scientific_tool
    assert trace.tool_agreement
    assert not any(
        s in trace.model_dump_json()
        for s in ("PRIVATE_REASONING", "INVENTED_SOURCE", "DO_NOT_RETAIN")
    )
    assert len(calls) == len(deepseek.read_ledger()["attempts"]) == 1
    if name == "C":
        assert trace.refusal_origin == "BOTH_MODEL_PLAN_AND_INDEPENDENT_VALIDATOR"


def test_dropped_unsupported_conditions_cannot_recommend(repo, local_config, monkeypatch):
    mock_transport(monkeypatch, envelope(arguments=screen_plan(conductivity_type=None)))
    result = run_research(AgentRequest(goal=SCENARIOS["C"], mode="REAL_LLM"), repo)
    assert (
        not result["result"].candidates
        and result["execution_trace"].executed_scientific_tool is None
    )
    assert result["execution_trace"].refusal_origin == "INDEPENDENT_VALIDATOR"
    assert "10,000 operating hours" in result["execution_trace"].model_dump_json()


@pytest.mark.parametrize(
    "kind",
    [
        "multiple",
        "missing",
        "unknown",
        "malformed_arguments",
        "invalid_unit",
        "missing_temperature",
        "long_class",
        "extra_source",
        "incomplete",
        "missing_id",
        "bad_envelope",
        "web_search",
        "invalid_row",
        "message_json_only",
    ],
)
def test_invalid_model_output_fails_closed(local_config, monkeypatch, kind):
    body = envelope()
    call = body["output"][0]
    args = screen_plan()
    if kind == "multiple":
        body["output"].append(call.copy())
    elif kind == "missing":
        body["output"] = []
    elif kind == "unknown":
        call["name"] = "execute_shell"
    elif kind == "malformed_arguments":
        call["arguments"] = "{broken"
    elif kind in {"invalid_unit", "missing_temperature", "long_class", "extra_source"}:
        if kind == "invalid_unit":
            args["temperature_unit"] = "F"
        if kind == "missing_temperature":
            args.pop("temperature")
        if kind == "long_class":
            args["material_class"] = "X" * 101
        if kind == "extra_source":
            args["source_doi"] = "INVENTED_SOURCE"
        call["arguments"] = json.dumps(args)
    elif kind == "incomplete":
        body["status"] = "incomplete"
    elif kind == "missing_id":
        body.pop("id")
    elif kind == "bad_envelope":
        body = []
    elif kind == "web_search":
        body["output"].append({"type": "web_search_call"})
    elif kind == "invalid_row":
        call.update(
            name="analyze_temperature_interval", arguments=json.dumps(interval_plan(row_ids=[484]))
        )
    else:
        body["output"] = [{"type": "message", "content": json.dumps(call)}]
    calls = mock_transport(monkeypatch, body)
    with pytest.raises(LLMError) as exc:
        call_tools(SCENARIOS["A"], [])
    assert len(calls) == len(deepseek.read_ledger()["attempts"]) == 1
    assert "INVENTED_SOURCE" not in str(exc.value)


@pytest.mark.parametrize("status", [302, 400, 401, 429, 500])
def test_systemic_http_failure_halts_sprint_durably(local_config, monkeypatch, status):
    calls = mock_transport(monkeypatch, {"error": "SENSITIVE_PROVIDER_TEXT"}, status=status)
    with pytest.raises(LLMError, match=f"PROVIDER_HTTP_{status}"):
        call_tools(SCENARIOS["A"], [])
    assert deepseek.read_ledger()["halted"]
    with pytest.raises(LLMError, match="BUDGET_HALTED"):
        call_tools(SCENARIOS["B"], [])
    assert len(calls) == 1


def test_timeout_consumes_one_attempt_and_never_retries(local_config, monkeypatch):
    calls = mock_transport(monkeypatch, error=httpx.ReadTimeout)
    with pytest.raises(LLMError, match="ReadTimeout") as exc:
        call_tools(SCENARIOS["A"], [])
    assert len(calls) == 1 and deepseek.read_ledger()["halted"]
    assert "SENSITIVE_PROVIDER_TEXT" not in str(exc.value)


def test_malformed_wire_json_is_systemic(local_config, monkeypatch):
    calls = mock_transport(monkeypatch, raw=b"not-json")
    with pytest.raises(LLMError, match="JSONDecodeError"):
        call_tools(SCENARIOS["A"], [])
    assert len(calls) == 1 and deepseek.read_ledger()["halted"]


def test_fourth_request_is_blocked_across_new_python_process(local_config):
    command = "from pathlib import Path; from backend.app.agents import deepseek as d; d.LEDGER=Path(__import__('sys').argv[1]); [d.claim_request({'local_invocation_id':str(i),'started_at_utc':'SYNTHETIC_TIME'}) for i in range(3)]"
    subprocess.run(
        [sys.executable, "-c", command, str(deepseek.LEDGER)],
        check=True,
        capture_output=True,
        env={
            k: v for k, v in os.environ.items() if k not in {"DEEPSEEK_API_KEY", "OPENAI_API_KEY"}
        },
        timeout=15,
    )
    with pytest.raises(LLMError, match="BUDGET_EXHAUSTED"):
        deepseek.claim_request(
            {"local_invocation_id": "fourth", "started_at_utc": "SYNTHETIC_TIME"}
        )
    assert len(deepseek.read_ledger()["attempts"]) == 3


def test_corrupt_or_locked_ledger_never_resets_budget(local_config):
    deepseek.LEDGER.write_text("{broken", encoding="utf-8")
    with pytest.raises(LLMError, match="BUDGET_INVALID"):
        deepseek.claim_request({"local_invocation_id": "test", "started_at_utc": "test"})
    assert deepseek.LEDGER.read_text() == "{broken"
    deepseek.LEDGER.with_suffix(".lock").touch()
    with pytest.raises(LLMError, match="BUDGET_LOCKED"):
        deepseek.claim_request({"local_invocation_id": "test", "started_at_utc": "test"})


def test_cloud_disabled_precedes_transport_and_budget(local_config, monkeypatch):
    monkeypatch.setenv("OXYPROOF_DISABLE_CLOUD", "1")
    with pytest.raises(LLMError, match="CLOUD_DISABLED"):
        call_tools(SCENARIOS["A"], [])
    assert not deepseek.LEDGER.exists()


def test_zero_cost_preflight_has_no_network_or_budget_use(repo, local_config):
    report = preflight(repo)
    assert report["status"] == "PASS" and not deepseek.LEDGER.exists()
    for live, authorized in [(False, False), (True, False), (False, True)]:
        result = acceptance(live=live, authorized=authorized)
        assert result["real_provider_requests_attempted"] == 0
    assert not deepseek.LEDGER.exists()


@pytest.mark.parametrize("systemic", [False, True])
def test_acceptance_budget_and_systemic_stop(local_config, monkeypatch, systemic):
    original = httpx.Client
    calls = []

    def handler(request):
        payload = json.loads(request.content)
        calls.append(payload)
        if systemic:
            return httpx.Response(401, json={"error": "SENSITIVE_PROVIDER_TEXT"})
        name = next(n for n, q in SCENARIOS.items() if q == payload["input"])
        return httpx.Response(
            200,
            json=envelope(
                "analyze_temperature_interval" if name == "B" else "screen_published_records",
                interval_plan()
                if name == "B"
                else screen_plan(conductivity_type=None if name == "C" else "bulk"),
            ),
        )

    monkeypatch.setattr(
        httpx, "Client", lambda **kw: original(transport=httpx.MockTransport(handler), **kw)
    )
    result = acceptance(live=True, authorized=True)
    assert len(calls) == result["real_provider_requests_attempted"] == (1 if systemic else 3)
    assert result["status"] == ("FAILED" if systemic else "VERIFIED")
    assert [s["status"] for s in result["live_scenarios"]] == (
        ["FAIL", "NOT_RUN", "NOT_RUN"] if systemic else ["PASS"] * 3
    )
    # A second process/run cannot treat a used ledger as a fresh authorization.
    assert acceptance(live=True, authorized=True)["real_provider_requests_attempted"] == 0


def test_actual_unit_network_transport_is_disabled():
    with pytest.raises(AssertionError, match="REAL_HTTP_FORBIDDEN"):
        httpx.Client(trust_env=False).get("https://example.invalid")
