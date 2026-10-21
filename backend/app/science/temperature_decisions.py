"""Analytic pairwise roots within joint published fixed-regime intervals.

Plot samples never determine the event locations or decision intervals.
Fits on opposite sides of T* are never assumed continuous.
"""

import itertools
import math

from backend.app.agents.planner import PlanError, interpret
from backend.app.agents.trace import execution_trace
from backend.app.data.ingest import Repository
from backend.app.reports.audit import calculate_record, code_version, group_key, warn
from backend.app.schemas import Quantity, Record, TraceStep
from backend.app.science.conductivity import (
    KB_EV_K,
    ScienceError,
    measurement_range,
    numeric,
    select_regime,
    to_kelvin,
)
from backend.app.science.decision_schemas import (
    DecisionEvent,
    DecisionSegment,
    MaterialEvidence,
    PointExclusion,
    RankedValue,
    RankingPoint,
    RejectedCrossover,
    TemperatureReport,
    TemperatureRequest,
    ValidityInterval,
)


def material_evidence(record: Record, conductivity_type: str) -> MaterialEvidence:
    evidence = MaterialEvidence(
        record=record, measured_range_k=[], transition_k=None, validity_intervals=[]
    )
    try:
        low, high = measurement_range(record.temperature_range_raw)
        evidence.measured_range_k = [low, high]
        # Validate every prerequisite, including the regime not currently selected.
        probe = low if record.raw.get("T*") != str(low) else high
        try:
            select_regime(record.raw, probe)
        except ScienceError as exc:
            if exc.code != "AT_TRANSITION":
                raise
            select_regime(record.raw, (low + high) / 2)
        if record.conductivity_type != conductivity_type:
            raise ScienceError(
                "TYPE_NOT_COMPARABLE",
                f"Requested {conductivity_type}, published {record.conductivity_type}",
            )
        tstar = numeric(record.raw, "T*", strictly_positive=True) if record.raw.get("T*") else None
        evidence.transition_k = tstar
        definitions = (
            [("SINGLE", low, high, "")]
            if tstar is None
            else [("LT", low, min(high, tstar), ""), ("HT", max(low, tstar), high, "HT")]
        )
        for regime, left, right, suffix in definitions:
            if left >= right:
                continue
            evidence.validity_intervals.append(
                ValidityInterval(
                    low_k=left,
                    high_k=right,
                    low_inclusive=left != tstar,
                    high_inclusive=right != tstar,
                    regime=regime,
                    activation_energy=Quantity(
                        value=numeric(record.raw, "Ea" + suffix, strictly_positive=True), unit="meV"
                    ),
                    prefactor=Quantity(
                        value=numeric(record.raw, "A" + suffix, strictly_positive=True),
                        unit="K S/cm",
                    ),
                )
            )
    except ScienceError as exc:
        evidence.excluded_reason = f"{exc.code}: {exc}"
    return evidence


def ranking_at(materials: list[MaterialEvidence], t: float) -> RankingPoint:
    values, excluded = [], []
    for item in materials:
        if item.excluded_reason:
            excluded.append(
                PointExclusion(row_id=item.record.row_id, reasons=[item.excluded_reason])
            )
            continue
        result = calculate_record(item.record, t)
        if result.status != "CALCULATED":
            excluded.append(
                PointExclusion(
                    row_id=item.record.row_id,
                    reasons=[w.code for w in result.warnings if w.code != "MISSING_CONDITIONS"],
                )
            )
            continue
        values.append(
            RankedValue(
                row_id=result.row_id,
                formula=result.formula,
                conductivity_s_cm=result.computed_values_with_units["conductivity"].value,
                regime=result.regime,
                warning_codes=[w.code for w in result.warnings],
            )
        )
    values.sort(key=lambda v: (-v.conductivity_s_cm, v.row_id))
    for v in values:
        v.tie_with = [
            other.row_id
            for other in values
            if other.row_id != v.row_id
            and math.isclose(v.conductivity_s_cm, other.conductivity_s_cm, rel_tol=1e-10, abs_tol=0)
        ]
    status = (
        "INSUFFICIENT_EVIDENCE"
        if len(values) < 2
        else "PARTIAL_EVIDENCE"
        if excluded
        else "SUPPORTED_CONDITIONAL_COMPARISON"
    )
    return RankingPoint(
        temperature_k=t,
        status=status,
        ordering=[v.row_id for v in values] if len(values) >= 2 else [],
        values=values,
        excluded=excluded,
    )


def ordering_text(point: RankingPoint) -> str:
    if not point.ordering:
        return "insufficient evidence"
    seen = set()
    groups = []
    for value in point.values:
        if value.row_id in seen:
            continue
        ids = [i for i in point.ordering if i == value.row_id or i in value.tie_with]
        seen.update(ids)
        groups.append(" = ".join(map(str, ids)))
    return " > ".join(groups)


def analyze_temperature_interval(
    request: TemperatureRequest,
    repository: Repository,
    *,
    model: str | None = None,
    response_id: str | None = None,
    provider_metadata: dict | None = None,
) -> TemperatureReport:
    if request.mode == "REAL_LLM" and (
        not model or not (response_id or (provider_metadata or {}).get("local_invocation_id"))
    ):
        from backend.app.agents.llm import LLMError

        raise LLMError("UNVALIDATED_MODEL_PLAN: REAL_LLM requires a validated provider response")
    parsed = interpret(request.goal, repository.classes(), interval=True)
    report = TemperatureReport(
        status="INSUFFICIENT_EVIDENCE",
        evidence_verdicts=[],
        research_request=request,
        resolved_plan={},
        request_coverage=parsed.coverage,
        runtime_mode=request.mode,
        llm_model=model,
        llm_response_id=response_id,
        validated_arguments={},
        source=repository.source,
        code_version=code_version(),
        warnings=[warn("MISSING_CONDITIONS")],
        trace=[
            TraceStep(
                step="interpret_constraints",
                outcome="COVERAGE_CHECKED",
                detail="Unknown text fails closed; structured fields and explicit natural-language fields must agree.",
            )
        ],
        next_scientific_actions=[
            "Review original atmosphere, preparation and density and verify bulk versus total separation.",
            "Repeat conductivity measurements bracketing reported transitions and predicted fixed-regime crossings. These are bounded proposals; no experiment was executed.",
        ],
    )
    try:
        if parsed.plan.unsupported_constraints:
            raise PlanError("; ".join(parsed.plan.unsupported_constraints))
        if parsed.row_ids and sorted(request.row_ids) != parsed.row_ids:
            raise PlanError(
                "CONFLICTING_RECORD_SELECTION: named Huang demonstration requires rows 1, 2, 3"
            )
        if parsed.row_ids and any(
            i not in repository.by_id
            or repository.by_id[i].source_doi != "10.1111/j.1151-2916.1998.tb02662.x"
            for i in parsed.row_ids
        ):
            raise PlanError(
                "ROWS_NOT_LOADED: named comparison requires its verified published rows"
            )
        if parsed.plan.formula_query or parsed.plan.material_class:
            raise PlanError(
                "UNVERIFIED_CONSTRAINTS: interval tool selects exact source groups or row IDs; use structured record selection"
            )
        if (
            parsed.plan.conductivity_type
            and parsed.plan.conductivity_type != request.conductivity_type
        ):
            raise PlanError("CONFLICTING_CONDUCTIVITY_TYPE: goal and structured input disagree")
        low, high = (
            to_kelvin(request.temperature_min, request.temperature_unit),
            to_kelvin(request.temperature_max, request.temperature_unit),
        )
        if high <= low:
            raise PlanError("INVALID_INTERVAL: require increasing temperature bounds")
        if parsed.interval:
            a, au, b, bu = parsed.interval
            if not (
                math.isclose(low, to_kelvin(a, au), abs_tol=1e-6)
                and math.isclose(high, to_kelvin(b, bu), abs_tol=1e-6)
            ):
                raise PlanError("CONFLICTING_TEMPERATURE: text and structured interval disagree")
        selected = [
            to_kelvin(t, request.temperature_unit) for t in request.selected_temperatures
        ] or [low, high]
        if any(t < low or t > high for t in selected):
            raise PlanError(
                "SELECTED_TEMPERATURE_OUTSIDE_INTERVAL: selected points must lie within requested interval"
            )
        if set(request.row_ids) - repository.by_id.keys():
            raise PlanError(
                "ROWS_NOT_LOADED: explicit selection is incomplete in loaded dataset scope"
            )
        records = (
            [r for r in repository.records if r.row_id in request.row_ids]
            if request.row_ids
            else [
                r
                for r in repository.records
                if request.comparison_group and group_key(r) == request.comparison_group
            ]
        )
        if not records:
            raise PlanError(
                "INSUFFICIENT_EVIDENCE: select an exact comparison group or at least two loaded row IDs"
            )
        if len(records) > request.max_materials:
            raise PlanError(
                "MATERIAL_LIMIT: narrow the selection; records are never silently truncated"
            )
        keys = {group_key(r) for r in records}
        if len(keys) != 1 or (request.comparison_group and keys != {request.comparison_group}):
            raise PlanError(
                "NON_COMPARABLE_SOURCE_GROUPS: exact DOI, type, method and measured range must match"
            )
        report.comparison_group = group_key(records[0])
        report.materials = [material_evidence(r, request.conductivity_type) for r in records]
        if len(records) < 2:
            raise PlanError(
                "INSUFFICIENT_EVIDENCE: at least two records are required for a comparison"
            )
        plan = {
            "temperature_min_k": low,
            "temperature_max_k": high,
            "row_ids": [r.row_id for r in records],
            "comparison_group": report.comparison_group,
            "conductivity_type": request.conductivity_type,
            "evidence_policy": request.evidence_policy,
            "points": request.points,
        }
        report.resolved_plan = report.validated_arguments = plan
        report.trace.append(
            TraceStep(
                step="retrieve_and_validate",
                outcome="REAL_PUBLISHED_DATA",
                detail=f"{len(records)} exact-group records; validate measurement range and every fit prerequisite.",
            )
        )
        boundaries = {low, high}
        transitions = {}
        for m in report.materials:
            for t in m.measured_range_k:
                if low < t < high:
                    boundaries.add(t)
            if (
                m.transition_k is not None
                and low <= m.transition_k <= high
                and not m.excluded_reason
            ):
                transitions.setdefault(m.transition_k, []).append(m.record.row_id)
                for t in (m.transition_k - 5, m.transition_k, m.transition_k + 5):
                    if low < t < high:
                        boundaries.add(t)
        # Analytic candidates are calculated per full evidence-regime intersection.
        # They are not estimated from graph samples or assumed fit continuity.
        for left, right in itertools.combinations(report.materials, 2):
            for li, ri in itertools.product(left.validity_intervals, right.validity_intervals):
                a, b = max(li.low_k, ri.low_k), min(li.high_k, ri.high_k)
                if a >= b:
                    continue
                log_ratio_a = math.log(li.prefactor.value) - math.log(ri.prefactor.value)
                delta_e = (li.activation_energy.value - ri.activation_energy.value) / 1000
                if abs(log_ratio_a) < 1e-14:
                    if log_ratio_a != 0 or delta_e != 0:
                        report.warnings.append(
                            warn(
                                "CROSSOVER_UNRESOLVED",
                                "Nearly equal log-prefactors: no numerically stable isolated root reported.",
                            )
                        )
                    continue  # Parallel/identical log-ratio curves: no isolated root.
                root = delta_e / (KB_EV_K * log_ratio_a)
                if not math.isfinite(root) or root <= 0:
                    continue
                rows = [left.record.row_id, right.record.row_id]
                at_transition = any(
                    m.transition_k is not None and abs(root - m.transition_k) <= 1e-6
                    for m in (left, right)
                )
                if not (a + 1e-6 < root < b - 1e-6) or at_transition:
                    report.rejected_crossovers.append(
                        RejectedCrossover(
                            row_ids=rows,
                            candidate_temperature_k=root,
                            fixed_regime_overlap_k=[a, b],
                        )
                    )
                    continue
                if not low < root < high:
                    report.rejected_crossovers.append(
                        RejectedCrossover(
                            row_ids=rows,
                            candidate_temperature_k=root,
                            fixed_regime_overlap_k=[a, b],
                            reason="Valid fixed-regime mathematical root lies outside requested interval; no switching claim within this request.",
                        )
                    )
                    continue
                # Validate numeric representability and a sign change independently of sampling.
                epsilon = min(root - a, b - root, root - low, high - root, 0.01) / 10
                before = log_ratio_a - delta_e / (KB_EV_K * (root - epsilon))
                after = log_ratio_a - delta_e / (KB_EV_K * (root + epsilon))
                check = ranking_at([left, right], root)
                if before * after >= 0 or len(check.values) != 2:
                    report.warnings.append(
                        warn(
                            "CROSSOVER_UNRESOLVED",
                            f"Pair {rows}: numeric root could not be verified",
                        )
                    )
                    continue
                boundaries.add(root)
                report.events.append(
                    DecisionEvent(
                        kind="CONTINUOUS_MODEL_CROSSOVER",
                        temperature_k=root,
                        row_ids=rows,
                        verdict="SUPPORTED_MODEL_RANK_REVERSAL",
                        exact_continuous_crossing=True,
                        left_ordering=ranking_at(report.materials, root - epsilon).ordering,
                        right_ordering=ranking_at(report.materials, root + epsilon).ordering,
                        explanation=f"Within joint measured fixed regimes {li.regime}/{ri.regime}: ln(A_i)-ln(A_j)={log_ratio_a:.12g}; delta Ea={delta_e:.12g} eV. T=delta Ea/[k_B*delta ln(A)]. Model-derived root, not an observed crossing or an uncertainty estimate.",
                    )
                )
        # Boundaries are evaluated explicitly and never joined by a curve segment.
        split = sorted(boundaries)
        for a, b in itertools.pairwise(split):
            mid = (a + b) / 2
            ranked = ranking_at(report.materials, mid)
            report.segments.append(
                DecisionSegment(
                    low_k=a,
                    high_k=b,
                    ordering=ranked.ordering,
                    regimes={str(v.row_id): v.regime for v in ranked.values},
                    status=ranked.status,
                    review_neighborhood=any(
                        m.transition_k is not None and abs(mid - m.transition_k) <= 5
                        for m in report.materials
                    ),
                    tie_groups=[
                        list(ids)
                        for ids in sorted(
                            {
                                tuple(sorted([v.row_id, *v.tie_with]))
                                for v in ranked.values
                                if v.tie_with
                            }
                        )
                    ],
                )
            )
        for t, rows in transitions.items():
            distances = [abs(t - x) for x in split if abs(t - x) > 1e-7]
            delta = min([0.001, *[x / 4 for x in distances]])
            before = ranking_at(report.materials, t - delta) if t > low else None
            after = ranking_at(report.materials, t + delta) if t < high else None
            changed = bool(
                before
                and after
                and before.ordering
                and after.ordering
                and before.ordering != after.ordering
            )
            report.events.append(
                DecisionEvent(
                    kind="REGIME_BOUNDARY_DRIVEN_CHANGE"
                    if changed
                    else "PUBLISHED_REGIME_BOUNDARY",
                    temperature_k=t,
                    row_ids=rows,
                    verdict="REGIME_BOUNDARY_REVIEW",
                    left_ordering=before.ordering if before else [],
                    right_ordering=after.ordering if after else [],
                    explanation="Published T* changes the selected fit. Exact T* is withheld; continuity between fits is not assumed. The ±5 K review neighborhood is an engineering heuristic, not an uncertainty interval.",
                )
            )
        report.events.sort(key=lambda e: (e.temperature_k, e.kind, e.row_ids))
        report.boundary_rankings = [ranking_at(report.materials, t) for t in split]
        report.selected_rankings = [ranking_at(report.materials, t) for t in sorted(set(selected))]
        sample_t = {low + (high - low) * i / (request.points - 1) for i in range(request.points)}
        # Include exact evidence boundaries and T* so clients can preserve nulls.
        sample_t.update(split)
        sample_t.update(selected)
        report.curve_points = [ranking_at(report.materials, t) for t in sorted(sample_t)]
        report.status = (
            "CALCULATED_WITH_WARNINGS"
            if any(s.ordering for s in report.segments)
            else "INSUFFICIENT_EVIDENCE"
        )
        report.evidence_verdicts = (
            ["SUPPORTED_CONDITIONAL_COMPARISON"]
            if report.status == "CALCULATED_WITH_WARNINGS"
            else ["INSUFFICIENT_EVIDENCE"]
        )
        if any(e.exact_continuous_crossing for e in report.events):
            report.evidence_verdicts.append("SUPPORTED_MODEL_RANK_REVERSAL")
        if transitions:
            report.evidence_verdicts.append("REGIME_BOUNDARY_REVIEW")
        if any(p.excluded for p in report.curve_points):
            report.warnings.append(
                warn(
                    "PARTIAL_OR_ABSENT_EVIDENCE",
                    "Some temperatures or records are withheld. Inspect excluded reasons and valid intervals; no ranking outside measurement bounds.",
                )
            )
        if report.rejected_crossovers:
            report.warnings.append(
                warn(
                    "REJECTED_CROSSOVER_CANDIDATES",
                    "Analytic candidates outside fixed-regime evidence or the requested interval are retained separately and never plotted as supported switches.",
                )
            )
        report.interpretation = [
            f"At {p.temperature_k:g} K, conditional model order (row IDs): {ordering_text(p)}. Equality uses numerical tolerance only."
            for p in report.selected_rankings
        ]
        report.interpretation.extend(
            [
                "Ordering depends on activation-energy differences and prefactor ratios within each valid regime. Regime-boundary events are reviewed separately from continuous roots.",
                "The curated dataset does not establish humidity tolerance, phase stability, lifetime, cost, toxicity or sample-to-sample uncertainty. No material was discovered or measured by this tool.",
            ]
        )
        report.trace.extend(
            [
                TraceStep(
                    step="execute_allowlisted_tool",
                    outcome="analyze_temperature_interval",
                    detail="Deterministic interval intersections, analytic pair roots, boundary-aware sampling and conditional ordering.",
                ),
                TraceStep(
                    step="independent_evidence_audit",
                    outcome=report.status,
                    detail="Exact-source grouping, measured-only policy, strict T* exclusion and original raw records attached.",
                ),
                TraceStep(
                    step="validated_explanation",
                    outcome="TEMPLATE_FROM_VALIDATED_OUTPUT",
                    detail="Only deterministic templates and existing DOI/parameters are shown; no model-generated arithmetic or citations.",
                ),
            ]
        )
    except (PlanError, ScienceError) as exc:
        report.status = "INSUFFICIENT_EVIDENCE"
        report.evidence_verdicts = [exc.code]
        report.warnings.append(warn(exc.code, str(exc)))
        report.trace.append(
            TraceStep(step="validate_or_abstain", outcome=exc.code, detail=str(exc))
        )
    report.execution_trace = execution_trace(
        report, "analyze_temperature_interval", provider_metadata=provider_metadata
    )
    return report
