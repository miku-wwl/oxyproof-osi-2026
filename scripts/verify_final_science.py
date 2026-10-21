"""Independent final numeric acceptance on the pinned published CSV; no model calls."""

import csv
import hashlib
import json
import math
import sys
from datetime import UTC, datetime
from decimal import Decimal, localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.data.ingest import DATASET_SHA256, FULL_PATH, Repository  # noqa: E402
from backend.app.science.decision_schemas import TemperatureRequest  # noqa: E402
from backend.app.science.temperature_decisions import analyze_temperature_interval  # noqa: E402


def reference_sigma(raw, t, suffix, precision=80):
    # SI joules; separate implementation, no production constants or regime selector.
    with localcontext() as ctx:
        ctx.prec = precision
        t = Decimal(str(t))
        energy = Decimal(raw["Ea" + suffix]) * Decimal("0.001") * Decimal("1.602176634e-19")
        return Decimal(raw["A" + suffix]) / t * (-energy / (Decimal("1.380649e-23") * t)).exp()


def reference_root(a, b, sa, sb, precision):
    with localcontext() as ctx:
        ctx.prec = precision
        energy = (Decimal(a["Ea" + sa]) - Decimal(b["Ea" + sb])) * Decimal("1.602176634e-22")
        return energy / (
            Decimal("1.380649e-23") * (Decimal(a["A" + sa]) / Decimal(b["A" + sb])).ln()
        )


def verify():
    content = FULL_PATH.read_bytes()
    assert hashlib.sha256(content).hexdigest() == DATASET_SHA256
    rows = list(csv.DictReader(content.decode("utf-8-sig").splitlines()))
    assert len(rows) == 483 and len(rows[0]) == 34
    source = {i: rows[i - 1] for i in (1, 2, 3)}
    report = analyze_temperature_interval(
        TemperatureRequest(row_ids=[1, 2, 3], selected_temperatures=[700, 1000]), Repository()
    )
    roots = []
    for i, j, si, sj in [(1, 2, "", ""), (1, 3, "HT", ""), (2, 3, "HT", "")]:
        a, b = source[i], source[j]
        root = reference_root(a, b, si, sj, 80)
        stable = abs(root - reference_root(a, b, si, sj, 40)) < Decimal("1e-30")
        # Bounds are independently constructed from dataset fields, not production intervals.
        ranges = [
            (float(r["T*"]) if s else 600, 1100 if s else float(r["T*"]))
            for r, s in [(a, si), (b, sj)]
        ]
        low, high = max(r[0] for r in ranges), min(r[1] for r in ranges)
        assert low < float(root) < high and stable
        event = next(
            e for e in report.events if e.exact_continuous_crossing and e.row_ids == [i, j]
        )
        assert math.isclose(event.temperature_k, float(root), rel_tol=2e-13)
        relative_error = abs(reference_sigma(a, root, si) / reference_sigma(b, root, sj) - 1)
        assert relative_error < Decimal("1e-25")
        side_orders = []
        for offset in [-1, 1]:
            t = root + Decimal(offset)
            values = {
                k: reference_sigma(r, t, "HT" if t > Decimal(r["T*"]) else "")
                for k, r in source.items()
            }
            side_orders.append(sorted(values, key=values.get, reverse=True))
        assert side_orders[0].index(i) < side_orders[0].index(j)
        assert side_orders[1].index(j) < side_orders[1].index(i)
        roots.append(
            {
                "row_ids": [i, j],
                "regimes": [si or "LT", sj or "LT"],
                "root_k_decimal_80_digits": str(root),
                "production_root_k": event.temperature_k,
                "common_fixed_regime_interval_k": [low, high],
                "order_at_root_minus_1_k": side_orders[0],
                "order_at_root_plus_1_k": side_orders[1],
                "relative_sigma_difference_at_root": str(relative_error),
                "precision_40_vs_80_stable": stable,
            }
        )
    endpoints = []
    for point, suffix in zip(report.selected_rankings, ["", "HT"], strict=True):
        for value in point.values:
            expected = reference_sigma(source[value.row_id], point.temperature_k, suffix)
            assert math.isclose(float(expected), value.conductivity_s_cm, rel_tol=2e-14)
            endpoints.append(
                {
                    "row_id": value.row_id,
                    "temperature_k": point.temperature_k,
                    "regime": suffix or "LT",
                    "sigma_s_cm_decimal": str(expected),
                }
            )
    result = {
        "status": "PASS",
        "executed_at_utc": datetime.now(UTC).isoformat(),
        "method": "Independent 80-digit Decimal SI arithmetic; exact CSV strings; 40/80 digit stability; no production calculator/constants/regime selector in reference functions",
        "dataset_sha256": DATASET_SHA256,
        "row_count": len(rows),
        "column_count": len(rows[0]),
        "source_doi": source[1]["DOI"],
        "source_records": source,
        "parameter_evidence_class": "VERIFIED_FROM_CURATED_DATASET",
        "original_full_text_conditions": "NOT_VERIFIED",
        "equation": "sigma=A/T*exp(-Ea_J/(k_B_SI*T)); root=(Ea_i_J-Ea_j_J)/(k_B_SI*ln(A_i/A_j))",
        "units": {
            "Ea_csv": "meV",
            "Ea_reference": "J per carrier",
            "A": "K S/cm",
            "T": "K",
            "sigma": "S/cm",
        },
        "roots": roots,
        "endpoints": endpoints,
        "code_version": report.code_version,
        "qualification": report.crossover_qualification,
        "interpretation": "Conditional model comparison, not experimental superiority; no uncertainty bounds or measured crossings.",
    }
    (ROOT / "artifacts/scientific_acceptance.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print("FINAL_SCIENCE=PASS roots=3 endpoint_values=6 precision=80 independent_side_checks=6")


if __name__ == "__main__":
    verify()
