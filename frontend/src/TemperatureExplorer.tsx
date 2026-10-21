import { useRef, useState } from 'react'
import { ArrowDownToLine, ArrowRight, CircleAlert, Thermometer, LoaderCircle } from 'lucide-react'
import { api, downloadReport, scientific } from './api'
import type { Catalog, DecisionPoint, Mode, TemperatureReport } from './types'

const colors = [
  '#167c78',
  '#bd6b36',
  '#596cc2',
  '#973d76',
  '#67722b',
  '#2d7fb2',
  '#a74747',
  '#4e6791',
  '#9d7825',
  '#714ab3',
  '#37754c',
  '#937455',
]

function orderText(order: number[], ties: number[][]) {
  const seen = new Set<number>()
  return order
    .flatMap((id) => {
      if (seen.has(id)) return []
      const group = ties.find((t) => t.includes(id)) ?? [id]
      group.forEach((i) => seen.add(i))
      return [order.filter((i) => group.includes(i)).join('=')]
    })
    .join(' > ')
}

function DecisionPlot({ report, point }: { report: TemperatureReport; point: DecisionPoint }) {
  const points = report.curve_points
  const low = points[0].temperature_k,
    high = points.at(-1)!.temperature_k
  const values = points.flatMap((p) => p.values.map((v) => Math.log10(v.conductivity_s_cm)))
  if (!values.length) return <p>No supported curve points.</p>
  const ymin = Math.floor(Math.min(...values)),
    ymax = Math.max(ymin + 1, Math.ceil(Math.max(...values)))
  const x = (t: number) => 80 + ((t - low) / (high - low)) * 760
  const y = (sigma: number) => 300 - ((Math.log10(sigma) - ymin) / (ymax - ymin)) * 245
  return (
    <svg
      viewBox="0 0 900 360"
      role="img"
      aria-label="Temperature-dependent conductivity curves with regime boundaries"
      className="decision-plot"
    >
      <rect x="80" y="45" width="760" height="255" fill="#f7faf9" />
      {report.materials.map((m, i) =>
        m.transition_k !== null && m.transition_k >= low && m.transition_k <= high ? (
          <g key={m.record.row_id}>
            <rect
              x={x(Math.max(low, m.transition_k - 5))}
              y="45"
              width={x(Math.min(high, m.transition_k + 5)) - x(Math.max(low, m.transition_k - 5))}
              height="255"
              fill="#d79e52"
              opacity=".13"
            />
            <line
              x1={x(m.transition_k)}
              x2={x(m.transition_k)}
              y1="45"
              y2="300"
              stroke={colors[i % colors.length]}
              strokeDasharray="4 4"
            />
            <text
              x={x(m.transition_k)}
              y={20 + (i % 3) * 11}
              textAnchor="middle"
              fontSize="10"
              fill={colors[i % colors.length]}
            >
              T* row {m.record.row_id}
            </text>
          </g>
        ) : null,
      )}
      {Array.from({ length: ymax - ymin + 1 }, (_, i) => ymin + i).map((exp) => (
        <g key={exp}>
          <line x1="80" x2="840" y1={y(10 ** exp)} y2={y(10 ** exp)} stroke="#dfe7e3" />
          <text x="68" y={y(10 ** exp) + 4} textAnchor="end" fontSize="12">
            10^{exp}
          </text>
        </g>
      ))}
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <g key={i}>
          <text x={x(low + ((high - low) * i) / 5)} y="325" textAnchor="middle" fontSize="12">
            {(low + ((high - low) * i) / 5).toFixed(0)}
          </text>
        </g>
      ))}
      <text x="460" y="351" textAnchor="middle" fontSize="13">
        Temperature · K
      </text>
      <text transform="translate(18,178) rotate(-90)" textAnchor="middle" fontSize="13">
        Model σ · S/cm · log scale
      </text>
      {report.materials.map((m, i) => {
        const paths: string[] = []
        let path = ''
        let regime = ''
        for (const p of points) {
          const v = p.values.find((v) => v.row_id === m.record.row_id)
          if (!v) {
            if (path) paths.push(path)
            path = ''
            regime = ''
            continue
          }
          if (regime && regime !== v.regime) {
            if (path) paths.push(path)
            path = ''
          }
          path += `${path ? 'L' : 'M'}${x(p.temperature_k).toFixed(2)},${y(v.conductivity_s_cm).toFixed(2)} `
          regime = v.regime
        }
        if (path) paths.push(path)
        return (
          <g key={m.record.row_id}>
            {paths.map((d, j) => (
              <path
                key={j}
                d={d}
                fill="none"
                stroke={colors[i % colors.length]}
                strokeWidth="2.6"
              />
            ))}
          </g>
        )
      })}
      {report.events
        .filter((e) => e.exact_continuous_crossing)
        .map((e, i) => (
          <g key={i}>
            <line
              x1={x(e.temperature_k)}
              x2={x(e.temperature_k)}
              y1="285"
              y2="301"
              stroke="#253b36"
            />
            <title>
              Continuous model crossing {e.row_ids.join('/')} at approximately{' '}
              {e.temperature_k.toFixed(0)} K
            </title>
          </g>
        ))}
      <line
        x1={x(point.temperature_k)}
        x2={x(point.temperature_k)}
        y1="45"
        y2="300"
        stroke="#263a36"
        strokeWidth="1.5"
      />
    </svg>
  )
}

export default function TemperatureExplorer({
  catalog,
  mode,
  onTrace,
}: {
  catalog: Catalog | null
  mode: Mode
  onTrace?: (trace: TemperatureReport['trace']) => void
}) {
  const groups =
    catalog?.comparison_groups?.filter(
      (g) => ['bulk', 'total'].includes(g.conductivity_type) && g.row_ids.length >= 2,
    ) ?? []
  const [groupId, setGroupId] = useState('')
  const selectedGroup = groups.find(
    (g) => g.id === (groupId || groups.find((g) => g.row_ids.includes(1))?.id),
  )
  const [rows, setRows] = useState([1, 2, 3])
  const [low, setLow] = useState(600),
    [high, setHigh] = useState(1100)
  const [unit, setUnit] = useState<'K' | 'C'>('K')
  const [report, setReport] = useState<TemperatureReport | null>(null)
  const [index, setIndex] = useState(0)
  const [busy, setBusy] = useState(false),
    [error, setError] = useState('')
  const sequence = useRef(0)
  async function run(flagship = false) {
    const id = ++sequence.current
    const min = flagship ? 600 : low,
      max = flagship ? 1100 : high,
      u = flagship ? 'K' : unit
    const ids = flagship ? [1, 2, 3] : rows
    const group = flagship ? groups.find((g) => g.row_ids.includes(1)) : selectedGroup
    if (flagship) {
      setLow(600)
      setHigh(1100)
      setUnit('K')
      setRows([1, 2, 3])
      setGroupId(group?.id ?? '')
    }
    setBusy(true)
    setError('')
    setReport(null)
    onTrace?.([])
    const loK = min + (u === 'C' ? 273.15 : 0),
      hiK = max + (u === 'C' ? 273.15 : 0)
    try {
      const result = await api<TemperatureReport>('/api/temperature-decisions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goal: `Compare ${group?.conductivity_type ?? 'bulk'} conductors between ${min} ${u} and ${max} ${u} with source provenance`,
          temperature_min: min,
          temperature_max: max,
          temperature_unit: u,
          row_ids: ids,
          comparison_group: group?.id,
          conductivity_type: group?.conductivity_type ?? 'bulk',
          max_materials: 12,
          evidence_policy: 'MEASURED_ONLY',
          points: 81,
          selected_temperatures: [700, 1000]
            .filter((t) => t >= loK && t <= hiK)
            .map((t) => t - (u === 'C' ? 273.15 : 0)),
          mode,
        }),
      })
      if (id !== sequence.current) return
      setReport(result)
      onTrace?.(result.trace)
      setIndex(
        Math.max(
          0,
          result.curve_points.findIndex((p) => Math.abs(p.temperature_k - 700) < 1e-6),
        ),
      )
    } catch (e) {
      if (id === sequence.current) setError(String(e))
    } finally {
      if (id === sequence.current) setBusy(false)
    }
  }
  const point = report?.curve_points[index]
  return (
    <section className="card temperature-explorer" aria-label="Temperature Decision Explorer">
      <div className="section-heading">
        <div>
          <Thermometer size={21} />
          <h2>Temperature Decision Explorer</h2>
        </div>
        <span className="demo-label">FLAGSHIP SCIENCE</span>
      </div>
      <h3>When the best material changes, see why.</h3>
      <p className="explorer-intro">
        Compare published fits across their evidence ranges. Continuous model crossings and reported
        regime transitions are audited separately.
      </p>
      <div className="explorer-controls">
        <label>
          Comparable source group
          <select
            aria-label="Decision source group"
            value={selectedGroup?.id ?? ''}
            onChange={(e) => {
              setGroupId(e.target.value)
              setRows(groups.find((g) => g.id === e.target.value)?.row_ids ?? [])
            }}
          >
            {groups.map((g) => (
              <option value={g.id} key={g.id}>
                {g.source_doi} · {g.conductivity_type} · {g.measurement} · {g.temperature_range} ·{' '}
                {g.row_ids.length} records
              </option>
            ))}
          </select>
        </label>
        <div className="interval-controls">
          <label>
            From
            <input
              aria-label="Interval minimum"
              type="number"
              value={low}
              onChange={(e) => setLow(Number(e.target.value))}
            />
          </label>
          <label>
            To
            <input
              aria-label="Interval maximum"
              type="number"
              value={high}
              onChange={(e) => setHigh(Number(e.target.value))}
            />
          </label>
          <label>
            Unit
            <select
              aria-label="Interval unit"
              value={unit}
              onChange={(e) => setUnit(e.target.value as 'K' | 'C')}
            >
              <option>K</option>
              <option value="C">°C</option>
            </select>
          </label>
          <button className="primary" disabled={busy || !catalog} onClick={() => void run()}>
            {busy ? (
              <LoaderCircle size={16} className="spin" />
            ) : (
              <>
                Analyze interval <ArrowRight size={16} />
              </>
            )}
          </button>
        </div>
      </div>
      <details className="record-selection">
        <summary>
          Select records · {rows.length} selected · maximum 12 (no silent truncation)
        </summary>
        <button onClick={() => setRows([])}>Clear selected records</button>
        <div>
          {selectedGroup?.row_ids.map((id) => (
            <label key={id}>
              <input
                type="checkbox"
                checked={rows.includes(id)}
                onChange={(e) =>
                  setRows(e.target.checked ? [...rows, id] : rows.filter((r) => r !== id))
                }
              />
              <span>
                Row {id} · {catalog?.records?.find((r) => r.row_id === id)?.formula}
              </span>
            </label>
          ))}
        </div>
      </details>
      <div className="explorer-preset">
        <button onClick={() => void run(true)} disabled={busy || !catalog}>
          Published rank reversal · rows 1 / 2 / 3
        </button>
        <span>
          {catalog?.source.row_count ?? '…'} loaded records · {mode} · measured-only
        </span>
      </div>
      {busy && (
        <p role="status">
          Intersecting evidence intervals, validating model roots and auditing boundaries…
        </p>
      )}
      {error && (
        <div role="alert" className="error">
          <CircleAlert size={18} />
          Interval analysis unavailable: {error}
        </div>
      )}
      {report && (
        <div className="decision-output">
          <p className="verdict" data-testid="crossover-qualification">
            {report.crossover_qualification} Event headings round to the nearest kelvin for
            presentation; full numerical values remain in exported JSON and technical details.
          </p>
          <div className={`verdict ${report.status === 'INSUFFICIENT_EVIDENCE' ? 'abstain' : ''}`}>
            <div>
              <strong>{report.evidence_verdicts.join(' · ').replaceAll('_', ' ')}</strong>
              <span>
                {report.source.row_count} records loaded · {report.source.scope} ·{' '}
                {report.runtime_mode} · conditional computations
              </span>
            </div>
            <button className="export" onClick={() => downloadReport(report)}>
              <ArrowDownToLine size={16} />
              Export decision JSON
            </button>
          </div>
          {!!point && (
            <>
              <div className="curve-legend">
                {report.materials.map((m, i) => (
                  <span key={m.record.row_id}>
                    <i style={{ background: colors[i % colors.length] }} />
                    Row {m.record.row_id} · {m.record.formula}
                  </span>
                ))}
              </div>
              <div className="decision-plot-wrap">
                <DecisionPlot report={report} point={point} />
              </div>
              <p className="plot-caption">
                Dashed lines: published T*. Shaded ±5 K: engineering review heuristic, not
                uncertainty. Gaps and fit boundaries are preserved. Small axis ticks mark continuous
                model crossings.
              </p>
              <div className="temperature-scrubber">
                <label htmlFor="decision-slider">
                  Explore at <strong>{point.temperature_k.toFixed(4)} K</strong> · backend-computed
                  samples
                </label>
                <input
                  id="decision-slider"
                  aria-label="Decision temperature slider"
                  type="range"
                  min="0"
                  max={report.curve_points.length - 1}
                  step="1"
                  value={index}
                  onChange={(e) => setIndex(Number(e.target.value))}
                />
                <div>
                  {[700, 1000].map((t) => {
                    const i = report.curve_points.findIndex(
                      (p) => Math.abs(p.temperature_k - t) < 1e-6,
                    )
                    return i >= 0 ? (
                      <button key={t} onClick={() => setIndex(i)}>
                        {t} K
                      </button>
                    ) : null
                  })}
                </div>
              </div>
              <div className="ordering-panel" data-testid="decision-ordering">
                <h3>Conditional ordering at {point.temperature_k.toFixed(4)} K</h3>
                <p>{point.status.replaceAll('_', ' ')} · ties explicitly marked</p>
                {point.values.map((v) => (
                  <div className="ordering-row" key={v.row_id}>
                    <span className="rank">
                      {point.ordering.length
                        ? point.values.findIndex(
                            (other) =>
                              other.row_id === v.row_id || v.tie_with.includes(other.row_id),
                          ) + 1
                        : '—'}
                    </span>
                    <strong>
                      {v.formula}
                      <small>
                        Row {v.row_id} · {v.regime}
                        {v.tie_with.length ? ` · tied with ${v.tie_with.join(', ')}` : ''}
                      </small>
                    </strong>
                    <span className="mono">{scientific(v.conductivity_s_cm)} S/cm</span>
                  </div>
                ))}
                {point.excluded.map((v) => (
                  <p className="exclusion" key={v.row_id}>
                    Row {v.row_id} withheld: {v.reasons.join(' · ')}
                  </p>
                ))}
              </div>
              <h3 className="interval-map-title">Interval decision map</h3>
              <p className="plot-caption">
                Each cell is an open interval with fixed model order; boundaries are evaluated
                separately. Hover for exact limits and all row IDs.
              </p>
              <div
                className="interval-map"
                role="img"
                aria-label="Interval-based candidate ranking map"
              >
                {report.segments.map((s, i) => (
                  <div
                    key={i}
                    style={{
                      flexGrow: s.high_k - s.low_k,
                      background: s.ordering.length
                        ? colors[
                            report.materials.findIndex((m) => m.record.row_id === s.ordering[0]) %
                              colors.length
                          ]
                        : '#8b9693',
                    }}
                    title={`${s.low_k} < T < ${s.high_k} K; order ${orderText(s.ordering, s.tie_groups) || 'insufficient'}${s.review_neighborhood ? '; T* review neighborhood' : ''}`}
                  >
                    <span>
                      {s.high_k - s.low_k > 25 ? orderText(s.ordering, s.tie_groups) : ''}
                    </span>
                  </div>
                ))}
              </div>
              <details className="interval-details">
                <summary>Exact interval limits, ordering and selected regimes</summary>
                <pre>{JSON.stringify(report.segments, null, 2)}</pre>
              </details>
            </>
          )}
          <div className="events-grid">
            {report.events.map((event, i) => (
              <article
                key={i}
                className={event.exact_continuous_crossing ? 'continuous-event' : 'regime-event'}
              >
                <span>
                  {event.exact_continuous_crossing ? 'CONTINUOUS MODEL CROSSING' : 'REGIME REVIEW'}
                </span>
                <h4>
                  ≈ {event.temperature_k.toFixed(0)} K · rows {event.row_ids.join(' / ')}
                </h4>
                <strong>{event.kind.replaceAll('_', ' ')}</strong>
                <p>{event.explanation}</p>
                <button
                  onClick={() =>
                    setIndex(
                      Math.max(
                        0,
                        report.curve_points.findIndex(
                          (p) => Math.abs(p.temperature_k - event.temperature_k) < 1e-6,
                        ),
                      ),
                    )
                  }
                >
                  Inspect this boundary
                </button>
              </article>
            ))}
          </div>
          <div className="decision-interpretation">
            <h3>Evidence interpretation & next scientific action</h3>
            {report.interpretation.map((p, i) => (
              <p key={i}>{p}</p>
            ))}
            {report.next_scientific_actions.map((p, i) => (
              <p key={i}>
                <strong>Proposed action {i + 1}.</strong> {p}
              </p>
            ))}
          </div>
          {report.warnings.map((w, i) => (
            <p className="decision-warning" key={i}>
              <strong>{w.code}</strong> {w.message}
            </p>
          ))}
          <details className="interval-details">
            <summary>Original formulas, fit parameters, validity ranges & provenance</summary>
            {report.materials.map((m) => (
              <div className="material-evidence" key={m.record.row_id}>
                <h4>
                  Row {m.record.row_id} · {m.record.formula}
                </h4>
                <a
                  href={`https://doi.org/${encodeURI(m.record.source_doi)}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  {m.record.source_doi} ↗
                </a>
                <p>
                  {m.record.reference} · {m.measured_range_k.join('–')} K · {m.excluded_reason}
                </p>
                {m.validity_intervals.map((v, i) => (
                  <p key={i}>
                    {v.regime}: {v.low_k}–{v.high_k} K; Eₐ={v.activation_energy.value} meV; A=
                    {v.prefactor.value} K S/cm. T* excluded.
                  </p>
                ))}
              </div>
            ))}
            <pre>
              {JSON.stringify(
                {
                  source: report.source,
                  code_version: report.code_version,
                  resolved_plan: report.resolved_plan,
                },
                null,
                2,
              )}
            </pre>
          </details>
        </div>
      )}
    </section>
  )
}
