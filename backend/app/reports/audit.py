import hashlib
import subprocess
from collections import defaultdict

from backend.app import __version__
from backend.app.agents.llm import plan_with_llm
from backend.app.agents.planner import (
    PlanError,
    interpret,
    offline_plan,
    resolve_plan,
    validate_model_coverage,
)
from backend.app.data.ingest import ROOT, Repository
from backend.app.schemas import (
    AuditReport,
    Calculation,
    ComparisonGroup,
    Quantity,
    Record,
    ScreenRequest,
    TraceStep,
    WarningItem,
)
from backend.app.science.conductivity import (
    ScienceError,
    conductivity_at_temperature,
    measurement_range,
    select_regime,
)

WARNING_MESSAGES = {
    "MISSING_CONDITIONS": "Atmosphere, preparation and density are not dataset columns; sample comparability needs original-paper review.",
    "NEAR_TRANSITION": "Within 5 K of T*: review heuristic, not a validated uncertainty bound.",
    "TRANSITION_OUTSIDE_REPORTED_RANGE": "Reported T* lies outside the reported measurement interval. Review original source.",
    "EXTRAPOLATION": "Outside the reported measurement interval. Calculation is unranked extrapolation; phase stability is unknown.",
}


def warn(code: str, message: str | None = None) -> WarningItem:
    return WarningItem(code=code, message=message or WARNING_MESSAGES[code])


def code_version() -> dict[str, str]:
    digest = hashlib.sha256()
    paths = sorted((ROOT / "backend/app").rglob("*.py")) + [
        ROOT / "pyproject.toml",
        ROOT / "uv.lock",
    ]
    for path in paths:
        if path.exists():
            digest.update(path.relative_to(ROOT).as_posix().encode())
            digest.update(b"\0")
            digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
    try:
        base = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=2,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        base = "UNAVAILABLE"
    return {
        "app_version": __version__,
        "git_base": base,
        "calculation_source_sha256": digest.hexdigest(),
    }


def group_key(record: Record) -> str:
    # Human-inspectable key; no claim that missing conditions actually match.
    return " | ".join(
        [
            record.source_doi,
            record.conductivity_type,
            record.measurement,
            record.temperature_range_raw,
        ]
    )


def calculate_record(record: Record, t: float, allow_extrapolation: bool = False) -> Calculation:
    result = Calculation(
        status="INSUFFICIENT_EVIDENCE",
        row_id=record.row_id,
        formula=record.formula,
        source_doi=record.source_doi,
        source_location=record.raw["Source"],
        conductivity_type=record.conductivity_type,
        comparison_group=group_key(record),
        inputs_with_units={"temperature": Quantity(value=t, unit="K")},
        warnings=[warn("MISSING_CONDITIONS")],
        next_measurement="Heuristic proposal: verify original atmosphere, preparation and density; measure ionic conductivity near the target temperature with bulk/grain-boundary separation. No experiment has been run.",
        raw_source_record=record.raw,
    )
    try:
        low, high = measurement_range(record.temperature_range_raw)
        result.inputs_with_units.update(
            {
                "measured_low": Quantity(value=low, unit="K"),
                "measured_high": Quantity(value=high, unit="K"),
            }
        )
        regime, ea, a, flags = select_regime(record.raw, t)
        result.regime = regime
        result.warnings.extend(warn(flag) for flag in flags)
        result.inputs_with_units.update(
            {
                "activation_energy": Quantity(value=ea, unit="meV"),
                "prefactor": Quantity(value=a, unit="K S/cm"),
            }
        )
        if record.raw["T*"]:
            result.inputs_with_units["transition"] = Quantity(
                value=float(record.raw["T*"]), unit="K"
            )
        result.trace.append(
            TraceStep(
                step="select_model",
                outcome=regime,
                detail="Published sigma*T convention; meV converted to eV; measured interval is not assumed to establish phase stability.",
            )
        )
        outside = not low <= t <= high
        if outside and not allow_extrapolation:
            raise ScienceError(
                "OUTSIDE_MEASURED_RANGE",
                f"T={t:g} K outside [{low:g}, {high:g}] K; no calculation authorized",
            )
        if outside:
            result.warnings.append(warn("EXTRAPOLATION"))
        sigma = conductivity_at_temperature(a, ea, t)
        result.computed_values_with_units["conductivity"] = Quantity(value=sigma, unit="S/cm")
        result.status = "EXTRAPOLATED" if outside else "CALCULATED"
        result.trace.append(
            TraceStep(
                step="compute",
                outcome=result.status,
                detail="sigma=(A/T)*exp(-(Ea/1000)/(k_B*T)); deterministic log-domain arithmetic.",
            )
        )
    except ScienceError as exc:
        result.warnings.append(warn(exc.code, str(exc)))
        result.trace.append(
            TraceStep(step="audit", outcome="INSUFFICIENT_EVIDENCE", detail=f"{exc.code}: {exc}")
        )
        if exc.code in ("AMBIGUOUS_REGIME", "AT_TRANSITION"):
            result.next_measurement = "Heuristic proposal: inspect the original temperature plot, obtain an explicit crossover and fit both regimes with measurements bracketing the transition. No experiment has been run."
    if record.conductivity_type not in ("bulk", "total"):
        result.warnings.append(
            warn(
                "UNKNOWN_CONDUCTIVITY_TYPE",
                "Not clearly mentioned in dataset; never coerced to total, never ranked.",
            )
        )
    return result


def screen(request: ScreenRequest, repository: Repository, *, model_plan=None) -> AuditReport:
    coverage = interpret(request.goal, repository.classes()).coverage
    trace = []
    warnings = [
        warn(
            "CONDITIONAL_SCREENING",
            "Group ranks are conditional model-derived screening, not experimental guarantees or discovery. No validated uncertainty intervals.",
        )
    ]
    proposed = None
    model = response_id = None
    if request.mode == "REAL_LLM":
        proposed, model, response_id = model_plan or plan_with_llm(request, repository.classes())
        trace.append(
            TraceStep(
                step="parse_goal",
                outcome="REAL_LLM",
                detail=f"Validated one allowlisted screen_published_records plan from {model}.",
            )
        )
    else:
        proposed = offline_plan(request, repository.classes())
        trace.append(
            TraceStep(
                step="parse_goal",
                outcome="OFFLINE_DETERMINISTIC",
                detail="Coverage grammar accounts for every non-punctuation span; unresolved clauses fail closed.",
            )
        )
        warnings.append(
            warn(
                "BOUNDED_PARSER",
                "Bounded grammar supports explicit C/K, bulk/total, known class, formula substring and provenance. Unresolved text is rejected; inspect request_coverage.",
            )
        )
    plan = None
    candidates = []
    excluded = []
    groups = []
    matched_count = 0
    evidence_verdict = "INSUFFICIENT_EVIDENCE"
    try:
        validate_model_coverage(request.goal, proposed, repository.classes())
        plan = resolve_plan(request, proposed, repository.classes())
        matched = [
            r
            for r in repository.records
            if (not plan.row_ids or r.row_id in plan.row_ids)
            and (not plan.material_class or r.material_class == plan.material_class)
            and (not plan.formula_query or plan.formula_query.casefold() in r.formula.casefold())
        ]
        matched_count = len(matched)
        missing_ids = sorted(set(plan.row_ids) - repository.by_id.keys())
        if missing_ids:
            warnings.append(
                warn(
                    "ROWS_NOT_LOADED",
                    f"Requested rows unavailable in loaded scope: {missing_ids}. Download pinned full data.",
                )
            )
        trace.append(
            TraceStep(
                step="retrieve_records",
                outcome="REAL_PUBLISHED_DATA",
                detail=f"Matched {len(matched)} raw records from {repository.source.scope}; type filter is {plan.conductivity_type}.",
            )
        )
        eligible = defaultdict(list)
        for record in matched:
            if record.conductivity_type != plan.conductivity_type:
                metadata_warnings = [
                    warn(
                        "TYPE_NOT_COMPARABLE",
                        f"Requested {plan.conductivity_type}; source reports {record.conductivity_type}. Excluded before calculation.",
                    )
                ]
                # Inspect regime prerequisites even for incomparable rows, without computing a value.
                try:
                    select_regime(record.raw, plan.temperature_k)
                except ScienceError as exc:
                    metadata_warnings.append(warn(exc.code, str(exc)))
                excluded.append(
                    Calculation(
                        status="INSUFFICIENT_EVIDENCE",
                        row_id=record.row_id,
                        formula=record.formula,
                        source_doi=record.source_doi,
                        source_location=record.raw["Source"],
                        conductivity_type=record.conductivity_type,
                        comparison_group=group_key(record),
                        warnings=metadata_warnings,
                        next_measurement="Heuristic proposal: establish conductivity type and resolve any incomplete regime metadata from the original temperature plot before comparison.",
                        raw_source_record=record.raw,
                    )
                )
                continue
            result = calculate_record(record, plan.temperature_k, plan.allow_extrapolation)
            if result.status == "CALCULATED":
                eligible[result.comparison_group].append(result)
            else:
                excluded.append(result)
        trace.append(
            TraceStep(
                step="select_model_compute_audit",
                outcome="COMPLETED",
                detail=f"{sum(map(len, eligible.values()))} in-range calculations; {len(excluded)} excluded or unranked. Incomplete regimes and unsupported extrapolations abstain.",
            )
        )
        for key in sorted(eligible):
            values = sorted(
                eligible[key],
                key=lambda item: (
                    -item.computed_values_with_units["conductivity"].value,
                    item.row_id,
                ),
            )
            shown = values[: plan.top_n]
            for rank, value in enumerate(shown, 1):
                value.rank = rank
            first = repository.by_id[values[0].row_id]
            groups.append(
                ComparisonGroup(
                    id=key,
                    source_doi=first.source_doi,
                    conductivity_type=first.conductivity_type,
                    measurement=first.measurement,
                    temperature_range=first.temperature_range_raw,
                    eligible_count=len(values),
                    shown_count=len(shown),
                    candidate_row_ids=[v.row_id for v in shown],
                )
            )
            candidates.extend(shown)
        trace.append(
            TraceStep(
                step="rank_or_abstain",
                outcome="GROUP_RANKS_ONLY" if candidates else "INSUFFICIENT_EVIDENCE",
                detail=f"{len(groups)} comparison groups; top {plan.top_n} per exact DOI/type/technique/range. Groups sorted lexically, never by global performance. Omitted in-group tail remains counted.",
            )
        )
        if candidates:
            evidence_verdict = "SUPPORTED_CONDITIONAL_COMPARISON"
    except (PlanError, ScienceError) as exc:
        warnings.append(warn("PLAN_REJECTED", str(exc)))
        if exc.code != "PLAN_REJECTED":
            warnings.append(warn(exc.code, str(exc)))
        evidence_verdict = exc.code
        trace.append(TraceStep(step="parse_goal", outcome="INSUFFICIENT_EVIDENCE", detail=str(exc)))
    trace.append(
        TraceStep(
            step="present_result",
            outcome="AUDIT_JSON",
            detail="Includes raw source fields, row IDs, units, code fingerprint, warnings and proposed measurement advice.",
        )
    )
    return AuditReport(
        status="CALCULATED_WITH_WARNINGS" if candidates else "INSUFFICIENT_EVIDENCE",
        research_request=request,
        resolved_plan=plan,
        runtime_mode=request.mode,
        llm_model=model,
        llm_response_id=response_id,
        source=repository.source,
        inputs_with_units={"temperature": Quantity(value=plan.temperature_k, unit="K")}
        if plan
        else {},
        computed_values_with_units={
            "location": "candidates[].computed_values_with_units.conductivity",
            "unit": "S/cm",
        },
        observations_vs_calculations="The source provides experimentally derived fit parameters and citations. All displayed target-temperature conductivities are calculations. Proposed measurements are heuristics, not results.",
        code_version=code_version(),
        warnings=warnings,
        trace=trace,
        groups=groups,
        candidates=candidates,
        excluded=excluded,
        matched_count=matched_count,
        request_coverage=coverage,
        evidence_verdict=evidence_verdict,
        validated_arguments=plan.model_dump() if plan else {},
        next_scientific_actions=[
            "Proposed measurement: measure ionic conductivity and stability before, during and after exposure to the requested water-vapor fraction at the operating temperature; document exposure duration and sample preparation. No experiment was executed."
            if any(word in request.goal.lower() for word in ("humidity", "wet"))
            and evidence_verdict == "UNVERIFIED_CONSTRAINTS"
            else "Proposed action: verify original-source atmosphere, preparation, density and conductivity type; obtain evidence for every unresolved requirement before making a material recommendation. No experiment was executed."
        ],
    )
