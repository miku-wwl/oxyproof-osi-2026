import math

import pytest

from backend.app.reports.audit import calculate_record
from backend.app.science.conductivity import (
    KB_EV_K,
    R_J_MOL_K,
    ScienceError,
    conductivity_at_temperature,
    measurement_range,
    select_regime,
    to_kelvin,
    wrong_equation_demo,
)
from scripts.reference_values import references


@pytest.mark.parametrize(
    "case", references(), ids=lambda c: f"row{c['source_row_id']}-{c['regime']}"
)
def test_independent_decimal_real_values(case):
    result = conductivity_at_temperature(
        float(case["prefactor_K_S_cm"]),
        float(case["activation_energy_mev"]),
        float(case["temperature_k"]),
    )
    assert result == pytest.approx(float(case["sigma_s_cm_decimal"]), rel=2e-14)


def test_hand_derived_log_two():
    # SYNTHETIC_TEST_ONLY: choose Ea=k_B*T*ln(2) and A=2*T, so sigma=1 S/cm.
    t = 1000
    ea_ev = KB_EV_K * t * math.log(2)
    assert conductivity_at_temperature(2000, ea_ev, t, energy_unit="eV") == pytest.approx(1)
    assert conductivity_at_temperature(
        2000, R_J_MOL_K * t * math.log(2), t, energy_unit="J/mol"
    ) == pytest.approx(1)


@pytest.mark.parametrize(
    "unit,energy",
    [("meV", 1000), ("eV", 1), ("J/mol", 96485.33212331002), ("kJ/mol", 96.48533212331002)],
)
def test_energy_unit_equivalence(unit, energy):
    expected = conductivity_at_temperature(1e5, 1000, 873.15)
    assert conductivity_at_temperature(
        1e5, energy, 600, temperature_unit="C", energy_unit=unit
    ) == pytest.approx(expected, rel=2e-13)


def test_conductivity_length_unit_conversion():
    assert conductivity_at_temperature(1e7, 700, 900, prefactor_unit="K S/m") == pytest.approx(
        conductivity_at_temperature(1e5, 700, 900)
    )


@pytest.mark.parametrize(
    "value,unit",
    [
        (0, "K"),
        (-1, "K"),
        (-273.15, "C"),
        (math.nan, "K"),
        (math.inf, "C"),
        (600, "F"),
        (10001, "K"),
    ],
)
def test_bad_temperatures(value, unit):
    with pytest.raises(ScienceError):
        to_kelvin(value, unit)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"prefactor": 0},
        {"prefactor": -1},
        {"prefactor": math.inf},
        {"activation_energy": -1},
        {"activation_energy": math.nan},
        {"energy_unit": "joule"},
        {"prefactor_unit": "S/cm"},
        {"activation_energy": 1e308},
        {"prefactor": 1e308, "activation_energy": 0, "temperature": 0.001},
    ],
)
def test_invalid_parameters_or_unrepresentable_result(kwargs):
    parameters = {"prefactor": 1e5, "activation_energy": 700, "temperature": 900} | kwargs
    with pytest.raises(ScienceError):
        conductivity_at_temperature(**parameters)


@pytest.mark.parametrize(
    "range_text", ["600 - 900", "900 - 600 K", "0 - 900 K", "600 C", "nan - inf K"]
)
def test_ambiguous_ranges(range_text):
    with pytest.raises(ScienceError):
        measurement_range(range_text)


def test_regime_selection_and_exact_boundary(repo):
    raw = repo.by_id[1].raw
    assert select_regime(raw, 700)[0] == "LT"
    assert select_regime(raw, 873.15)[0] == "HT"
    with pytest.raises(ScienceError, match="exact T"):
        select_regime(raw, float(raw["T*"]))


@pytest.mark.parametrize("row_id", [66, 68, 72, 462, 463, 464])
def test_real_ambiguous_regimes_abstain(repo, row_id):
    result = calculate_record(repo.by_id[row_id], 873.15)
    assert result.status == "INSUFFICIENT_EVIDENCE"
    assert "AMBIGUOUS_REGIME" in {w.code for w in result.warnings}
    assert not result.computed_values_with_units


def test_extrapolation_opt_in_never_ranks(repo):
    record = repo.by_id[39]
    assert calculate_record(record, 873.15).status == "INSUFFICIENT_EVIDENCE"
    result = calculate_record(record, 873.15, True)
    assert result.status == "EXTRAPOLATED" and result.rank is None


def test_transition_outside_range_preserves_warning(repo):
    result = calculate_record(repo.by_id[280], 1000)
    assert result.status == "CALCULATED"
    assert "TRANSITION_OUTSIDE_REPORTED_RANGE" in {w.code for w in result.warnings}


def test_wrong_formula_dimensional_failure(repo):
    result = calculate_record(repo.by_id[1], 873.15)
    sigma = result.computed_values_with_units["conductivity"].value
    wrong = wrong_equation_demo(sigma, 873.15)
    assert wrong["status"] == "REJECTED_WRONG_FORMULA"
    assert wrong["wrong_quantity"]["unit"] == "K S/cm"
    assert wrong["wrong_quantity"]["value"] / sigma == pytest.approx(873.15)
    assert wrong["numeric_ratio"]["unit"] == "K"
