"""Bounded public contracts for measured-only temperature decisions."""

from typing import Literal

from pydantic import Field, FiniteFloat, field_validator

from backend.app.schemas import (
    Contract,
    Mode,
    Quantity,
    Record,
    RequestCoverage,
    SourceInfo,
    TraceStep,
    WarningItem,
)


class IntervalGoalPlan(Contract):
    temperature_min: FiniteFloat | None
    temperature_max: FiniteFloat | None
    temperature_unit: Literal["C", "K"]
    conductivity_type: Literal["bulk", "total"] | None
    unsupported_constraints: list[str] = Field(max_length=20)


class EvidenceGoalPlan(Contract):
    row_id: int = Field(ge=1, le=483)
    unsupported_constraints: list[str] = Field(max_length=20)


class AgentRequest(Contract):
    goal: str = Field(min_length=1, max_length=2000)
    row_ids: list[int] = Field(default_factory=list, max_length=12)
    mode: Mode = "OFFLINE_DETERMINISTIC"

    @field_validator("row_ids")
    @classmethod
    def valid_rows(cls, value):
        if len(set(value)) != len(value) or any(i < 1 or i > 483 for i in value):
            raise ValueError("row_ids must be distinct published row indices 1..483")
        return value


class TemperatureRequest(Contract):
    goal: str = Field(default="", max_length=2000)
    temperature_min: FiniteFloat = 600
    temperature_max: FiniteFloat = 1100
    temperature_unit: Literal["C", "K"] = "K"
    conductivity_type: Literal["bulk", "total"] = "bulk"
    row_ids: list[int] = Field(default_factory=list, max_length=12)
    comparison_group: str | None = Field(default=None, max_length=500)
    max_materials: int = Field(default=6, ge=2, le=12)
    evidence_policy: Literal["MEASURED_ONLY"] = "MEASURED_ONLY"
    points: int = Field(default=81, ge=2, le=201)
    selected_temperatures: list[FiniteFloat] = Field(default_factory=list, max_length=20)
    mode: Mode = "OFFLINE_DETERMINISTIC"

    @field_validator("row_ids")
    @classmethod
    def rows(cls, value):
        if len(set(value)) != len(value) or any(i < 1 or i > 483 for i in value):
            raise ValueError("row_ids must be distinct published row indices 1..483")
        return value


class ValidityInterval(Contract):
    low_k: FiniteFloat
    high_k: FiniteFloat
    low_inclusive: bool = True
    high_inclusive: bool = True
    regime: Literal["SINGLE", "LT", "HT"]
    activation_energy: Quantity
    prefactor: Quantity


class MaterialEvidence(Contract):
    record: Record
    measured_range_k: list[FiniteFloat]
    transition_k: FiniteFloat | None
    validity_intervals: list[ValidityInterval]
    excluded_reason: str | None = None


class RankedValue(Contract):
    row_id: int
    formula: str
    conductivity_s_cm: FiniteFloat
    regime: str
    tie_with: list[int] = Field(default_factory=list)
    warning_codes: list[str] = Field(default_factory=list)


class PointExclusion(Contract):
    row_id: int
    reasons: list[str]


class RankingPoint(Contract):
    temperature_k: FiniteFloat
    status: Literal["SUPPORTED_CONDITIONAL_COMPARISON", "PARTIAL_EVIDENCE", "INSUFFICIENT_EVIDENCE"]
    ordering: list[int]
    values: list[RankedValue]
    excluded: list[PointExclusion]


class DecisionSegment(Contract):
    low_k: FiniteFloat
    high_k: FiniteFloat
    endpoint_policy: str = "Open interval; evaluate boundaries separately. T* is withheld."
    ordering: list[int]
    regimes: dict[str, str]
    status: str
    review_neighborhood: bool
    tie_groups: list[list[int]] = Field(default_factory=list)


class DecisionEvent(Contract):
    kind: str
    temperature_k: FiniteFloat
    row_ids: list[int]
    verdict: str
    exact_continuous_crossing: bool = False
    left_ordering: list[int] = Field(default_factory=list)
    right_ordering: list[int] = Field(default_factory=list)
    explanation: str


class RejectedCrossover(Contract):
    row_ids: list[int]
    candidate_temperature_k: FiniteFloat
    fixed_regime_overlap_k: list[FiniteFloat]
    reason: str = "Outside open joint measured and fixed-regime interval; not a supported crossing."


class TemperatureReport(Contract):
    schema_version: str = "2.0"
    status: str
    evidence_verdicts: list[str]
    research_request: TemperatureRequest
    resolved_plan: dict
    request_coverage: RequestCoverage
    runtime_mode: Literal["OFFLINE_DETERMINISTIC", "REAL_LLM", "UNAVAILABLE"]
    llm_model: str | None = None
    llm_response_id: str | None = None
    validated_tool: str = "analyze_temperature_interval"
    validated_arguments: dict
    source: SourceInfo
    code_version: dict[str, str]
    equation: str = "sigma(T) = A/T * exp(-Ea/(k_B*T))"
    crossover_qualification: str = "Model-derived crossover temperatures; uncertainty bounds unavailable; experimental confirmation required."
    ratio_equation: str = (
        "ln(sigma_i/sigma_j) = ln(A_i)-ln(A_j) - (Ea_i-Ea_j)/(1000*k_B*T); Ea in meV"
    )
    ordering_semantics: str = "Descending computed sigma, row ID breaks exact arithmetic ties. tie_with/tie_groups annotate relative 1e-10 numerical equality, not scientific uncertainty. Segment limits are open."
    units: dict[str, str] = Field(
        default_factory=lambda: {
            "temperature": "K",
            "conductivity": "S/cm",
            "activation_energy": "meV",
            "prefactor": "K S/cm",
        }
    )
    comparison_group: str | None = None
    materials: list[MaterialEvidence] = Field(default_factory=list)
    segments: list[DecisionSegment] = Field(default_factory=list)
    events: list[DecisionEvent] = Field(default_factory=list)
    rejected_crossovers: list[RejectedCrossover] = Field(default_factory=list)
    selected_rankings: list[RankingPoint] = Field(default_factory=list)
    curve_points: list[RankingPoint] = Field(default_factory=list)
    boundary_rankings: list[RankingPoint] = Field(default_factory=list)
    warnings: list[WarningItem] = Field(default_factory=list)
    trace: list[TraceStep] = Field(default_factory=list)
    interpretation: list[str] = Field(default_factory=list)
    next_scientific_actions: list[str] = Field(default_factory=list)
    review_required: bool = True
    observations_vs_calculations: str = "Published fitted parameters; all curves and rankings are model computations, not new observations. No validated uncertainty interval or stability guarantee."
