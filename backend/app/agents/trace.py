"""Compact presentation derived only from validated scientific output, never provider prose."""

from backend.app.schemas import ExecutionTrace


def execution_trace(
    result, tool_name, *, question=None, model_selected=False, provider_metadata=None
):
    evidence = tool_name == "inspect_scientific_evidence"
    if evidence:
        mode = result["runtime_mode"]
        record = result["record"]
        model = result.get("llm_model")
        response_id = result.get("llm_response_id")
        summary = {"status": result["status"], "row_id": record.row_id if record else None}
        verdicts = [result["status"]]
        explanation = [
            f"Published source row {record.row_id}, {record.formula}, DOI {record.source_doi}; fit parameters, not a new measurement."
            if record
            else "Requested source row is not loaded; no evidence was invented."
        ]
        arguments = {"row_id": result["requested_row_id"]}
        goal = question
        status = "EVIDENCE_ONLY" if record else "ABSTAINED"
    else:
        mode, model, response_id = result.runtime_mode, result.llm_model, result.llm_response_id
        goal = question if question is not None else result.research_request.goal
        arguments = result.validated_arguments
        status = "COMPUTED" if result.status == "CALCULATED_WITH_WARNINGS" else "ABSTAINED"
        if tool_name == "analyze_temperature_interval":
            verdicts = result.evidence_verdicts
            summary = {
                "status": result.status,
                "source_scope": result.source.scope,
                "selected_rankings": [
                    {"temperature_k": p.temperature_k, "ordering": p.ordering, "status": p.status}
                    for p in result.selected_rankings
                ],
                "continuous_crossings_k": [
                    e.temperature_k for e in result.events if e.exact_continuous_crossing
                ],
            }
            explanation = [*result.interpretation, result.crossover_qualification]
            explanation.extend(
                f"Row {m.record.row_id}: curated Ea={m.record.raw['Ea']} meV, EaHT={m.record.raw['EaHT'] or 'absent'} meV; source DOI {m.record.source_doi}. Prefactor ratios and regime selection also affect the order."
                for m in result.materials[:6]
            )
        else:
            verdicts = [result.evidence_verdict]
            summary = {
                "status": result.status,
                "source_scope": result.source.scope,
                "candidates": len(result.candidates),
                "comparison_groups": len(result.groups),
                "sample_calculations": [
                    {
                        "row_id": c.row_id,
                        "comparison_group": c.comparison_group,
                        "group_rank": c.rank,
                        "regime": c.regime,
                        "warning_codes": [w.code for w in c.warnings],
                        "conductivity": c.computed_values_with_units["conductivity"].model_dump(),
                        "source_doi": c.source_doi,
                    }
                    for c in result.candidates[:6]
                ],
            }
            explanation = (
                [
                    f"Calculated {len(result.candidates)} displayed candidates in {len(result.groups)} conditional source groups. There is no global ranking across experiments.",
                    result.observations_vs_calculations,
                    "Atmosphere, preparation, density and fit uncertainty are not established here; group ranks are conditional model calculations.",
                ]
                if result.candidates
                else [
                    "No complete recommendation: unresolved constraints, conflicting parameters or insufficient source evidence prevent a supported comparison."
                ]
            )
            explanation.extend(
                w.message for w in result.warnings if w.code == "NOMINAL_TEMPERATURE"
            )
            explanation.extend(
                f"Row {c.row_id}: {w.code}: {w.message}"
                for c in result.candidates
                for w in c.warnings
                if w.code in {"NEAR_TRANSITION", "TRANSITION_OUTSIDE_REPORTED_RANGE"}
            )
        if status == "ABSTAINED":
            explanation.extend(
                f"{w.code}: {w.message}"
                for w in result.warnings
                if w.code not in {"CONDITIONAL_SCREENING", "BOUNDED_PARSER"}
            )
        explanation.extend(result.next_scientific_actions)
    metadata = provider_metadata or {}
    selected = (
        (metadata.get("model_selected_tool") or tool_name)
        if mode == "REAL_LLM" and model_selected
        else None
    )
    refused = status == "ABSTAINED" and "UNVERIFIED_CONSTRAINTS" in verdicts
    return ExecutionTrace(
        research_question=goal or "Structured scientific request",
        runtime_mode=mode,
        planning_source=mode,
        model=model,
        response_id=response_id,
        local_invocation_id=metadata.get("local_invocation_id"),
        provider_metadata=metadata,
        model_selected_tool=selected,
        deterministically_expected_tool=tool_name,
        tool_agreement=selected == tool_name if selected else None,
        executed_scientific_tool=tool_name if status != "ABSTAINED" else None,
        refusal_origin=(
            "BOTH_MODEL_PLAN_AND_INDEPENDENT_VALIDATOR"
            if metadata.get("raw_model_arguments", {}).get("unsupported_constraints")
            else "INDEPENDENT_VALIDATOR"
        )
        if refused
        else None,
        tool_name=tool_name,
        tool_selection="MODEL_SELECTED"
        if model_selected and mode == "REAL_LLM"
        else "FIXED_ENDPOINT"
        if mode == "REAL_LLM"
        else "DETERMINISTIC_SELECTED",
        validated_arguments=arguments,
        execution_status=status,
        scientific_result=summary,
        evidence_verdicts=verdicts,
        grounded_explanation=explanation,
    )
