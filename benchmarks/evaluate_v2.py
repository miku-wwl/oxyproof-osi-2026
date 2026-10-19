"""Evaluate frozen references; records successes AND failures, never live-model evidence."""

import hashlib
import json
import math
import sys
from pathlib import Path

from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.app.data.ingest import Repository  # noqa: E402
from backend.app.reports.audit import calculate_record, code_version, screen  # noqa: E402
from backend.app.schemas import GoalPlan, ScreenRequest  # noqa: E402
from backend.app.science.conductivity import conductivity_at_temperature  # noqa: E402
from backend.app.science.decision_schemas import TemperatureRequest  # noqa: E402
from backend.app.science.temperature_decisions import analyze_temperature_interval  # noqa: E402
from benchmarks.reference_v2 import synthetic_pair  # noqa: E402


def check(case, repo):
    kind, args, expected = case["kind"], case["input"], case["expected"]
    if kind == "numeric":
        result = calculate_record(repo.by_id[args["row_id"]], args["temperature_k"])
        actual = result.computed_values_with_units["conductivity"].value
        return math.isclose(actual, float(expected["sigma_s_cm"]), rel_tol=2e-14), {
            "sigma_s_cm": actual,
            "regime": result.regime,
        }
    if kind == "screen":
        report = screen(ScreenRequest(**args), repo)
        codes = {w.code for w in report.warnings} | {
            w.code for r in report.excluded + report.candidates for w in r.warnings
        }
        order = [c.row_id for c in report.candidates]
        passed = (
            report.status == expected["status"]
            and (not expected.get("warning") or expected["warning"] in codes)
            and (not expected.get("ordering") or order == expected["ordering"])
        )
        return passed, {"status": report.status, "warning_codes": sorted(codes), "ordering": order}
    if kind in ("interval", "root", "range_gaps"):
        report = analyze_temperature_interval(
            TemperatureRequest(**{k: v for k, v in args.items() if k != "pair"}), repo
        )
        if kind == "root":
            events = [
                e
                for e in report.events
                if e.exact_continuous_crossing and e.row_ids == args["pair"]
            ]
            actual = [e.temperature_k for e in events]
            return len(actual) == 1 and math.isclose(
                actual[0], float(expected["temperature_k"]), rel_tol=2e-13
            ), {"roots_k": actual}
        if kind == "range_gaps":
            low, high = expected["measured_bounds"]
            outside = [
                p for p in report.curve_points if p.temperature_k < low or p.temperature_k > high
            ]
            return bool(outside) and all(not p.values and not p.ordering for p in outside), {
                "outside_points": len(outside),
                "outside_ranked": sum(bool(p.ordering) for p in outside),
            }
        actual = {
            "verdicts": report.evidence_verdicts,
            "orders": [p.ordering for p in report.selected_rankings],
            "continuous_count": sum(e.exact_continuous_crossing for e in report.events),
            "transition_count": sum(not e.exact_continuous_crossing for e in report.events),
        }
        passed = (
            expected.get("verdict") in report.evidence_verdicts
            if expected.get("verdict")
            else all(actual[k] == v for k, v in expected.items())
        )
        return passed, actual
    if kind == "unit":
        raw = repo.by_id[1].raw
        a, ea = float(raw["A"]), float(raw["Ea"])
        unit = args["unit"]
        energy, energy_unit = ea, "meV"
        if unit == "eV":
            energy, energy_unit = ea / 1000, "eV"
        if unit in ["J/mol", "kJ/mol"]:
            energy, energy_unit = (
                ea / 1000 * 1.602176634e-19 * 6.02214076e23 / (1000 if unit == "kJ/mol" else 1),
                unit,
            )
        actual = conductivity_at_temperature(
            a * 100 if unit == "K S/m" else a,
            energy,
            700,
            energy_unit=energy_unit,
            prefactor_unit="K S/m" if unit == "K S/m" else "K S/cm",
        )
        return math.isclose(actual, float(expected["sigma_s_cm"]), rel_tol=2e-14), {
            "sigma_s_cm": actual
        }
    if kind == "synthetic":
        report = analyze_temperature_interval(
            TemperatureRequest(row_ids=[1, 2]), synthetic_pair(repo, args["scenario"])
        )
        roots = [e.temperature_k for e in report.events if e.exact_continuous_crossing]
        if args["scenario"] == "continuous":
            passed = len(roots) == 1 and math.isclose(roots[0], 800, abs_tol=1e-10)
        elif args["scenario"] == "discontinuity":
            passed = not roots and any(
                e.kind == "REGIME_BOUNDARY_DRIVEN_CHANGE" for e in report.events
            )
        else:
            passed = not roots and any(
                math.isclose(e.candidate_temperature_k, 1400, abs_tol=1e-9)
                for e in report.rejected_crossovers
            )
        return passed, {
            "continuous_roots": roots,
            "event_kinds": [e.kind for e in report.events],
            "label": "SYNTHETIC_TEST_ONLY",
        }
    if kind == "metamorphic":
        a = analyze_temperature_interval(TemperatureRequest(**args, points=2), repo)
        b = analyze_temperature_interval(TemperatureRequest(**args, points=201), repo)
        return a.events == b.events and a.segments == b.segments, {
            "event_count": len(a.events),
            "segment_count": len(a.segments),
        }
    if kind == "model_contract":
        value = {
            "temperature": 600,
            "temperature_unit": "C",
            "conductivity_type": "bulk",
            "material_class": None,
            "formula_query": None,
            "unsupported_constraints": [],
        }
        if args.get("extra"):
            value[args["extra"]] = "SYNTHETIC_TEST_ONLY"
        else:
            value.update(args)
        try:
            GoalPlan.model_validate(value)
        except ValidationError:
            return True, {"rejected": True, "provider_call": False}
        return False, {"rejected": False, "provider_call": False}
    raise ValueError("UNKNOWN_BENCHMARK_CASE_KIND")


def evaluate():
    repository = Repository(fixture_only=True)
    corpus = json.loads((ROOT / "benchmarks/scientific_cases.json").read_text(encoding="utf-8"))
    results = []
    for case in corpus["cases"]:
        try:
            passed, actual = check(case, repository)
        except Exception as exc:
            passed, actual = False, {"error": type(exc).__name__, "message": str(exc)}
        results.append(case | {"passed": passed, "actual": actual})
    return {
        "corpus_sha256": hashlib.sha256(
            (ROOT / "benchmarks/scientific_cases.json").read_bytes()
        ).hexdigest(),
        "reference_source_sha256": hashlib.sha256(
            (ROOT / "benchmarks/reference_v2.py").read_bytes()
        ).hexdigest(),
        "evaluator_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "methodology": "Frozen hand-selected scientific decision guards; independent Decimal/SI numeric expectations and manually justified refusal labels. Synthetic cases explicitly marked. No held-out population, significance claim or live LLM evaluation. Old 8-case unsafe-baseline demonstration remains separate.",
        "source": repository.source.model_dump(),
        "code_version": code_version(),
        "runtime_mode": "OFFLINE_DETERMINISTIC",
        "real_model_calls": 0,
        "sample_size": len(results),
        "passed": sum(r["passed"] for r in results),
        "failed": sum(not r["passed"] for r in results),
        "cases": results,
    }


if __name__ == "__main__":
    result = evaluate()
    (ROOT / "artifacts/scientific_benchmark_v2.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"SCIENTIFIC_BENCHMARK_V2 cases={result['sample_size']} passed={result['passed']} failed={result['failed']} live_model_calls=0"
    )
    for r in result["cases"]:
        if not r["passed"]:
            print("FAILED", r["id"], r["actual"])
    raise SystemExit(bool(result["failed"]))
