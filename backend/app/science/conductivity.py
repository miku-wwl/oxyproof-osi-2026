"""Dataset-specific sigma*T convention; explicit energy and temperature units."""

import math
import re
import sys
from typing import Literal

KB_EV_K = 1.380649e-23 / 1.602176634e-19
R_J_MOL_K = 1.380649e-23 * 6.02214076e23
EQUATION = "sigma(T) = A/T * exp(-Ea/(k_B*T))"


class ScienceError(ValueError):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


def to_kelvin(value: float, unit: Literal["C", "K"]) -> float:
    if unit not in ("C", "K"):
        raise ScienceError("UNSUPPORTED_TEMPERATURE_UNIT", "Only explicit C or K is accepted")
    temperature = value + 273.15 if unit == "C" else value
    if not math.isfinite(temperature) or temperature <= 0 or temperature > 10000:
        raise ScienceError("INVALID_TEMPERATURE", "Temperature must be finite and 0 < T <= 10000 K")
    return temperature


def conductivity_at_temperature(
    prefactor: float,
    activation_energy: float,
    temperature: float,
    *,
    temperature_unit: Literal["C", "K"] = "K",
    energy_unit: Literal["meV", "eV", "J/mol", "kJ/mol"] = "meV",
    prefactor_unit: Literal["K S/cm", "K S/m"] = "K S/cm",
) -> float:
    t = to_kelvin(temperature, temperature_unit)
    if not math.isfinite(prefactor) or prefactor <= 0:
        raise ScienceError("INVALID_PREFACTOR", "A must be finite and positive")
    if not math.isfinite(activation_energy) or activation_energy < 0:
        raise ScienceError("INVALID_ENERGY", "Ea must be finite and nonnegative")
    if prefactor_unit not in ("K S/cm", "K S/m"):
        raise ScienceError(
            "UNSUPPORTED_PREFACTOR_UNIT", "A needs temperature times conductivity units"
        )
    if energy_unit == "meV":
        exponent = -(activation_energy / 1000) / (KB_EV_K * t)
    elif energy_unit == "eV":
        exponent = -activation_energy / (KB_EV_K * t)
    elif energy_unit in ("J/mol", "kJ/mol"):
        factor = 1000 if energy_unit == "kJ/mol" else 1
        exponent = -(activation_energy * factor) / (R_J_MOL_K * t)
    else:
        raise ScienceError(
            "UNSUPPORTED_ENERGY_UNIT", "Explicit supported energy units are required"
        )
    # Work in log space, including unit scaling, rather than underflowing exp first.
    log_sigma = math.log(prefactor) - math.log(t) + exponent
    if prefactor_unit == "K S/m":
        log_sigma -= math.log(100)
    if not math.isfinite(log_sigma) or not (
        math.log(sys.float_info.min) <= log_sigma <= math.log(sys.float_info.max)
    ):
        raise ScienceError(
            "NUMERIC_RANGE", "Result outside normal finite float range; no silent zero"
        )
    return math.exp(log_sigma)


def numeric(raw: dict[str, str], key: str, *, strictly_positive: bool = False) -> float:
    try:
        value = float(raw[key])
    except (KeyError, ValueError, TypeError) as exc:
        raise ScienceError("MISSING_PARAMETER", f"Missing/non-numeric {key}") from exc
    if not math.isfinite(value) or value < 0 or (strictly_positive and value == 0):
        raise ScienceError("INVALID_PARAMETER", f"Invalid {key}")
    return value


def measurement_range(raw: str) -> tuple[float, float]:
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s+K\s*", raw)
    if not match:
        raise ScienceError(
            "AMBIGUOUS_RANGE", "Measurement range requires explicit increasing K limits"
        )
    low, high = map(float, match.groups())
    if not (0 < low < high <= 10000):
        raise ScienceError("AMBIGUOUS_RANGE", "Invalid measured range")
    return low, high


def select_regime(raw: dict[str, str], t: float) -> tuple[str, float, float, list[str]]:
    ht_keys = ["EaHT", "AHT", "T*"]
    has_ht = [bool(raw.get(k, "").strip()) for k in ht_keys]
    warnings = []
    if any(has_ht):
        if not all(has_ht):
            raise ScienceError(
                "AMBIGUOUS_REGIME", "Partial HT metadata: no defensible regime selection"
            )
        transition = numeric(raw, "T*", strictly_positive=True)
        # Validate both pairs even when the requested side is the other regime.
        ht_ea = numeric(raw, "EaHT", strictly_positive=True)
        ht_a = numeric(raw, "AHT", strictly_positive=True)
        lt_ea = numeric(raw, "Ea", strictly_positive=True)
        lt_a = numeric(raw, "A", strictly_positive=True)
        if abs(t - transition) <= 1e-6:
            raise ScienceError(
                "AT_TRANSITION", "Paper defines T<T* and T>T*; exact T* needs review"
            )
        if abs(t - transition) <= 5:
            warnings.append("NEAR_TRANSITION")
        low, high = measurement_range(raw["Measurement_temperature_range"])
        if not low <= transition <= high:
            warnings.append("TRANSITION_OUTSIDE_REPORTED_RANGE")
        return ("LT", lt_ea, lt_a, warnings) if t < transition else ("HT", ht_ea, ht_a, warnings)
    return (
        "SINGLE",
        numeric(raw, "Ea", strictly_positive=True),
        numeric(raw, "A", strictly_positive=True),
        warnings,
    )


def wrong_equation_demo(sigma: float, temperature_k: float) -> dict[str, object]:
    """An explicitly dimensionally invalid reuse of the dataset prefactor."""
    wrong = sigma * temperature_k
    if not math.isfinite(wrong):
        raise ScienceError("NUMERIC_RANGE", "Adversarial value overflows")
    return {
        "status": "REJECTED_WRONG_FORMULA",
        "correct_equation": EQUATION,
        "correct_value": {"value": sigma, "unit": "S/cm"},
        "wrong_expression": "A * exp(-Ea/(k_B*T))",
        "wrong_quantity": {"value": wrong, "unit": "K S/cm"},
        "numeric_ratio": {"value": temperature_k, "unit": "K"},
        "warning": "Same numeric A reused without 1/T. The wrong quantity is NOT conductivity.",
        "scope": "Educational counterexample for this dataset; not an accusation about any source paper.",
    }
