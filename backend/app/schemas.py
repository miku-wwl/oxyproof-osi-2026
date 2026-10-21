from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, field_validator, model_validator

Mode = Literal["OFFLINE_DETERMINISTIC", "REAL_LLM"]
Verdict = Literal["CALCULATED", "EXTRAPOLATED", "INSUFFICIENT_EVIDENCE"]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, strict=True)


class ScreenRequest(Contract):
    goal: str = Field(default="Find oxygen-ion conductors at 600 °C", max_length=2000)
    temperature: FiniteFloat | None = None
    temperature_unit: Literal["C", "K"] = "C"
    conductivity_type: Literal["bulk", "total"] | None = None
    material_class: str | None = Field(default=None, max_length=100)
    formula_query: str | None = Field(default=None, max_length=120)
    row_ids: list[int] = Field(default_factory=list, max_length=50)
    allow_extrapolation: bool = False
    top_n: int = Field(default=5, ge=1, le=20)
    mode: Mode = "OFFLINE_DETERMINISTIC"
    goal_origin: Literal["GENERATED", "MANUAL"] = "MANUAL"

    @model_validator(mode="before")
    @classmethod
    def structured_only_has_no_implied_text_constraint(cls, value):
        # The legacy convenience default is 600 C only when no temperature is
        # supplied. An absent goal must never invent a conflicting requirement.
        if isinstance(value, dict) and "goal" not in value and value.get("temperature") is not None:
            return {**value, "goal": "", "goal_origin": "GENERATED"}
        return value

    @field_validator("row_ids")
    @classmethod
    def positive_rows(cls, value: list[int]) -> list[int]:
        if any(i <= 0 or i > 483 for i in value) or len(set(value)) != len(value):
            raise ValueError("row_ids must be unique integers from 1 through 483")
        return value


class GoalPlan(Contract):
    """Only a plan for an allowlisted tool; never executable code or URLs."""

    temperature: FiniteFloat | None
    temperature_unit: Literal["C", "K"]
    conductivity_type: Literal["bulk", "total"] | None
    material_class: str | None = Field(max_length=100)
    formula_query: str | None = Field(max_length=120)
    unsupported_constraints: list[str] = Field(max_length=20)


class ResolvedPlan(Contract):
    temperature_k: FiniteFloat
    conductivity_type: Literal["bulk", "total"]
    material_class: str | None
    formula_query: str | None
    row_ids: list[int]
    allow_extrapolation: bool
    top_n: int


class WarningItem(Contract):
    code: str
    message: str


class TextSpan(Contract):
    start: int
    end: int
    text: str
    field: str


class RequestCoverage(Contract):
    grammar_version: str = "2.0"
    recognized: list[TextSpan] = Field(default_factory=list)
    unresolved: list[TextSpan] = Field(default_factory=list)
    complete: bool = False


class Quantity(Contract):
    value: FiniteFloat
    unit: str


class TraceStep(Contract):
    step: str
    outcome: str
    detail: str


class Record(Contract):
    row_id: int
    formula: str
    material_class: str
    source_doi: str
    reference: str
    conductivity_type: str
    measurement: str
    temperature_range_raw: str
    raw: dict[str, str]


class Calculation(Contract):
    status: Verdict
    row_id: int
    formula: str
    source_doi: str
    source_location: str
    conductivity_type: str
    comparison_group: str
    rank: int | None = None
    regime: Literal["SINGLE", "LT", "HT"] | None = None
    inputs_with_units: dict[str, Quantity] = Field(default_factory=dict)
    computed_values_with_units: dict[str, Quantity] = Field(default_factory=dict)
    warnings: list[WarningItem] = Field(default_factory=list)
    review_required: bool = True
    trace: list[TraceStep] = Field(default_factory=list)
    observations_vs_calculations: str = (
        "Source-reported fitted parameters; model-derived conductivity, not a new measurement."
    )
    next_measurement: str
    raw_source_record: dict[str, str]


class SourceInfo(Contract):
    dataset_doi: str
    dataset_record_id: str
    dataset_sha256: str
    loaded_sha256: str
    scope: Literal["FULL_DATASET", "REAL_PUBLISHED_FIXTURE"]
    row_count: int
    license: str
    accessed_date: str
    article_url: str
    dataset_url: str
    attribution: str


class ExecutionTrace(Contract):
    research_question: str
    runtime_mode: Literal["OFFLINE_DETERMINISTIC", "REAL_LLM"]
    planning_source: Literal["OFFLINE_DETERMINISTIC", "REAL_LLM"]
    model: str | None = None
    response_id: str | None = None
    local_invocation_id: str | None = None
    model_selected_tool: str | None = None
    deterministically_expected_tool: str | None = None
    tool_agreement: bool | None = None
    executed_scientific_tool: str | None = None
    refusal_origin: str | None = None
    tool_name: str
    tool_selection: Literal["MODEL_SELECTED", "FIXED_ENDPOINT", "DETERMINISTIC_SELECTED"]
    validated_arguments: dict
    execution_status: Literal["COMPUTED", "ABSTAINED", "EVIDENCE_ONLY"]
    scientific_result: dict
    evidence_verdicts: list[str]
    grounded_explanation: list[str]
    explanation_source: Literal["DETERMINISTIC_VALIDATED_RESULTS"] = (
        "DETERMINISTIC_VALIDATED_RESULTS"
    )
    provider_metadata: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def honest_runtime_evidence(self):
        if self.planning_source != self.runtime_mode:
            raise ValueError("Planning source must match the execution runtime")
        local_identity = (
            self.provider_metadata.get("provider") == "Ollama Local"
            and self.local_invocation_id
            and self.local_invocation_id == self.provider_metadata.get("local_invocation_id")
        )
        if self.runtime_mode == "REAL_LLM" and (
            not self.model or not (self.response_id or local_identity)
        ):
            raise ValueError("Real planning trace requires model and provider response identity")
        if self.runtime_mode == "OFFLINE_DETERMINISTIC" and (
            self.model or self.response_id or self.local_invocation_id or self.provider_metadata
        ):
            raise ValueError("Offline trace cannot claim provider execution")
        if self.tool_selection == "MODEL_SELECTED" and self.runtime_mode != "REAL_LLM":
            raise ValueError("Only a provider execution can claim model-selected tools")
        return self


class ComparisonGroup(Contract):
    id: str
    source_doi: str
    conductivity_type: str
    measurement: str
    temperature_range: str
    eligible_count: int
    shown_count: int
    candidate_row_ids: list[int]


class AuditReport(Contract):
    schema_version: str = "1.0"
    execution_trace: ExecutionTrace | None = None
    status: Literal["CALCULATED_WITH_WARNINGS", "INSUFFICIENT_EVIDENCE"]
    research_request: ScreenRequest
    resolved_plan: ResolvedPlan | None
    runtime_mode: Literal["OFFLINE_DETERMINISTIC", "REAL_LLM", "UNAVAILABLE"]
    llm_model: str | None = None
    llm_response_id: str | None = None
    source: SourceInfo
    dataset_record_id: str = "18947543"
    equation: str = "sigma(T) = A/T * exp(-Ea/(k_B*T))"
    inputs_with_units: dict[str, Quantity]
    computed_values_with_units: dict[str, str]
    observations_vs_calculations: str
    code_version: dict[str, str]
    warnings: list[WarningItem]
    trace: list[TraceStep]
    review_required: bool = True
    groups: list[ComparisonGroup]
    candidates: list[Calculation]
    excluded: list[Calculation]
    matched_count: int
    request_coverage: RequestCoverage = Field(default_factory=RequestCoverage)
    evidence_verdict: str = "INSUFFICIENT_EVIDENCE"
    validated_tool: str = "screen_published_records"
    validated_arguments: dict = Field(default_factory=dict)
    next_scientific_actions: list[str] = Field(default_factory=list)
