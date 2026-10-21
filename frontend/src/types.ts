export type Mode = 'OFFLINE_DETERMINISTIC' | 'REAL_LLM'
export type ExecutionTrace = {
  local_invocation_id?: string | null
  model_selected_tool?: string | null
  deterministically_expected_tool?: string | null
  tool_agreement?: boolean | null
  executed_scientific_tool?: string | null
  refusal_origin?: string | null
  research_question: string
  runtime_mode: Mode
  planning_source: Mode
  model: string | null
  response_id: string | null
  tool_name: string
  tool_selection: string
  validated_arguments: Record<string, unknown>
  execution_status: 'COMPUTED' | 'ABSTAINED' | 'EVIDENCE_ONLY'
  scientific_result: Record<string, unknown>
  evidence_verdicts: string[]
  grounded_explanation: string[]
  explanation_source: string
  provider_metadata: Record<string, unknown>
}
export type AgentResponse = {
  runtime_mode: Mode
  tool_name: string
  validated_arguments: Record<string, unknown>
  execution_trace: ExecutionTrace
  result: unknown
}
export type Warning = { code: string; message: string }
export type Quantity = { value: number; unit: string }
export type Source = {
  dataset_doi: string
  dataset_record_id: string
  dataset_sha256: string
  loaded_sha256: string
  scope: string
  row_count: number
  license: string
  attribution: string
  accessed_date: string
}
export type Request = {
  goal: string
  temperature?: number
  temperature_unit: 'C' | 'K'
  conductivity_type: 'bulk' | 'total'
  material_class?: string
  formula_query?: string
  row_ids: number[]
  top_n: number
  allow_extrapolation: boolean
  mode: Mode
  goal_origin?: 'GENERATED' | 'MANUAL'
}
export type Calculation = {
  status: string
  row_id: number
  formula: string
  source_doi: string
  source_location: string
  conductivity_type: string
  comparison_group: string
  rank: number | null
  regime: string | null
  inputs_with_units: Record<string, Quantity>
  computed_values_with_units: Record<string, Quantity>
  warnings: Warning[]
  next_measurement: string
  raw_source_record: Record<string, string>
  observations_vs_calculations: string
}
export type Report = {
  execution_trace?: ExecutionTrace | null
  next_scientific_actions?: string[]
  status: string
  research_request: Request
  runtime_mode: Mode
  source: Source
  code_version: Record<string, string>
  resolved_plan: {
    temperature_k: number
    conductivity_type: string
    material_class: string | null
    formula_query: string | null
  } | null
  warnings: Warning[]
  candidates: Calculation[]
  excluded: Calculation[]
  matched_count: number
  groups: {
    id: string
    source_doi: string
    measurement: string
    temperature_range: string
    eligible_count: number
    shown_count: number
    candidate_row_ids: number[]
  }[]
  trace: { step: string; outcome: string; detail: string }[]
}
export type SourceGroup = {
  id: string
  source_doi: string
  conductivity_type: string
  measurement: string
  temperature_range: string
  row_ids: number[]
}
export type Catalog = {
  classes: string[]
  source: Source
  comparison_groups?: SourceGroup[]
  records?: { row_id: number; formula: string }[]
}
export type Health = { real_llm_status: string; source: Source }
export type Curve = {
  row_id: number
  points: { temperature_c: number; conductivity_s_cm: number | null; regime: string | null }[]
}
export type Adversarial = {
  demo: {
    status: string
    correct_value: Quantity
    wrong_quantity: Quantity
    numeric_ratio: Quantity
    warning: string
  }
}

export type DecisionPoint = {
  temperature_k: number
  status: string
  ordering: number[]
  values: {
    row_id: number
    formula: string
    conductivity_s_cm: number
    regime: string
    tie_with: number[]
    warning_codes: string[]
  }[]
  excluded: { row_id: number; reasons: string[] }[]
}
export type TemperatureReport = {
  execution_trace?: ExecutionTrace | null
  crossover_qualification: string
  trace: { step: string; outcome: string; detail: string }[]
  status: string
  evidence_verdicts: string[]
  runtime_mode: string
  source: Source
  comparison_group: string
  code_version: Record<string, string>
  resolved_plan: Record<string, unknown>
  warnings: Warning[]
  interpretation: string[]
  next_scientific_actions: string[]
  curve_points: DecisionPoint[]
  selected_rankings: DecisionPoint[]
  materials: {
    record: {
      row_id: number
      formula: string
      source_doi: string
      reference: string
      raw: Record<string, string>
    }
    measured_range_k: number[]
    transition_k: number | null
    excluded_reason: string | null
    validity_intervals: {
      low_k: number
      high_k: number
      regime: string
      activation_energy: Quantity
      prefactor: Quantity
    }[]
  }[]
  segments: {
    low_k: number
    high_k: number
    ordering: number[]
    regimes: Record<string, string>
    status: string
    review_neighborhood: boolean
    tie_groups: number[][]
  }[]
  events: {
    kind: string
    temperature_k: number
    row_ids: number[]
    verdict: string
    exact_continuous_crossing: boolean
    explanation: string
  }[]
}
