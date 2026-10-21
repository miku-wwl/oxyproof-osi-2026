import { useState } from 'react'
import { ArrowDownToLine, ArrowRight, LoaderCircle } from 'lucide-react'
import { api, downloadReport } from './api'
import type { AgentResponse, ExecutionTrace, Mode } from './types'

const questions = [
  {
    name: 'Screening question',
    goal: 'Find promising published bulk oxygen-ion conductors around 600 degrees Celsius, show their conductivity estimates, and tell me what evidence supports the comparison.',
  },
  {
    name: 'Huang interval question',
    goal: 'How does the ranking of the three comparable Huang materials change from 700 K to 1000 K? Explain the change using their published activation energies.',
  },
  {
    name: 'Humidity and lifetime question',
    goal: 'Find oxygen-ion conductors at 600 °C that survive 10% humidity and remain stable for 10,000 operating hours.',
  },
]

export function ExecutionTraceView({ trace }: { trace: ExecutionTrace }) {
  return (
    <div className="agent-execution" data-testid="agent-execution-trace">
      <div className={`verdict ${trace.execution_status === 'ABSTAINED' ? 'abstain' : ''}`}>
        <div>
          <strong>
            {trace.execution_status} · {trace.evidence_verdicts.join(' · ')}
          </strong>
          <span>
            {trace.runtime_mode} · {trace.tool_selection}
          </span>
        </div>
      </div>
      <dl className="agent-facts">
        <div>
          <dt>1 · Research question</dt>
          <dd>{trace.research_question}</dd>
        </div>
        <div>
          <dt>2 · Planning and model</dt>
          <dd>
            {trace.planning_source === 'REAL_LLM'
              ? `REAL_LLM — ${String(trace.provider_metadata.provider ?? 'Provider plan received')} — ${trace.model ?? 'model unavailable'} · ${trace.local_invocation_id ? `Local invocation: ${trace.local_invocation_id}` : (trace.response_id ?? 'response ID unavailable')}`
              : 'Offline deterministic coverage grammar · no model call'}
          </dd>
        </div>
        <div>
          <dt>3 · Scientific tool</dt>
          <dd>{trace.tool_name}</dd>
          <dd>
            Model selected: {trace.model_selected_tool ?? 'none'} · Independent expectation:{' '}
            {trace.deterministically_expected_tool ?? trace.tool_name} · Agreement:{' '}
            {trace.tool_agreement == null ? 'not applicable' : String(trace.tool_agreement)}
          </dd>
          {trace.refusal_origin && <dd>Refusal origin: {trace.refusal_origin}</dd>}
        </div>
      </dl>
      <details>
        <summary>4 · Validated tool arguments</summary>
        <pre>{JSON.stringify(trace.validated_arguments, null, 2)}</pre>
      </details>
      <details>
        <summary>5 · Scientific execution result</summary>
        <pre>{JSON.stringify(trace.scientific_result, null, 2)}</pre>
      </details>
      <p>
        <strong>6 · Evidence audit:</strong> {trace.evidence_verdicts.join(' · ')}
      </p>
      <div className="agent-explanation">
        <strong>7 · Grounded explanation</strong>
        <p className="subtle">
          Generated from validated backend results. Provider prose is not scientific evidence.
        </p>
        {trace.grounded_explanation.map((p, i) => (
          <p key={i}>{p}</p>
        ))}
      </div>
      {trace.planning_source === 'REAL_LLM' && (
        <details>
          <summary>Provider execution metadata</summary>
          <pre>{JSON.stringify(trace.provider_metadata, null, 2)}</pre>
        </details>
      )}
    </div>
  )
}

export default function ResearchAgent({
  mode,
  onModeChange,
  available,
  providerStatus,
}: {
  mode: Mode
  onModeChange: (mode: Mode) => void
  available: boolean
  providerStatus: string
}) {
  const [goal, setGoal] = useState(questions[0].goal)
  const [rows, setRows] = useState('1, 2, 3')
  const [execution, setExecution] = useState<AgentResponse | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  function clear() {
    setExecution(null)
    setError('')
  }
  async function run() {
    clear()
    const parts = rows
      .split(',')
      .map((v) => v.trim())
      .filter(Boolean)
    if (parts.some((v) => !/^\d+$/.test(v))) {
      setError('Row IDs must be comma-separated positive integers.')
      return
    }
    setBusy(true)
    try {
      const result = await api<AgentResponse>('/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal, row_ids: parts.map(Number), mode }),
      })
      setExecution(result)
    } catch (e) {
      setError(String(e))
    } finally {
      setBusy(false)
    }
  }
  return (
    <section className="card research-agent" aria-label="Research Agent execution">
      <div className="section-heading">
        <div>
          <h2>Research Agent execution</h2>
        </div>
        <span className="demo-label">BOUNDED SCIENTIFIC TOOLS</span>
      </div>
      <p>
        Ask a supported research question. The planner selects screening, interval analysis or
        source evidence inspection; independent guards control the science.
      </p>
      <div className="agent-presets">
        {questions.map((q) => (
          <button
            key={q.name}
            disabled={busy}
            onClick={() => {
              clear()
              setGoal(q.goal)
              setRows('1, 2, 3')
            }}
          >
            {q.name}
          </button>
        ))}
      </div>
      <label>
        Agent research question
        <textarea
          aria-label="Agent research question"
          maxLength={2000}
          value={goal}
          disabled={busy}
          onChange={(e) => {
            clear()
            setGoal(e.target.value)
          }}
        />
      </label>
      <div className="interval-controls">
        <label>
          Agent runtime
          <select
            aria-label="Agent runtime"
            value={mode}
            disabled={busy}
            onChange={(e) => {
              clear()
              onModeChange(e.target.value as Mode)
            }}
          >
            <option>OFFLINE_DETERMINISTIC</option>
            <option>REAL_LLM</option>
          </select>
        </label>
        <label>
          Source row IDs
          <input
            aria-label="Agent source row IDs"
            value={rows}
            disabled={busy}
            onChange={(e) => {
              clear()
              setRows(e.target.value)
            }}
          />
        </label>
        <button className="primary" disabled={busy || !available} onClick={() => void run()}>
          {busy ? (
            <LoaderCircle className="spin" size={16} />
          ) : (
            <>
              Run research agent <ArrowRight size={16} />
            </>
          )}
        </button>
      </div>
      <p className="subtle">
        Provider planning: {providerStatus}. REAL_LLM uses the explicitly configured provider when
        run. Offline mode makes no model call. Named Huang demo means rows 1–3; “around” is a
        nominal point, not an uncertainty interval.
      </p>
      {busy && (
        <p role="status">
          Validating the plan, executing the scientific tool and auditing the evidence…
        </p>
      )}
      {error && (
        <div className="error" role="alert">
          <div>
            <strong>UNAVAILABLE · no scientific result</strong>
            <p>{error}</p>
            <p>
              No offline result was substituted. Select OFFLINE_DETERMINISTIC explicitly for a
              separate run.
            </p>
          </div>
        </div>
      )}
      {execution ? (
        <>
          <button className="export" onClick={() => downloadReport(execution)}>
            <ArrowDownToLine size={16} />
            Export agent execution JSON
          </button>
          <ExecutionTraceView trace={execution.execution_trace} />
        </>
      ) : (
        !busy && !error && <p>No agent planning has run. No model execution is implied.</p>
      )}
    </section>
  )
}
