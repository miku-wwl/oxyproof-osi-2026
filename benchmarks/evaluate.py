"""Fixed labeled scientific guard cases, NOT a general LLM/science accuracy claim."""

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.data.ingest import Repository  # noqa: E402
from backend.app.reports.audit import calculate_record, screen  # noqa: E402
from backend.app.schemas import ScreenRequest  # noqa: E402
from backend.app.science.conductivity import wrong_equation_demo  # noqa: E402


def evaluate() -> dict:
    repo = Repository(fixture_only=True)
    cases = [
        ("valid_in_range", ScreenRequest(row_ids=[1]), "CALCULATED_WITH_WARNINGS", None),
        (
            "outside_measured_range",
            ScreenRequest(row_ids=[39]),
            "INSUFFICIENT_EVIDENCE",
            "OUTSIDE_MEASURED_RANGE",
        ),
        (
            "missing_breakpoint",
            ScreenRequest(row_ids=[462]),
            "INSUFFICIENT_EVIDENCE",
            "AMBIGUOUS_REGIME",
        ),
        (
            "unknown_type_and_sentinel",
            ScreenRequest(row_ids=[66], conductivity_type="total"),
            "INSUFFICIENT_EVIDENCE",
            "TYPE_NOT_COMPARABLE",
        ),
        (
            "bulk_is_not_total",
            ScreenRequest(row_ids=[1], conductivity_type="total"),
            "INSUFFICIENT_EVIDENCE",
            "TYPE_NOT_COMPARABLE",
        ),
        (
            "exact_transition",
            ScreenRequest(
                row_ids=[1],
                goal="Screen oxygen-ion conductors",
                temperature=float(repo.by_id[1].raw["T*"]),
                temperature_unit="K",
            ),
            "INSUFFICIENT_EVIDENCE",
            "AT_TRANSITION",
        ),
        (
            "temperature_without_unit",
            ScreenRequest(row_ids=[1], goal="Screen at 600"),
            "INSUFFICIENT_EVIDENCE",
            "PLAN_REJECTED",
        ),
    ]
    rows = []
    for name, request, expected, reason in cases:
        report = screen(request, repo)
        codes = {w.code for w in report.warnings} | {
            w.code for r in report.excluded for w in r.warnings
        }
        # The intentionally non-audited baseline returns a numeric result without checks.
        baseline = "CALCULATED_WITH_WARNINGS"
        raw = repo.by_id[request.row_ids[0]].raw
        # Deliberately unsafe: guess 600 C when units/temperature are absent, always
        # use the low/single fields, omit 1/T, and mislabel the resulting quantity.
        guessed_k = (
            873.15
            if request.temperature is None
            else request.temperature + (273.15 if request.temperature_unit == "C" else 0)
        )
        baseline_number = float(raw["A"]) * math.exp(
            -float(raw["Ea"]) / (1000 * (1.380649e-23 / 1.602176634e-19) * guessed_k)
        )
        rows.append(
            {
                "case": name,
                "expected_status": expected,
                "required_warning": reason,
                "baseline_status": baseline,
                "baseline_numeric_trace": {
                    "value_mislabelled_as_S_cm": baseline_number,
                    "actual_unit": "K S/cm",
                    "assumed_temperature_k": guessed_k,
                    "Ea_mev": float(raw["Ea"]),
                    "A_K_S_cm": float(raw["A"]),
                    "parameter_fields": ["Ea", "A"],
                },
                "audited_status": report.status,
                "audited_warning_codes": sorted(codes),
                "baseline_correct": baseline == expected,
                "audited_correct": report.status == expected
                and (reason is None or reason in codes),
            }
        )
    calculation = calculate_record(repo.by_id[1], 873.15)
    demo = wrong_equation_demo(calculation.computed_values_with_units["conductivity"].value, 873.15)
    rows.append(
        {
            "case": "same_prefactor_wrong_dimensions",
            "expected_status": "REJECTED_WRONG_FORMULA",
            "baseline_status": "ACCEPTED_AS_CONDUCTIVITY",
            "audited_status": demo["status"],
            "baseline_correct": False,
            "audited_correct": demo["status"] == "REJECTED_WRONG_FORMULA",
            "detail": demo,
        }
    )
    return {
        "methodology": "Eight hand-labeled, fixed guard cases using unchanged published records. Naive baseline accepts every case, reuses A without 1/T and ignores units/type/regime/range. Metric checks expected decision plus required warning; not representative scientific accuracy, LLM quality, or experimental validation. No randomized split or statistical interval.",
        "source": repo.source.model_dump(),
        "sample_size": len(rows),
        "baseline_correct_decisions": sum(r["baseline_correct"] for r in rows),
        "audited_correct_decisions": sum(r["audited_correct"] for r in rows),
        "cases": rows,
    }


if __name__ == "__main__":
    result = evaluate()
    (ROOT / "artifacts/benchmark.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"MEASURED guard_cases={result['sample_size']} baseline_correct={result['baseline_correct_decisions']} audited_correct={result['audited_correct_decisions']}"
    )
    if result["audited_correct_decisions"] != result["sample_size"]:
        sys.exit(1)
