import { scientific } from './api'
import type { Calculation, Curve } from './types'

export function ComparisonPlot({
  candidates,
  selected,
  onSelect,
}: {
  candidates: Calculation[]
  selected?: number
  onSelect: (id: number) => void
}) {
  if (!candidates.length)
    return <div className="empty">No comparable in-range calculations to plot.</div>
  const max = Math.max(...candidates.map((c) => c.computed_values_with_units.conductivity.value))
  return (
    <div
      className="bars"
      role="img"
      aria-label="Calculated conductivity comparison within selected source group"
    >
      {candidates.map((c) => (
        <button
          className={`bar-row ${selected === c.row_id ? 'selected' : ''}`}
          key={c.row_id}
          onClick={() => onSelect(c.row_id)}
        >
          <span>Row {c.row_id}</span>
          <span className="bar-track">
            <span
              style={{
                width: `${Math.max(0.5, (c.computed_values_with_units.conductivity.value / max) * 100)}%`,
              }}
            />
          </span>
          <strong>{scientific(c.computed_values_with_units.conductivity.value)}</strong>
        </button>
      ))}
      <div className="axis-label">σ · S/cm · linear scale · model-derived</div>
    </div>
  )
}

export function TemperaturePlot({ curve }: { curve: Curve | null }) {
  if (!curve)
    return <div className="empty small">Select a record to inspect its temperature response.</div>
  const valid = curve.points.filter((p) => p.conductivity_s_cm !== null)
  if (!valid.length)
    return (
      <div className="empty small">
        Curve withheld: temperature or regime evidence is insufficient.
      </div>
    )
  const xMin = curve.points[0].temperature_c,
    xMax = curve.points[curve.points.length - 1].temperature_c
  const logs = valid.map((p) => Math.log10(p.conductivity_s_cm!))
  const yMin = Math.floor(Math.min(...logs)),
    yMax = Math.max(yMin + 1, Math.ceil(Math.max(...logs)))
  const x = (v: number) => 55 + ((v - xMin) / (xMax - xMin)) * 480
  const y = (v: number) => 155 - ((Math.log10(v) - yMin) / (yMax - yMin)) * 130
  // A new segment after every null or regime change; never bridge unsupported regions.
  const segments: string[] = []
  let previousRegime: string | null = null
  let open = false
  curve.points.forEach((p) => {
    if (p.conductivity_s_cm === null) {
      open = false
      return
    }
    const point = `${x(p.temperature_c)},${y(p.conductivity_s_cm)}`
    if (!open || previousRegime !== p.regime) segments.push(`M${point}`)
    else segments[segments.length - 1] += ` L${point}`
    open = true
    previousRegime = p.regime
  })
  return (
    <svg
      className="temperature-plot"
      viewBox="0 0 560 200"
      role="img"
      aria-label={`Temperature-dependent calculated conductivity for row ${curve.row_id}`}
    >
      {[0, 0.5, 1].map((r) => (
        <g key={r}>
          <line x1="55" x2="535" y1={155 - r * 130} y2={155 - r * 130} stroke="#e2e8e4" />
          <text x="47" y={159 - r * 130} textAnchor="end">
            10^{(yMin + r * (yMax - yMin)).toFixed(1)}
          </text>
        </g>
      ))}
      {[0, 0.5, 1].map((r) => (
        <text key={r} x={55 + 480 * r} y="175" textAnchor="middle">
          {(xMin + (xMax - xMin) * r).toFixed(0)} °C
        </text>
      ))}
      {segments.map((d, i) => (
        <path key={i} d={d} fill="none" stroke="#13765e" strokeWidth="2.8" />
      ))}
      <text x="55" y="13">
        σ (S/cm) · log scale · measured interval only
      </text>
    </svg>
  )
}
