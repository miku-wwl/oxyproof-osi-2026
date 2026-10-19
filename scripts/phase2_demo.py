"""Reproducible scientific reports plus independent endpoint references."""

import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.data.ingest import Repository  # noqa: E402
from backend.app.reports.audit import code_version, screen  # noqa: E402
from backend.app.schemas import ScreenRequest  # noqa: E402
from backend.app.science.decision_schemas import TemperatureRequest  # noqa: E402
from backend.app.science.temperature_decisions import analyze_temperature_interval  # noqa: E402
from benchmarks.reference_v2 import root_decimal, sigma_decimal  # noqa: E402


def write(name, obj):
    value = obj.model_dump() if hasattr(obj, "model_dump") else obj
    (ROOT / "artifacts" / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    repository = Repository()
    decision = analyze_temperature_interval(
        TemperatureRequest(
            goal="Compare bulk conductors between 600 K and 1100 K with source provenance",
            row_ids=[1, 2, 3],
            selected_temperatures=[700, 1000],
        ),
        repository,
    )
    assert [p.ordering for p in decision.selected_rankings] == [[1, 2, 3], [3, 2, 1]]
    write("temperature_decision_flagship.json", decision)
    refusal = screen(
        ScreenRequest(
            goal="Find bulk conductors at 600 C that survive 10% humidity", row_ids=[1, 2, 3]
        ),
        repository,
    )
    assert refusal.evidence_verdict == "UNVERIFIED_CONSTRAINTS" and not refusal.candidates
    write("humidity_refusal_v2.json", refusal)
    reference = {
        "method": "60-digit Decimal/SI independent reference; regime fields explicitly chosen for endpoint checks",
        "source": repository.source.model_dump(),
        "endpoint_values": [
            {
                "row_id": i,
                "formula": repository.by_id[i].formula,
                "temperature_k": t,
                "regime": "LT" if suffix == "" else "HT",
                "sigma_s_cm_decimal": sigma_decimal(repository.by_id[i].raw, t, suffix),
            }
            for t, suffix in [(700, ""), (1000, "HT")]
            for i in [1, 2, 3]
        ],
        "roots": [
            {
                "row_ids": [a, b],
                "regimes": [sa or "LT", sb or "LT"],
                "temperature_k_decimal": root_decimal(
                    repository.by_id[a].raw, repository.by_id[b].raw, sa, sb
                ),
            }
            for a, b, sa, sb in [(1, 2, "", ""), (1, 3, "HT", ""), (2, 3, "HT", "")]
        ],
    }
    reference.update(
        code_version=code_version(),
        equation="sigma(T) = A/T * exp(-Ea/(k_B*T))",
        units={
            "temperature": "K",
            "activation_energy": "meV",
            "prefactor": "K S/cm",
            "conductivity": "S/cm",
        },
        source_records=[repository.by_id[i].model_dump() for i in [1, 2, 3]],
        reference_source_sha256=hashlib.sha256(
            (ROOT / "benchmarks/reference_v2.py").read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest(),
    )
    write("rank_reversal_reference_v2.json", reference)
    configured = bool(os.environ.get("OPENAI_API_KEY") and os.environ.get("OXYPROOF_LLM_MODEL"))
    write(
        "real_llm_status_v2.json",
        {
            "status": "CONFIGURED_NOT_VERIFIED" if configured else "NOT_CONFIGURED",
            "provider_calls_executed_by_this_script": 0,
            "note": "Mock transport tests are contract evidence only. No credentials or paid resources requested.",
        },
    )
    print(
        f"PHASE2_OFFLINE_DEMO=PASS scope={repository.source.scope} rows={repository.source.row_count} selected_orders=1>2>3;3>2>1 continuous_model_crossings=3"
    )
