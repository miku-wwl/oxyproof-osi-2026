"""MOCK_TRANSPORT_CONTRACT_TEST_ONLY. These do not verify a live model."""

import json

import httpx
import pytest

from backend.app.agents.llm import LLMError, plan_with_llm
from backend.app.schemas import ScreenRequest


def install_transport(monkeypatch, body=None, status=200):
    original_client = httpx.Client

    def handler(request):
        payload = json.loads(request.content)
        assert payload["tools"][0]["name"] == "screen_published_records"
        assert payload["parallel_tool_calls"] is False
        assert payload["store"] is False
        assert "772" not in request.content.decode()  # No raw parameter payload.
        return httpx.Response(status, json=body)

    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kwargs: original_client(transport=httpx.MockTransport(handler), **kwargs),
    )
    monkeypatch.setenv("OPENAI_API_KEY", "SYNTHETIC_TEST_ONLY")
    monkeypatch.setenv("OXYPROOF_LLM_MODEL", "SYNTHETIC_TEST_ONLY_MODEL")


def valid_body():
    return {
        "status": "completed",
        "id": "SYNTHETIC_TEST_ONLY_RESPONSE",
        "output": [
            {
                "type": "function_call",
                "name": "screen_published_records",
                "arguments": json.dumps(
                    {
                        "temperature": 600,
                        "temperature_unit": "C",
                        "conductivity_type": "bulk",
                        "material_class": None,
                        "formula_query": None,
                        "unsupported_constraints": [],
                    }
                ),
            }
        ],
    }


def test_allowlisted_plan_contract_only(monkeypatch):
    install_transport(monkeypatch, valid_body())
    plan, model, response_id = plan_with_llm(ScreenRequest(), [])
    assert plan.temperature == 600
    assert model == "SYNTHETIC_TEST_ONLY_MODEL"
    assert response_id == "SYNTHETIC_TEST_ONLY_RESPONSE"


@pytest.mark.parametrize(
    "variant",
    [
        "shell",
        "extra_field",
        "bad_json",
        "incomplete",
        "two_calls",
        "missing_id",
        "array_envelope",
        "null_output",
        "bad_output_item",
    ],
)
def test_malformed_or_unsafe_model_plan_rejected(monkeypatch, variant):
    body = valid_body()
    if variant == "shell":
        body["output"][0]["name"] = "execute_shell"
    if variant == "extra_field":
        body["output"][0]["arguments"] = body["output"][0]["arguments"][:-1] + ', "code": "evil"}'
    if variant == "bad_json":
        body["output"][0]["arguments"] = "not json"
    if variant == "incomplete":
        body["status"] = "incomplete"
    if variant == "two_calls":
        body["output"] *= 2
    if variant == "missing_id":
        del body["id"]
    if variant == "array_envelope":
        body = []
    if variant == "null_output":
        body["output"] = None
    if variant == "bad_output_item":
        body["output"] = ["not an object"]
    install_transport(monkeypatch, body)
    with pytest.raises(LLMError):
        plan_with_llm(ScreenRequest(), [])


def test_provider_failure_body_not_leaked(monkeypatch):
    install_transport(monkeypatch, {"secret": "DO_NOT_ECHO"}, status=401)
    with pytest.raises(LLMError, match="PROVIDER_HTTP_401") as exc:
        plan_with_llm(ScreenRequest(), [])
    assert "DO_NOT_ECHO" not in str(exc.value)


def test_no_credentials_does_not_call_provider(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(LLMError, match="NOT_CONFIGURED"):
        plan_with_llm(ScreenRequest(), [])
