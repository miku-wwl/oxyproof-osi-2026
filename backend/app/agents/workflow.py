"""Small allowlisted planner/executor. No model text becomes scientific evidence."""

import math
import re

from backend.app.agents.llm import LLMError, call_tools
from backend.app.agents.planner import interpret
from backend.app.agents.trace import execution_trace
from backend.app.data.ingest import Repository
from backend.app.reports.audit import code_version
from backend.app.schemas import ScreenRequest
from backend.app.science.conductivity import to_kelvin
from backend.app.science.decision_schemas import AgentRequest, TemperatureRequest
from backend.app.science.temperature_decisions import analyze_temperature_interval


def validate_interval_model(request, proposed, classes):
    parsed = interpret(request.goal, classes, interval=True)
    if proposed.unsupported_constraints or parsed.plan.unsupported_constraints:
        return False
    expected_type = parsed.plan.conductivity_type or ("bulk" if parsed.row_ids else None)
    if proposed.conductivity_type != expected_type:
        return False
    if parsed.row_ids and proposed.row_ids != parsed.row_ids:
        return False
    if proposed.row_ids is not None and sorted(proposed.row_ids) != sorted(request.row_ids):
        return False
    if parsed.interval:
        low, lu, high, hu = parsed.interval
        if proposed.temperature_min is None or proposed.temperature_max is None:
            return False
        return math.isclose(
            to_kelvin(low, lu),
            to_kelvin(proposed.temperature_min, proposed.temperature_unit),
            abs_tol=1e-6,
        ) and math.isclose(
            to_kelvin(high, hu),
            to_kelvin(proposed.temperature_max, proposed.temperature_unit),
            abs_tol=1e-6,
        )
    return proposed.temperature_min is None and proposed.temperature_max is None


def run_temperature(request: TemperatureRequest, repository: Repository):
    model = response_id = None
    telemetry = {}
    if request.mode == "REAL_LLM":
        _, proposed, model, response_id = call_tools(
            request.goal, repository.classes(), "analyze_temperature_interval", telemetry=telemetry
        )
        if not validate_interval_model(request, proposed, repository.classes()):
            # Unknown clauses are returned as typed scientific abstention; model omission
            # or invention on a covered request is a rejected integration result.
            parsed = interpret(request.goal, repository.classes(), interval=True)
            if not parsed.plan.unsupported_constraints:
                raise LLMError("MODEL_PLAN_CONFLICT: interval plan not independently supported")
    report = analyze_temperature_interval(request, repository, model=model, response_id=response_id)
    report.execution_trace.provider_metadata = telemetry
    return report


def run_research(request: AgentRequest, repository: Repository):
    evidence = re.fullmatch(
        r"\s*inspect(?: scientific)? evidence (?:for )?row (\d+)(?: with source provenance)?[.!]?\s*",
        request.goal,
        re.I,
    )
    parsed = interpret(request.goal, repository.classes(), interval=True)
    expected = (
        "inspect_scientific_evidence"
        if evidence
        else "analyze_temperature_interval"
        if parsed.interval
        else "screen_published_records"
    )
    model = response_id = None
    plan = None
    telemetry = {}
    if request.mode == "REAL_LLM":
        selected, plan, model, response_id = call_tools(
            request.goal, repository.classes(), telemetry=telemetry
        )
        if selected != expected:
            raise LLMError(
                "MODEL_TOOL_CONFLICT: selected tool disagrees with independently supported intent"
            )
    if expected == "inspect_scientific_evidence":
        row_id = int(evidence.group(1))
        if plan and (plan.row_id != row_id or plan.unsupported_constraints):
            raise LLMError("MODEL_PLAN_CONFLICT: evidence row changed or unsupported")
        record = repository.by_id.get(row_id)
        result = {
            "status": "PUBLISHED_RECORD" if record else "INSUFFICIENT_EVIDENCE",
            "record": record,
            "source": repository.source,
            "code_version": code_version(),
            "runtime_mode": request.mode,
            "llm_model": model,
            "llm_response_id": response_id,
            "requested_row_id": row_id,
        }
        arguments = {"row_id": row_id}
    elif expected == "analyze_temperature_interval":
        lo, lu, hi, hu = parsed.interval
        args = TemperatureRequest(
            goal=request.goal,
            temperature_min=to_kelvin(lo, lu),
            temperature_max=to_kelvin(hi, hu),
            temperature_unit="K",
            conductivity_type=parsed.plan.conductivity_type or "bulk",
            row_ids=request.row_ids or parsed.row_ids or [],
            mode=request.mode,
        )
        if plan and not validate_interval_model(args, plan, repository.classes()):
            if not parsed.plan.unsupported_constraints:
                raise LLMError("MODEL_PLAN_CONFLICT: interval fields changed or omitted")
        if plan and not parsed.plan.unsupported_constraints:
            # Execute accepted provider bounds/selection only after independent equality checks.
            args = args.model_copy(
                update={
                    "temperature_min": plan.temperature_min,
                    "temperature_max": plan.temperature_max,
                    "temperature_unit": plan.temperature_unit,
                    "row_ids": plan.row_ids if plan.row_ids is not None else args.row_ids,
                }
            )
        result = analyze_temperature_interval(
            args, repository, model=model, response_id=response_id
        )
        arguments = result.validated_arguments
    else:
        # Reuse audited screening with the already received model plan. A bounded
        # injected planner prevents a second call and is local to this execution.
        from backend.app.reports import audit

        args = ScreenRequest(goal=request.goal, row_ids=request.row_ids, mode=request.mode)
        result = audit.screen(
            args, repository, model_plan=(plan, model, response_id) if plan else None
        )
        arguments = result.validated_arguments
    compact = execution_trace(result, expected, question=request.goal, model_selected=True)
    compact.provider_metadata = telemetry
    if hasattr(result, "execution_trace"):
        result.execution_trace = compact
    return {
        "schema_version": "2.0",
        "runtime_mode": request.mode,
        "tool_name": expected,
        "model": model,
        "response_id": response_id,
        "validated_arguments": arguments,
        "research_question": request.goal,
        "execution_trace": compact,
        "states": [
            "INTERPRET",
            "VALIDATE_TYPED_PLAN",
            "ALLOWLIST_TOOL",
            "DETERMINISTIC_COMPUTATION",
            "INDEPENDENT_EVIDENCE_AUDIT",
            "VALIDATED_PRESENTATION",
        ],
        "result": result,
    }
