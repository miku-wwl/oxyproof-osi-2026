import math
import re

from backend.app.schemas import GoalPlan, ResolvedPlan, ScreenRequest
from backend.app.science.conductivity import ScienceError, to_kelvin


class PlanError(ValueError):
    pass


def offline_plan(request: ScreenRequest, classes: list[str]) -> GoalPlan:
    goal = request.goal
    matches = re.findall(
        r"(?<![\w.])(-?\d+(?:\.\d+)?)\s*(?:°\s*|deg\s*)?(Celsius|Kelvin|C|K)\b",
        goal,
        re.I,
    )
    unsupported = []
    if len(matches) > 1:
        unsupported.append("Multiple goal temperatures: use one explicit operating temperature")
    if re.search(r"\b(fahrenheit|\d+\s*°?\s*F)\b", goal, re.I):
        unsupported.append("Fahrenheit is unsupported; use C or K")
    unsupported_words = re.findall(
        r"\b(?:exclude|without|stable|stability|atmosphere|cheap|cost|toxic|toxicity|confidence|uncertainty|pressure|synthesize)\b",
        goal,
        re.I,
    )
    if unsupported_words:
        unsupported.append(
            "Unsupported constraint(s): " + ", ".join(sorted(set(unsupported_words)))
        )
    if re.search(
        r"\b(?:above|below|over|under|between|at least|at most|greater|less than|minimum|maximum)\b|[<>]",
        goal,
        re.I,
    ):
        unsupported.append("Inequality/range constraints need a supported structured field")
    type_matches = re.findall(r"\b(bulk|total)\b", goal, re.I)
    if len({v.lower() for v in type_matches}) > 1:
        unsupported.append("Bulk and total cannot be combined in a ranking")
    class_matches = [
        c for c in classes if re.search(r"\b" + re.escape(c.rstrip("s")) + r"s?\b", goal, re.I)
    ]
    if len(class_matches) > 1:
        unsupported.append("Multiple material classes: select one structured class")
    temp, unit = matches[0] if matches else (None, "C")
    formula_match = re.search(r"\bformula\s+([A-Za-z0-9.]+)", goal, re.I)
    return GoalPlan(
        temperature=float(temp) if temp is not None else None,
        temperature_unit="K" if unit.lower().startswith("k") else "C",
        conductivity_type=type_matches[0].lower() if type_matches else None,
        material_class=class_matches[0] if class_matches else None,
        formula_query=formula_match.group(1) if formula_match else None,
        unsupported_constraints=unsupported,
    )


def resolve_plan(request: ScreenRequest, proposed: GoalPlan, classes: list[str]) -> ResolvedPlan:
    if proposed.unsupported_constraints:
        raise PlanError("; ".join(proposed.unsupported_constraints))
    temperature = request.temperature
    unit = request.temperature_unit
    if temperature is None:
        temperature, unit = proposed.temperature, proposed.temperature_unit
    if temperature is None:
        raise PlanError("INSUFFICIENT_EVIDENCE: specify a temperature with C or K units")
    try:
        kelvin = to_kelvin(temperature, unit)
        if proposed.temperature is not None and request.temperature is not None:
            goal_k = to_kelvin(proposed.temperature, proposed.temperature_unit)
            if not math.isclose(kelvin, goal_k, abs_tol=1e-6):
                raise PlanError("CONFLICTING_TEMPERATURE: goal and structured input disagree")
    except ScienceError as exc:
        raise PlanError(str(exc)) from exc
    for field in ["conductivity_type", "material_class", "formula_query"]:
        explicit, inferred = getattr(request, field), getattr(proposed, field)
        if explicit and inferred and explicit.casefold() != inferred.casefold():
            raise PlanError(f"CONFLICTING_{field.upper()}: goal and structured input disagree")
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
