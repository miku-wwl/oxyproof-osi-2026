"""Conservative coverage grammar; unknown text is retained and fails closed."""

import math
import re
from dataclasses import dataclass

from backend.app.schemas import GoalPlan, RequestCoverage, ResolvedPlan, ScreenRequest, TextSpan
from backend.app.science.conductivity import ScienceError, to_kelvin

TEMP = r"(?<![\w.])(-?\d+(?:\.\d+)?)\s*(?:°\s*|degrees?\s+|deg\s*)?(Celsius|Kelvin|C|K)\b"


class PlanError(ValueError):
    def __init__(self, message: str, code: str | None = None):
        self.code = code or (message.split(":", 1)[0] if ":" in message else "PLAN_REJECTED")
        super().__init__(message)


@dataclass
class Interpretation:
    plan: GoalPlan
    coverage: RequestCoverage
    interval: tuple[float, str, float, str] | None = None
    row_ids: list[int] | None = None


def interpret(goal: str, classes: list[str], *, interval: bool = False) -> Interpretation:
    masked = list(goal)
    recognized = []

    def claim(pattern: str, field: str):
        matches = list(re.finditer(pattern, "".join(masked), re.I))
        for match in matches:
            recognized.append(
                TextSpan(
                    start=match.start(),
                    end=match.end(),
                    text=goal[match.start() : match.end()],
                    field=field,
                )
            )
            masked[match.start() : match.end()] = " " * (match.end() - match.start())
        return matches

    problems = []
    bounds = None
    # Explicit presentation semantics, not evidence that any performance threshold holds.
    claim(r"\baround(?=\s+" + TEMP + r")", "nominal_temperature")
    claim(r"\bpromising\b", "conditional_screening_order")
    claim(r"\bshow their conductivity estimates\b", "presentation")
    claim(r"\btell me what evidence supports the comparison\b", "presentation")
    claim(r"\bHow does the ranking of\b", "interval_action")
    claim(r"\bExplain the change using their (?:published )?activation energies\b", "presentation")
    claim(r"\bpublished\b", "published_data_scope")
    named = (
        claim(r"\b(?:the\s+)?three comparable Huang materials\b", "named_selection")
        if interval
        else []
    )
    if len(named) > 1:
        problems.append("CONFLICTING_RECORD_SELECTION: specify the named comparison once")
    claim(r"\bchange(?=\s+from\b)", "interval_action")
    if interval:
        ranges = claim(
            r"\b(?:between|from)\s+" + TEMP + r"\s+(?:and|to)\s+" + TEMP, "temperature_interval"
        )
        if len(ranges) == 1:
            lo, lu, hi, hu = ranges[0].groups()
            bounds = (
                float(lo),
                "K" if lu.lower().startswith("k") else "C",
                float(hi),
                "K" if hu.lower().startswith("k") else "C",
            )
        elif ranges:
            problems.append("MULTIPLE_TEMPERATURE_CONSTRAINTS: use one interval")
    temperatures = claim(TEMP, "temperature")
    if len(temperatures) > 1 or (interval and temperatures):
        problems.append(
            "MULTIPLE_TEMPERATURE_CONSTRAINTS: use one operating temperature, or the interval tool with explicit bounds"
        )
    formulas = claim(r"\bformula\s+([A-Za-z0-9.]+)\b", "formula_query")
    if len(formulas) > 1:
        problems.append("UNVERIFIED_CONSTRAINTS: only one formula substring is supported")
    types = claim(r"\b(bulk|total)\b", "conductivity_type")
    if len({m.group(1).lower() for m in types}) > 1:
        problems.append("CONFLICTING_CONDUCTIVITY_TYPE: bulk and total cannot be combined")
    found_classes = []
    for c in sorted(classes, key=len, reverse=True):
        if claim(r"\b" + re.escape(c.rstrip("s")) + r"s?\b", "material_class"):
            found_classes.append(c)
    if len(found_classes) > 1:
        problems.append("UNVERIFIED_CONSTRAINTS: select one material class")
    claim(
        r"\b(?:show|include|with)?\s*(?:source provenance|source references|provenance|citations|evidence|audit report)\b",
        "presentation",
    )
    claim(r"\b(?:find|screen|compare|analyze|analyse|inspect)\b", "action")
    claim(
        r"\b(?:oxygen[ -]ion[ -]conducting\s+oxide\s+materials|oxygen[ -]ion\s+conductors|oxygen[ -]ion[ -]conducting\s+oxides|conductors|conductivity|materials|records)\b",
        "domain",
    )
    if interval:
        claim(
            r"\b(?:temperature interval|temperature range|rank reversals|rank reversal|ordering|conductivity curves)\b",
            "interval_action",
        )
    claim(r"\b(?:at|with|and|for|the|please|class)\b", "connector")
    residue = "".join(masked)
    # Preserve numeric punctuation in unresolved requirements, such as 10,000 hours.
    unknown_token = r"(?:[^\s.,;:!?]|(?<=\d),(?=\d))+"
    unresolved = [
        TextSpan(
            start=m.start(),
            end=m.end(),
            text=goal[m.start() : m.end()],
            field="UNVERIFIED_CONSTRAINTS",
        )
        for m in re.finditer(unknown_token + r"(?:\s+" + unknown_token + r")*", residue)
    ]
    if unresolved:
        problems.append(
            "UNVERIFIED_CONSTRAINTS: unsupported text: " + "; ".join(s.text for s in unresolved)
        )
    temp, unit = temperatures[0].groups() if temperatures else (None, "C")
    plan = GoalPlan(
        temperature=float(temp) if temp is not None else None,
        temperature_unit="K" if unit.lower().startswith("k") else "C",
        conductivity_type=types[0].group(1).lower() if types else None,
        material_class=found_classes[0] if found_classes else None,
        formula_query=formulas[0].group(1) if formulas else None,
        unsupported_constraints=problems,
    )
    return Interpretation(
        plan,
        RequestCoverage(
            grammar_version="2.6",
            recognized=sorted(recognized, key=lambda s: s.start),
            unresolved=unresolved,
            complete=not problems,
        ),
        bounds,
        [1, 2, 3] if named else None,
    )


def offline_plan(request: ScreenRequest, classes: list[str]) -> GoalPlan:
    return interpret(request.goal, classes).plan


def validate_model_coverage(goal: str, proposed: GoalPlan, classes: list[str]) -> None:
    independent = interpret(goal, classes).plan
    if independent.unsupported_constraints:
        raise PlanError("; ".join(independent.unsupported_constraints))
    if proposed.unsupported_constraints:
        raise PlanError(
            "MODEL_PLAN_CONFLICT: model flags unsupported requirements on an independently covered request; provider prose withheld"
        )
    for field in ("temperature", "conductivity_type", "material_class", "formula_query"):
        actual, model = getattr(independent, field), getattr(proposed, field)
        if field == "temperature" and actual is not None and model is not None:
            if not math.isclose(
                to_kelvin(actual, independent.temperature_unit),
                to_kelvin(model, proposed.temperature_unit),
                abs_tol=1e-6,
            ):
                raise PlanError(
                    "MODEL_PLAN_CONFLICT: temperature differs from independently parsed input"
                )
        elif actual != model:
            raise PlanError(f"MODEL_PLAN_CONFLICT: {field} omitted, invented or changed")


def resolve_plan(request: ScreenRequest, proposed: GoalPlan, classes: list[str]) -> ResolvedPlan:
    if proposed.unsupported_constraints:
        raise PlanError("; ".join(proposed.unsupported_constraints))
    temperature, unit = request.temperature, request.temperature_unit
    if temperature is None:
        temperature, unit = proposed.temperature, proposed.temperature_unit
    if temperature is None:
        raise PlanError("INSUFFICIENT_EVIDENCE: specify a temperature with C or K units")
    try:
        kelvin = to_kelvin(temperature, unit)
        if proposed.temperature is not None and request.temperature is not None:
            if not math.isclose(
                kelvin, to_kelvin(proposed.temperature, proposed.temperature_unit), abs_tol=1e-6
            ):
                raise PlanError(
                    "CONFLICTING_TEMPERATURE: goal and structured input disagree; synchronize the goal or change the controls"
                )
    except ScienceError as exc:
        raise PlanError(f"{exc.code}: {exc}") from exc
    for field in ["conductivity_type", "material_class", "formula_query"]:
        explicit, inferred = getattr(request, field), getattr(proposed, field)
        if explicit and inferred and explicit.casefold() != inferred.casefold():
            raise PlanError(
                f"CONFLICTING_{field.upper()}: goal and structured input disagree; synchronize or edit both"
            )
    material_class = request.material_class or proposed.material_class
    if material_class and material_class not in classes:
        raise PlanError("UNKNOWN_CLASS: use the exact class label from /api/catalog")
    return ResolvedPlan(
        temperature_k=kelvin,
        conductivity_type=request.conductivity_type or proposed.conductivity_type or "bulk",
        material_class=material_class,
        formula_query=request.formula_query or proposed.formula_query,
        row_ids=request.row_ids,
        allow_extrapolation=request.allow_extrapolation,
        top_n=request.top_n,
    )
