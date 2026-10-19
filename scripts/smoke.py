"""Genuine HTTP smoke test against a running localhost API; no remote endpoints."""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8000"


def http(path: str, body: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(
        BASE + path, data=data, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=35) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as exc:
        return exc.code, json.load(exc)


def main() -> None:
    results = []
    status, health = http("/api/health")
    assert status == 200 and health["source"]["row_count"] in (24, 483)
    results.append(
        {
            "check": "health",
            "http_status": status,
            "source_scope": health["source"]["scope"],
            "row_count": health["source"]["row_count"],
        }
    )
    status, report = http("/api/screen", {"row_ids": [1, 2, 3]})
    assert status == 200 and [c["row_id"] for c in report["candidates"]] == [3, 2, 1]
    assert (
        abs(
            report["candidates"][-1]["computed_values_with_units"]["conductivity"]["value"]
            - 0.013243811986442925
        )
        < 1e-14
    )
    results.append(
        {
            "check": "real_screen",
            "http_status": status,
            "candidate_rows": [3, 2, 1],
            "status": report["status"],
        }
    )
    status, wrong = http("/api/records/1/adversarial?temperature_c=600")
    assert status == 200 and wrong["demo"]["status"] == "REJECTED_WRONG_FORMULA"
    results.append(
        {"check": "wrong_formula", "http_status": status, "status": wrong["demo"]["status"]}
    )
    status, rejected = http("/api/screen", {"row_ids": [462]})
    assert status == 200 and rejected["status"] == "INSUFFICIENT_EVIDENCE"
    assert "AMBIGUOUS_REGIME" in {w["code"] for w in rejected["excluded"][0]["warnings"]}
    results.append(
        {"check": "ambiguous_regime", "http_status": status, "status": rejected["status"]}
    )
    status, outside = http("/api/screen", {"row_ids": [39]})
    assert status == 200 and not outside["candidates"]
    results.append({"check": "outside_range", "http_status": status, "status": outside["status"]})
    status, _ = http("/api/screen", {"temperature_unit": "F"})
    assert status == 422
    results.append({"check": "invalid_unit", "http_status": status})
    output = {
        "status": "PASS",
        "transport": "real localhost HTTP",
        "base_url": BASE,
        "checks": results,
    }
    (ROOT / "artifacts/http_smoke.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8"
    )
    print(f"HTTP_SMOKE=PASS checks={len(results)} scope={health['source']['scope']}")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, ValueError) as exc:
        print(f"HTTP_SMOKE=FAIL {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
