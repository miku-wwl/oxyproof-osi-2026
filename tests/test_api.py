import pytest


def test_health_and_real_catalog(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["real_llm_status"] == "NOT_CONFIGURED"
    assert client.get("/api/catalog").json()["source"]["row_count"] == 24


def test_screen_contract(client):
    response = client.post("/api/screen", json={"row_ids": [1, 2, 3]})
    assert response.status_code == 200
    result = response.json()
    for key in [
        "status",
        "research_request",
        "source",
        "dataset_record_id",
        "equation",
        "inputs_with_units",
        "computed_values_with_units",
        "observations_vs_calculations",
        "warnings",
        "trace",
        "review_required",
    ]:
        assert key in result
    assert result["candidates"][0]["row_id"] == 3
    assert result["source"]["dataset_doi"] == "10.5281/zenodo.18947543"


@pytest.mark.parametrize(
    "body",
    [
        {"temperature_unit": "F"},
        {"top_n": 0},
        {"row_ids": [-1]},
        {"row_ids": [1, 1]},
        {"row_ids": [999]},
        {"mode": "FAKE_LLM"},
        {"url": "file:///etc/passwd"},
        {"code": "rm -rf"},
        {"goal": "x" * 2001},
    ],
)
def test_invalid_request_contract(client, body):
    assert client.post("/api/screen", json=body).status_code == 422


@pytest.mark.parametrize("nonfinite", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite_json_has_safe_typed_error(client, nonfinite):
    response = client.post(
        "/api/screen",
        content='{"temperature":' + nonfinite + "}",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "finite_number"


def test_real_llm_no_silent_fallback(client):
    response = client.post("/api/screen", json={"mode": "REAL_LLM"})
    assert response.status_code == 503
    assert response.json()["detail"]["runtime_mode"] == "UNAVAILABLE"
    assert "NOT_CONFIGURED" in response.text


def test_real_record_detail(client):
    response = client.get("/api/records/1")
    assert response.json()["record"]["raw"]["Ea"] == "772"
    assert client.get("/api/records/999").status_code == 404


def test_curve_gaps_and_units(client):
    response = client.get("/api/records/1/curve?min_c=0&max_c=1000&points=21")
    assert response.status_code == 200
    points = response.json()["points"]
    assert points[0]["conductivity_s_cm"] is None
    assert any(p["conductivity_s_cm"] is not None for p in points)
    assert client.get("/api/records/462/curve").json()["points"][0]["conductivity_s_cm"] is None
    assert client.get("/api/records/1/curve?min_c=700&max_c=300").status_code == 422
    assert client.get("/api/records/1/curve?points=10000").status_code == 422


def test_adversarial_endpoint(client):
    response = client.get("/api/records/1/adversarial?temperature_c=600")
    assert response.json()["demo"]["status"] == "REJECTED_WRONG_FORMULA"
    assert response.json()["demo"]["wrong_quantity"]["unit"] == "K S/cm"
    assert client.get("/api/records/39/adversarial?temperature_c=600").status_code == 422


def test_unknown_api_route_is_not_spa_html(client):
    assert client.get("/api/nonexistent").status_code == 404


def test_unavailable_data_returns_explicit_503(client, monkeypatch):
    import backend.app.main as module
    from backend.app.data.ingest import DataError

    def unavailable():
        raise DataError("CHECKSUM_MISMATCH")

    monkeypatch.setattr(module, "repository", unavailable)
    response = client.post("/api/screen", json={"row_ids": [1, 2, 3]})
    assert response.status_code == 503
    assert response.json()["detail"]["runtime_mode"] == "UNAVAILABLE"
    assert response.json()["detail"]["code"] == "DATA_UNAVAILABLE"


def test_provider_failure_never_becomes_offline_success(client, monkeypatch):
    from tests.test_llm_adapter import install_transport

    install_transport(monkeypatch, {"secret": "DO_NOT_ECHO"}, status=401)
    response = client.post("/api/screen", json={"mode": "REAL_LLM"})
    assert response.status_code == 503
    assert response.json()["detail"]["runtime_mode"] == "UNAVAILABLE"
    assert "PROVIDER_HTTP_401" in response.text and "DO_NOT_ECHO" not in response.text
