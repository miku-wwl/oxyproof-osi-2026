"""Independent 60-digit Decimal/SI reference; does not import production science code."""

import csv
import hashlib
import json
from decimal import Decimal, localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = [(1, "700", "LT"), (1, "873.15", "HT"), (39, "1100", "SINGLE"), (483, "600", "SINGLE")]


def references() -> list[dict]:
    fixture = ROOT / "backend/app/data/fixtures"
    manifest = json.loads((fixture / "manifest.json").read_text(encoding="utf-8"))
    content = (fixture / "published_subset.csv").read_bytes()
    if hashlib.sha256(content).hexdigest() != manifest["fixture_sha256"]:
        raise ValueError("CHECKSUM_MISMATCH")
    rows = list(csv.DictReader(content.decode("utf-8").splitlines()))
    by_id = dict(zip(manifest["source_row_ids"], rows, strict=True))
    results = []
    with localcontext() as ctx:
        ctx.prec = 60
        # Work in SI joules per carrier, independently of production eV arithmetic.
        kb = Decimal("1.380649e-23")
        electronvolt_j = Decimal("1.602176634e-19")
        for row_id, temperature, regime in CASES:
            row = by_id[row_id]
            suffix = "HT" if regime == "HT" else ""
            a, ea, t = Decimal(row["A" + suffix]), Decimal(row["Ea" + suffix]), Decimal(temperature)
            ea_j = ea * Decimal("0.001") * electronvolt_j
            exponent = -ea_j / (kb * t)
            sigma = a / t * exponent.exp()
            results.append(
                {
                    "source_row_id": row_id,
                    "source_doi": row["DOI"],
                    "formula": row["Formula"],
                    "regime": regime,
                    "temperature_k": temperature,
                    "activation_energy_mev": str(ea),
                    "prefactor_K_S_cm": str(a),
                    "exponent_decimal": str(exponent),
                    "sigma_s_cm_decimal": str(sigma),
                    "wrong_quantity_K_S_cm_decimal": str(sigma * t),
                }
            )
    return results


if __name__ == "__main__":
    data = references()
    output = ROOT / "artifacts/reference_values.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "method": "60-digit Decimal, SI energy per carrier, exact SI k_B and e",
                "cases": data,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    for case in data:
        print(
            f"row={case['source_row_id']} T={case['temperature_k']} K regime={case['regime']} sigma={case['sigma_s_cm_decimal']} S/cm"
        )
