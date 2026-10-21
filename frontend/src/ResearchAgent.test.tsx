import { render, screen, cleanup } from '@testing-library/react'
import { afterEach, expect, it } from 'vitest'
import { ExecutionTraceView } from './ResearchAgent'
import type { ExecutionTrace } from './types'

// UI_CONTRACT_ONLY: synthetic provider identity is not a live invocation.
const trace: ExecutionTrace = {
  research_question: 'CONTRACT_TEST_ONLY question',
  runtime_mode: 'REAL_LLM',
  planning_source: 'REAL_LLM',
  model: 'SYNTHETIC_MODEL',
  response_id: 'SYNTHETIC_RESPONSE',
  tool_name: 'screen_published_records',
  tool_selection: 'MODEL_SELECTED',
  validated_arguments: { temperature_k: 873.15 },
  execution_status: 'COMPUTED',
  scientific_result: { status: 'CALCULATED_WITH_WARNINGS' },
  evidence_verdicts: ['SUPPORTED_CONDITIONAL_COMPARISON'],
  grounded_explanation: ['CONTRACT_TEST_ONLY deterministic explanation'],
  explanation_source: 'DETERMINISTIC_VALIDATED_RESULTS',
  provider_metadata: {},
}
afterEach(cleanup)
it('labels local native inference without inventing a provider response ID', () => {
  render(
    <ExecutionTraceView
      trace={{
        ...trace,
        model: 'phi4-mini:latest',
        response_id: null,
        local_invocation_id: 'SYNTHETIC_LOCAL_INVOCATION',
        provider_metadata: { provider: 'Ollama Local' },
      }}
    />,
  )
  expect(screen.getByText(/REAL_LLM — Ollama Local — phi4-mini:latest/)).toHaveTextContent(
    'Local invocation: SYNTHETIC_LOCAL_INVOCATION',
  )
  expect(screen.queryByText(/response ID unavailable/)).not.toBeInTheDocument()
})
it('renders provider identity only from a returned execution trace', () => {
  render(<ExecutionTraceView trace={trace} />)
  expect(screen.getByText(/Provider plan received/)).toHaveTextContent('SYNTHETIC_MODEL')
  expect(screen.getByText(/Provider plan received/)).toHaveTextContent('SYNTHETIC_RESPONSE')
  expect(screen.getByText('screen_published_records')).toBeInTheDocument()
  expect(screen.getByText(/Provider prose is not scientific evidence/)).toBeInTheDocument()
})
it('labels an offline execution without provider identity', () => {
  render(
    <ExecutionTraceView
      trace={{
        ...trace,
        runtime_mode: 'OFFLINE_DETERMINISTIC',
        planning_source: 'OFFLINE_DETERMINISTIC',
        model: null,
        response_id: null,
        tool_selection: 'DETERMINISTIC_SELECTED',
      }}
    />,
  )
  expect(screen.getByText(/no model call/)).toBeInTheDocument()
  expect(screen.queryByText(/Provider plan received/)).not.toBeInTheDocument()
})
