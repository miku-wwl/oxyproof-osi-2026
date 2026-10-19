import { useEffect, useRef, useState } from 'react'
import {
  ArrowDownToLine,
  ArrowRight,
  Atom,
  Check,
  ChevronRight,
  CircleAlert,
  FileSearch,
  FlaskConical,
  Layers3,
  LoaderCircle,
  ShieldCheck,
} from 'lucide-react'
import { api, downloadReport, scientific } from './api'
import { ComparisonPlot, TemperaturePlot } from './Plots'
import type {
  Adversarial,
  Calculation,
  Catalog,
  Curve,
  Health,
  Mode,
  Report,
  Request,
} from './types'

const defaultRequest: Request = {
  goal: 'Find bulk oxygen-ion conductors at 600 °C. Show source provenance.',
  temperature: 600,
  temperature_unit: 'C',
  conductivity_type: 'bulk',
  row_ids: [1, 2, 3],
  top_n: 5,
  allow_extrapolation: false,
  mode: 'OFFLINE_DETERMINISTIC',
}
const seeds = [
  { name: '600 °C screening', request: defaultRequest },
  { name: 'Wrong-formula audit', request: { ...defaultRequest, row_ids: [1] }, adversarial: true },
  {
    name: 'Unresolved regime',
    request: {
      ...defaultRequest,
      goal: 'Screen formula Sr0.85K0.15GeO2.925 at 600 °C',
      row_ids: [462],
    },
  },
  {
    name: 'Outside measured range',
    request: { ...defaultRequest, goal: 'Screen bulk conductors at 600 °C', row_ids: [39] },
  },
]

function SourceLink({ doi, children }: { doi: string; children?: React.ReactNode }) {
  return (
    <a href={`https://doi.org/${encodeURI(doi)}`} target="_blank" rel="noreferrer">
      {children ?? doi} ↗
    </a>
  )
}

function WarningList({ warnings }: { warnings: { code: string; message: string }[] }) {
  return (
    <div className="warning-list">
      {warnings.map((w, i) => (
        <div key={`${w.code}-${i}`}>
          <CircleAlert size={14} />
          <span>
            <strong>{w.code.replaceAll('_', ' ')}</strong>
            {w.message}
          </span>
        </div>
      ))}
    </div>
  )
}

export default function App() {
  const [request, setRequest] = useState<Request>(defaultRequest)
  const [catalog, setCatalog] = useState<Catalog | null>(null)
  const [health, setHealth] = useState<Health | null>(null)
  const [report, setReport] = useState<Report | null>(null)
  const [groupId, setGroupId] = useState('')
  const [selectedId, setSelectedId] = useState<number>()
  const [curve, setCurve] = useState<Curve | null>(null)
  const [adversarial, setAdversarial] = useState<Adversarial | null>(null)
  const [showAdversarial, setShowAdversarial] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [detailError, setDetailError] = useState('')
  const [rowsInput, setRowsInput] = useState('1, 2, 3')
  const requestSequence = useRef(0)
  const detailSequence = useRef(0)

  useEffect(() => {
    Promise.all([api<Catalog>('/api/catalog'), api<Health>('/api/health')])
      .then(([c, h]) => {
        setCatalog(c)
        setHealth(h)
      })
      .catch((e) => setError(String(e)))
  }, [])

  async function run(input: Request, wrongFormula = showAdversarial) {
    const sequence = ++requestSequence.current
    setBusy(true)
    setError('')
    setDetailError('')
    setCurve(null)
    setAdversarial(null)
    setReport(null)
    setSelectedId(undefined)
    setShowAdversarial(wrongFormula)
    try {
      const result = await api<Report>('/api/screen', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input),
      })
      if (sequence !== requestSequence.current) return
      setReport(result)
      setGroupId(result.groups[0]?.id ?? '')
      setSelectedId(result.candidates[0]?.row_id ?? result.excluded[0]?.row_id)
    } catch (e) {
      if (sequence === requestSequence.current) setError(String(e))
    } finally {
      if (sequence === requestSequence.current) setBusy(false)
    }
  }

  const selected: Calculation | undefined = report
    ? [...report.candidates, ...report.excluded].find((c) => c.row_id === selectedId)
    : undefined
  const temperatureC = report?.resolved_plan ? report.resolved_plan.temperature_k - 273.15 : 600
  useEffect(() => {
    const sequence = ++detailSequence.current
    let active = true
    if (selectedId === undefined || !report) return
    // Reset when selecting a row, not when stale responses finish.
    api<Curve>(`/api/records/${selectedId}/curve`)
      .then((c) => {
        if (active && sequence === detailSequence.current) setCurve(c)
      })
      .catch((e) => {
        if (active && sequence === detailSequence.current) setDetailError(String(e))
      })
    if (selected?.status === 'CALCULATED')
      api<Adversarial>(`/api/records/${selectedId}/adversarial?temperature_c=${temperatureC}`)
        .then((a) => {
          if (active && sequence === detailSequence.current) setAdversarial(a)
        })
        .catch((e) => {
          if (active && sequence === detailSequence.current) setDetailError(String(e))
        })
    return () => {
      active = false
    }
  }, [selectedId, report, selected?.status, temperatureC])

  const group = report?.groups.find((g) => g.id === groupId)
  const visible = report?.candidates.filter((c) => c.comparison_group === groupId) ?? []
  const source = report?.source ?? catalog?.source
  function selectRow(id: number) {
    setSelectedId(id)
    setCurve(null)
    setAdversarial(null)
    setDetailError('')
  }
  function submit() {
    const parts = rowsInput
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean)
    if (parts.some((s) => !/^\d+$/.test(s))) {
      setError('Row IDs must be comma-separated positive integers.')
      return
    }
    const input = { ...request, row_ids: parts.map(Number) }
    setRequest(input)
    void run(input)
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">
            <Atom size={28} />
          </span>
          <div>
            OxyProof<span>SCIENTIFIC RESEARCH AGENT</span>
          </div>
        </div>
        <div className="sidebar-label">WORKSPACE</div>
        <div className="nav-current">
          <FlaskConical size={18} /> Research workbench <ChevronRight size={14} />
        </div>
        <div className="sidebar-label trace-title">ANALYSIS TRACE</div>
        <ol className="trace">
          {(
            report?.trace ?? [
              { step: 'parse_goal', outcome: 'READY', detail: 'Parse a bounded screening request' },
              {
                step: 'retrieve_records',
                outcome: 'READY',
                detail: 'Retrieve published source records',
              },
              {
                step: 'select_model_compute_audit',
                outcome: 'READY',
                detail: 'Select regime, calculate and audit',
              },
              {
                step: 'rank_or_abstain',
                outcome: 'READY',
                detail: 'Rank within groups or abstain',
              },
              { step: 'present_result', outcome: 'READY', detail: 'Export the evidence trail' },
            ]
          ).map((step, i) => (
            <li key={i} title={step.detail}>
              <span className={report ? 'done' : ''}>
                {report ? <Check size={12} /> : `0${i + 1}`}
              </span>
              <div>
                {step.step.replaceAll('_', ' ')}
                <small>{step.outcome.replaceAll('_', ' ')}</small>
              </div>
            </li>
          ))}
        </ol>
        <div className="sidebar-source">
          <div className="sidebar-label">PUBLISHED FOUNDATION</div>
          <strong>60 years of oxygen-ion research</strong>
          <p>
            {source
              ? `${source.row_count} loaded records · ${source.scope === 'FULL_DATASET' ? 'full pinned dataset' : 'published subset'}`
              : 'Connecting to local API…'}
          </p>
          <SourceLink doi="10.5281/zenodo.18947543">Jang et al. · Zenodo</SourceLink>
          <span>CC BY 4.0 · source-verified 20 Oct 2026</span>
        </div>
        <div className="sidebar-foot">
          <ShieldCheck size={15} /> Evidence before certainty.
        </div>
      </aside>

      <main>
        <header>
          <div className="breadcrumb">
            Workspace <ChevronRight size={13} />
            <strong>Research workbench</strong>
          </div>
          <div className="mode-badge">
            <span />
            {report?.runtime_mode ?? request.mode}
          </div>
        </header>
        <section className="intro">
          <div>
            <div className="eyebrow">OXYGEN-ION CONDUCTOR SCREENING</div>
            <h1>
              Every candidate.
              <br />
              <span>An evidence trail.</span>
            </h1>
            <p>
              Explore published oxide data, calculate conductivity,
              <br className="desktop-break" /> and see exactly where the evidence ends.
            </p>
          </div>
          <div className="intro-seal">
            <ShieldCheck size={26} />
            <span>
              Published parameters.
              <br />
              Auditable calculations.
            </span>
          </div>
        </section>

        <section className="request-card">
          <div className="section-heading">
            <div>
              <span className="section-number">01</span>
              <h2>Define your research question</h2>
            </div>
            <span className="subtle">Bounded tools · explicit units</span>
          </div>
          <label className="sr-only" htmlFor="goal">
            Research goal
          </label>
          <textarea
            id="goal"
            value={request.goal}
            onChange={(e) => setRequest({ ...request, goal: e.target.value })}
            maxLength={2000}
          />
          <div className="input-row">
            <label>
              Temperature
              <input
                type="number"
                aria-label="Temperature"
                value={request.temperature ?? ''}
                onChange={(e) =>
                  setRequest({
                    ...request,
                    temperature: e.target.value === '' ? undefined : Number(e.target.value),
                  })
                }
              />
            </label>
            <label>
              Unit
              <select
                aria-label="Temperature unit"
                value={request.temperature_unit}
                onChange={(e) =>
                  setRequest({ ...request, temperature_unit: e.target.value as 'C' | 'K' })
                }
              >
                <option value="C">°C</option>
                <option value="K">K</option>
              </select>
            </label>
            <label>
              Conductivity
              <select
                aria-label="Conductivity type"
                value={request.conductivity_type}
                onChange={(e) =>
                  setRequest({ ...request, conductivity_type: e.target.value as 'bulk' | 'total' })
                }
              >
                <option value="bulk">Bulk</option>
                <option value="total">Total</option>
              </select>
            </label>
            <label className="class-input">
              Material class
              <select
                aria-label="Material class"
                value={request.material_class ?? ''}
                onChange={(e) =>
                  setRequest({ ...request, material_class: e.target.value || undefined })
                }
              >
                <option value="">All classes</option>
                {catalog?.classes.map((c) => (
                  <option key={c}>{c}</option>
                ))}
              </select>
            </label>
            <button className="primary" onClick={submit} disabled={busy || !catalog}>
              {busy ? (
                <LoaderCircle className="spin" size={17} />
              ) : (
                <>
                  Run screening <ArrowRight size={17} />
                </>
              )}
            </button>
          </div>
          <details className="advanced">
            <summary>Structured filters & runtime</summary>
            <div className="advanced-fields">
              <label>
                Source row IDs (blank = all)
                <input
                  aria-label="Source row IDs"
                  value={rowsInput}
                  onChange={(e) => setRowsInput(e.target.value)}
                  placeholder="1, 2, 3"
                />
              </label>
              <label>
                Formula substring
                <input
                  value={request.formula_query ?? ''}
                  onChange={(e) =>
                    setRequest({ ...request, formula_query: e.target.value || undefined })
                  }
                />
              </label>
              <label>
                Runtime
                <select
                  aria-label="Runtime"
                  value={request.mode}
                  onChange={(e) => setRequest({ ...request, mode: e.target.value as Mode })}
                >
                  <option>OFFLINE_DETERMINISTIC</option>
                  <option>REAL_LLM</option>
                </select>
              </label>
              <label className="checkbox">
                <input
                  type="checkbox"
                  checked={request.allow_extrapolation}
                  onChange={(e) =>
                    setRequest({ ...request, allow_extrapolation: e.target.checked })
                  }
                />
                Allow unranked extrapolation
              </label>
            </div>
            <p>
              Live LLM: {health?.real_llm_status ?? 'checking'}. Offline rules parse C/K,
              bulk/total, class, and “formula X”; inspect the resolved plan. Goal and structured
              inputs must agree.
            </p>
          </details>
          <div className="seed-row">
            <span>TRY A WORKFLOW</span>
            {seeds.map((seed) => (
              <button
                disabled={busy || !catalog}
                key={seed.name}
                onClick={() => {
                  setRequest(seed.request)
                  setRowsInput(seed.request.row_ids.join(', '))
                  void run(seed.request, !!seed.adversarial)
                }}
              >
                {seed.name}
                <ChevronRight size={12} />
              </button>
            ))}
          </div>
        </section>

        {error && (
          <div role="alert" className="error">
            <CircleAlert size={18} />
            <div>
              <strong>Analysis unavailable</strong>
              <p>{error}</p>
              <p>
                No fallback result has been fabricated. Check the local API or select offline mode.
              </p>
            </div>
          </div>
        )}

        {!report && !busy && (
          <div className="welcome">
            <div className="welcome-icon">
              <FileSearch size={30} />
            </div>
            <h2>A useful shortlist starts with a checkable source.</h2>
            <p>
              Run the seeded screening to follow three real records from
              <br />
              published parameters to a temperature-specific comparison.
            </p>
            <span>No predictions or rankings are preloaded.</span>
          </div>
        )}
        {busy && (
          <div className="welcome" aria-live="polite">
            <LoaderCircle className="spin" size={30} />
            <h2>Checking the evidence…</h2>
            <p>Retrieve → select regime → calculate → audit → rank or abstain</p>
          </div>
        )}

        {report && (
          <>
            <div className="results-heading">
              <div>
                <div className="eyebrow">SCREENING RESULTS</div>
                <h2>
                  {report.candidates.length
                    ? 'Calculated. Cited. Conditional.'
                    : 'The evidence is insufficient.'}
                </h2>
              </div>
              <button className="export" onClick={() => downloadReport(report)}>
                <ArrowDownToLine size={16} />
                Export audit JSON
              </button>
            </div>
            <div className="metrics">
              <div>
                <span>Published records matched</span>
                <strong>
                  {report.matched_count}
                  <small> / {report.source.row_count} loaded</small>
                </strong>
              </div>
              <div>
                <span>Shown in-range calculations</span>
                <strong>
                  {report.candidates.length}
                  <small> · {report.groups.length} source groups</small>
                </strong>
              </div>
              <div>
                <span>Excluded or unranked</span>
                <strong>
                  {report.excluded.length}
                  <small> · reasons preserved</small>
                </strong>
              </div>
              <div>
                <span>Operating temperature</span>
                <strong>
                  {report.resolved_plan?.temperature_k.toFixed(2) ?? '—'}
                  <small> K</small>
                </strong>
              </div>
            </div>
            <div className={`verdict ${report.candidates.length ? '' : 'abstain'}`}>
              <ShieldCheck size={20} />
              <div>
                <strong>{report.status.replaceAll('_', ' ')}</strong>
                <span>
                  Model-derived screening · manual review required · no validated uncertainty
                  intervals
                </span>
              </div>
            </div>
            <details className="plan-details">
              <summary>Resolved plan & global warnings</summary>
              <pre>{JSON.stringify(report.resolved_plan, null, 2)}</pre>
              <WarningList warnings={report.warnings} />
            </details>

            {report.groups.length > 0 && (
              <section className="card results-card">
                <div className="section-heading">
                  <div>
                    <span className="section-number">02</span>
                    <h2>Compare within a source group</h2>
                  </div>
                  <span className="subtle">No global rank across experiments</span>
                </div>
                <label className="group-selector">
                  Source / method / measured interval
                  <select
                    aria-label="Comparison group"
                    value={groupId}
                    onChange={(e) => {
                      setGroupId(e.target.value)
                      const g = report.groups.find((g) => g.id === e.target.value)
                      if (g) selectRow(g.candidate_row_ids[0])
                    }}
                  >
                    {report.groups.map((g) => (
                      <option key={g.id} value={g.id}>
                        {g.source_doi} · {g.measurement} · {g.temperature_range}
                      </option>
                    ))}
                  </select>
                </label>
                <p className="group-note">
                  Top {group?.shown_count} of {group?.eligible_count} valid records in this
                  provisional group. Atmosphere, preparation and sample density still need
                  original-source review.
                </p>
                <div className="comparison-layout">
                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>Group rank</th>
                          <th>Published composition</th>
                          <th>σ · S/cm</th>
                          <th>Regime</th>
                        </tr>
                      </thead>
                      <tbody>
                        {visible.map((c) => (
                          <tr key={c.row_id} className={selectedId === c.row_id ? 'active' : ''}>
                            <td>
                              <span className="rank">{c.rank}</span>
                            </td>
                            <td>
                              <button
                                className="material-button"
                                onClick={() => selectRow(c.row_id)}
                              >
                                {c.formula}
                                <small>
                                  Source row {c.row_id} · {c.conductivity_type}
                                </small>
                              </button>
                            </td>
                            <td className="mono">
                              {scientific(c.computed_values_with_units.conductivity.value)}
                            </td>
                            <td>
                              <span className="regime-tag">{c.regime}</span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div className="comparison-chart">
                    <h3>Conductivity at {temperatureC.toFixed(2)} °C</h3>
                    <ComparisonPlot
                      candidates={visible}
                      selected={selectedId}
                      onSelect={selectRow}
                    />
                  </div>
                </div>
              </section>
            )}

            {report.excluded.length > 0 && (
              <details className="card excluded-card" open={report.candidates.length === 0}>
                <summary>
                  <CircleAlert size={16} />
                  {report.excluded.length} excluded / unranked records · inspect reasons
                </summary>
                <div className="excluded-list">
                  {report.excluded.map((c) => (
                    <button
                      key={c.row_id}
                      onClick={() => selectRow(c.row_id)}
                      className={selectedId === c.row_id ? 'active' : ''}
                    >
                      <strong>
                        {c.formula}
                        <small>
                          Row {c.row_id} · {c.conductivity_type}
                        </small>
                      </strong>
                      <span>{c.warnings.map((w) => w.code).join(' · ')}</span>
                      <ChevronRight size={14} />
                    </button>
                  ))}
                </div>
              </details>
            )}

            {selected && (
              <div className="detail-grid">
                <section className="card evidence-card">
                  <div className="section-heading">
                    <div>
                      <span className="section-number">03</span>
                      <h2>Inspect the evidence</h2>
                    </div>
                    <span className="row-label">ROW {selected.row_id}</span>
                  </div>
                  <h3 className="selected-formula">{selected.formula}</h3>
                  <div className="source-reference">
                    {selected.raw_source_record.Reference}
                    <SourceLink doi={selected.source_doi} />
                  </div>
                  <dl className="provenance-grid">
                    <div>
                      <dt>Source location</dt>
                      <dd>{selected.source_location}</dd>
                    </div>
                    <div>
                      <dt>Evidence type</dt>
                      <dd>Published fit parameters</dd>
                    </div>
                    <div>
                      <dt>Measured interval</dt>
                      <dd>{selected.raw_source_record.Measurement_temperature_range}</dd>
                    </div>
                    <div>
                      <dt>Method / conductivity</dt>
                      <dd>
                        {selected.raw_source_record.Measurement} / {selected.conductivity_type}
                      </dd>
                    </div>
                    {Object.entries(selected.inputs_with_units).map(([k, v]) => (
                      <div key={k}>
                        <dt>{k.replaceAll('_', ' ')}</dt>
                        <dd>
                          {v.value.toLocaleString('en-US', { maximumFractionDigits: 6 })} {v.unit}
                        </dd>
                      </div>
                    ))}
                  </dl>
                  <WarningList warnings={selected.warnings} />
                  <div className="measurement">
                    <FlaskConical size={17} />
                    <div>
                      <strong>What to measure next</strong>
                      <p>{selected.next_measurement}</p>
                    </div>
                  </div>
                  <details>
                    <summary>Exact source record & code version</summary>
                    <pre>
                      {JSON.stringify(
                        {
                          dataset: report.source,
                          raw_source_record: selected.raw_source_record,
                          code_version: report.code_version,
                        },
                        null,
                        2,
                      )}
                    </pre>
                  </details>
                </section>
                <section className="card model-card">
                  <div className="section-heading">
                    <div>
                      <Layers3 size={18} />
                      <h2>Model & temperature response</h2>
                    </div>
                  </div>
                  <div className="equation">
                    σ(T) = <span>A / T</span> · exp(−Eₐ / kᵦT)
                    <small>A in K·S/cm · Eₐ in meV → eV · T in K</small>
                  </div>
                  <TemperaturePlot curve={curve} />
                  <p className="plot-caption">
                    Only supported intervals are drawn. Curves split at regime changes; gaps are
                    preserved.
                  </p>
                  <label className="adversarial-toggle">
                    <input
                      type="checkbox"
                      checked={showAdversarial}
                      onChange={(e) => setShowAdversarial(e.target.checked)}
                    />
                    <span>Challenge the formula</span>
                    <span className="demo-label">ADVERSARIAL DEMO</span>
                  </label>
                  {showAdversarial &&
                    (adversarial ? (
                      <div className="adversarial-result">
                        <strong>
                          <CircleAlert size={16} /> REJECTED WRONG FORMULA
                        </strong>
                        <p>Reusing A without 1/T fails the unit check.</p>
                        <dl>
                          <div>
                            <dt>Correct conductivity</dt>
                            <dd>{scientific(adversarial.demo.correct_value.value)} S/cm</dd>
                          </div>
                          <div>
                            <dt>Wrong quantity · not conductivity</dt>
                            <dd>{scientific(adversarial.demo.wrong_quantity.value)} K·S/cm</dd>
                          </div>
                          <div>
                            <dt>Numeric ratio with units</dt>
                            <dd>{adversarial.demo.numeric_ratio.value.toFixed(2)} K</dd>
                          </div>
                        </dl>
                        <p>
                          Educational counterexample for this dataset convention. Original-paper
                          error is not inferred.
                        </p>
                      </div>
                    ) : (
                      <p className="empty small">
                        A valid in-range calculation is required before comparing equations.
                      </p>
                    ))}
                  {detailError && (
                    <p className="error" role="alert">
                      {detailError}
                    </p>
                  )}
                </section>
              </div>
            )}
            <details className="card full-trace">
              <summary>Complete orchestration trace</summary>
              {report.trace.map((t, i) => (
                <div key={i}>
                  <span>{i + 1}</span>
                  <p>
                    <strong>
                      {t.step} · {t.outcome}
                    </strong>
                    {t.detail}
                  </p>
                </div>
              ))}
            </details>
          </>
        )}
        <footer>
          <span>OxyProof · Scientific screening, with limits in view.</span>
          <span>
            {source?.license ?? 'CC BY 4.0'} data ·{' '}
            <SourceLink doi="10.5281/zenodo.18947543">Dataset provenance</SourceLink>
          </span>
        </footer>
      </main>
    </div>
  )
}
