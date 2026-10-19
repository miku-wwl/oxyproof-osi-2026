export type Mode = 'OFFLINE_DETERMINISTIC' | 'REAL_LLM'
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
export type Catalog = { classes: string[]; source: Source }
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
