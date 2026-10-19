import { fireEvent, render, screen, waitFor, cleanup } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import { ComparisonPlot, TemperaturePlot } from './Plots'
import type { Calculation, Report } from './types'

// UI_CONTRACT_TEST_ONLY. Actual API/browser integration is verified separately.
const source = {
  dataset_doi: '10.5281/zenodo.18947543',
  dataset_record_id: '18947543',
  scope: 'REAL_PUBLISHED_FIXTURE',
  row_count: 24,
  license: 'CC-BY-4.0',
}
const candidate = {
  row_id: 1,
  formula: 'CONTRACT_TEST_ONLY',
  rank: 1,
  status: 'CALCULATED',
  comparison_group: 'test-group',
  conductivity_type: 'bulk',
  regime: 'HT',
  source_doi: '10.1111/j.1151-2916.1998.tb02662.x',
  source_location: 'Table 3',
  inputs_with_units: {},
  computed_values_with_units: { conductivity: { value: 0.01234, unit: 'S/cm' } },
  warnings: [],
  raw_source_record: {
    Reference: 'CONTRACT_TEST_ONLY',
    Measurement: 'two-probe AC',
    Measurement_temperature_range: '600 - 1100 K',
  },
  next_measurement: 'CONTRACT_TEST_ONLY',
} as unknown as Calculation
const response = {
  source,
  candidates: [candidate],
  excluded: [],
  groups: [
    {
      id: 'test-group',
      source_doi: candidate.source_doi,
      measurement: 'two-probe AC',
      temperature_range: '600 - 1100 K',
      eligible_count: 1,
      shown_count: 1,
      candidate_row_ids: [1],
    },
  ],
  warnings: [],
  trace: [],
  runtime_mode: 'OFFLINE_DETERMINISTIC',
  status: 'CALCULATED_WITH_WARNINGS',
  matched_count: 1,
  resolved_plan: { temperature_k: 873.15 },
  code_version: {},
  research_request: {},
} as unknown as Report

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
})

function transport(fail = false) {
  return vi.spyOn(globalThis, 'fetch').mockImplementation(async (path) => {
    const url = String(path)
    const value =
      url === '/api/catalog'
        ? { source, classes: [] }
        : url === '/api/health'
          ? { source, real_llm_status: 'NOT_CONFIGURED' }
          : url === '/api/screen'
            ? fail
              ? { detail: 'UNAVAILABLE_CONTRACT_TEST' }
              : response
            : url.includes('/curve')
              ? { row_id: 1, points: [] }
              : {
                  demo: {
                    status: 'REJECTED_WRONG_FORMULA',
                    correct_value: { value: 0.01234 },
                    wrong_quantity: { value: 10.77 },
                    numeric_ratio: { value: 873.15 },
                  },
                }
    return new Response(JSON.stringify(value), {
      status: fail && url === '/api/screen' ? 503 : 200,
      headers: { 'Content-Type': 'application/json' },
    })
  })
}

describe('workbench API contract', () => {
  it('synchronizes generated text with temperature and type controls', async () => {
    const fetchMock = transport()
    render(<App />)
    await waitFor(() => expect(screen.getByRole('button', { name: 'Run screening' })).toBeEnabled())
    fireEvent.change(screen.getByLabelText('Temperature', { exact: true }), {
      target: { value: '700' },
    })
    fireEvent.change(screen.getByLabelText('Conductivity type'), { target: { value: 'total' } })
    expect(screen.getByLabelText('Research goal')).toHaveValue(
      'Find total oxygen-ion conductors at 700 °C. Show source provenance.',
    )
    fireEvent.click(screen.getByRole('button', { name: 'Run screening' }))
    await screen.findByText('Calculated. Cited. Conditional.')
    const call = fetchMock.mock.calls.find(([p]) => p === '/api/screen')!
    const body = JSON.parse(call[1]?.body as string)
    expect(body.temperature).toBe(700)
    expect(body.conductivity_type).toBe('total')
  })

  it('preserves a manual scientific requirement when controls change', async () => {
    transport()
    render(<App />)
    fireEvent.change(screen.getByLabelText('Research goal'), {
      target: { value: 'Find bulk conductors at 600 C that survive 10% humidity' },
    })
    fireEvent.change(screen.getByLabelText('Temperature', { exact: true }), {
      target: { value: '700' },
    })
    expect(screen.getByLabelText('Research goal')).toHaveValue(
      'Find bulk conductors at 600 C that survive 10% humidity',
    )
    expect(screen.getByTestId('goal-origin')).toHaveTextContent('Manual goal')
    fireEvent.click(screen.getByRole('button', { name: 'Use synchronized goal' }))
    expect(screen.getByLabelText('Research goal')).toHaveValue(
      'Find bulk oxygen-ion conductors at 700 °C. Show source provenance.',
    )
  })
  it('has no candidate rankings before an API screening', async () => {
    const fetchMock = transport()
    render(<App />)
    expect(screen.getByText('No predictions or rankings are preloaded.')).toBeInTheDocument()
    expect(screen.queryByText('CONTRACT_TEST_ONLY')).not.toBeInTheDocument()
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2))
    expect(
      screen.getByText('OFFLINE_DETERMINISTIC', { selector: '.mode-badge' }),
    ).toBeInTheDocument()
  })

  it('renders exactly the API value and sends the seeded typed request', async () => {
    const fetchMock = transport()
    render(<App />)
    const run = screen.getByRole('button', { name: 'Run screening' })
    await waitFor(() => expect(run).toBeEnabled())
    fireEvent.click(run)
    await screen.findByText('Calculated. Cited. Conditional.')
    expect(screen.getAllByText('1.234e-2').length).toBeGreaterThan(0)
    const call = fetchMock.mock.calls.find(([path]) => path === '/api/screen')!
    const body = JSON.parse(call[1]?.body as string)
    expect(body.row_ids).toEqual([1, 2, 3])
    expect(body.mode).toBe('OFFLINE_DETERMINISTIC')
  })

  it('surfaces API failure without candidate results', async () => {
    transport(true)
    render(<App />)
    const run = screen.getByRole('button', { name: 'Run screening' })
    await waitFor(() => expect(run).toBeEnabled())
    fireEvent.click(run)
    expect(await screen.findByRole('alert')).toHaveTextContent('UNAVAILABLE_CONTRACT_TEST')
    expect(screen.queryByText('Calculated. Cited. Conditional.')).not.toBeInTheDocument()
  })

  it('rejected regime seed renders no ranking and preserves warning', async () => {
    const mock = transport()
    mock.mockImplementation(async (path) => {
      const url = String(path)
      return new Response(
        JSON.stringify(
          url === '/api/catalog'
            ? { source, classes: [] }
            : url === '/api/health'
              ? { source, real_llm_status: 'NOT_CONFIGURED' }
              : url === '/api/screen'
                ? {
                    ...response,
                    status: 'INSUFFICIENT_EVIDENCE',
                    candidates: [],
                    groups: [],
                    excluded: [
                      {
                        ...candidate,
                        status: 'INSUFFICIENT_EVIDENCE',
                        computed_values_with_units: {},
                        warnings: [{ code: 'AMBIGUOUS_REGIME', message: 'Missing T*' }],
                      },
                    ],
                  }
                : { row_id: 1, points: [] },
        ),
        { status: 200 },
      )
    })
    render(<App />)
    const button = screen.getByRole('button', { name: /Unresolved regime/ })
    await waitFor(() => expect(button).toBeEnabled())
    fireEvent.click(button)
    expect(await screen.findByText('The evidence is insufficient.')).toBeInTheDocument()
    expect(screen.getByText('Missing T*')).toBeInTheDocument()
    expect(screen.queryByRole('table')).not.toBeInTheDocument()
  })
})

describe('plots preserve evidence boundaries', () => {
  it('uses the supplied calculation for the comparison bar', () => {
    const select = vi.fn()
    render(<ComparisonPlot candidates={[candidate]} selected={1} onSelect={select} />)
    fireEvent.click(screen.getByRole('button', { name: /Row 1/ }))
    expect(select).toHaveBeenCalledWith(1)
    expect(screen.getByText('1.234e-2')).toBeInTheDocument()
  })
  it('splits curves at gaps and regime transitions', () => {
    const { container } = render(
      <TemperaturePlot
        curve={{
          row_id: 1,
          points: [
            { temperature_c: 300, conductivity_s_cm: 0.001, regime: 'LT' },
            { temperature_c: 400, conductivity_s_cm: 0.002, regime: 'LT' },
            { temperature_c: 500, conductivity_s_cm: null, regime: null },
            { temperature_c: 600, conductivity_s_cm: 0.003, regime: 'HT' },
            { temperature_c: 700, conductivity_s_cm: 0.004, regime: 'LT' },
          ],
        }}
      />,
    )
    expect(container.querySelectorAll('path')).toHaveLength(3)
  })
})
