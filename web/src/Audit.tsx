import { useEffect, useState } from 'react'
import { api } from './api'
import { Approvals } from './Approvals'
import type { AuditRun, AuditEvent } from './types'

const searchMetrics = [
  ['Authorized matches', 'authorized_candidate_count'],
  ['Quarantined', 'quarantined_count'],
  ['Sent to rerank', 'rerank_candidate_count'],
  ['Selected for context', 'context_passage_count'],
] as const

function TimelineEvent({ event }: { event: AuditEvent }) {
  const { event_type, payload } = event
  const isSearch = event_type === 'tool_decision' && payload.tool === 'search_documents'
    && typeof payload.authorized_candidate_count === 'number'
  if (!isSearch) {
    return <details><summary>{event_type.replaceAll('_', ' ')}</summary>
      <pre>{JSON.stringify(payload, null, 2)}</pre>
    </details>
  }

  const sources = Array.isArray(payload.source_ids) ? payload.source_ids : []
  return <details><summary>Document search</summary>
    <dl className="search-metrics">
      {searchMetrics.map(([label, key]) => <div key={key}>
        <dt>{label}</dt><dd>{String(payload[key])}</dd>
      </div>)}
      <div><dt>Selected source IDs</dt><dd>{sources.length ? sources.join(', ') : 'None'}</dd></div>
    </dl>
  </details>
}

function Timeline({ runId }: { runId: string }) {
  const [events, setEvents] = useState<AuditEvent[]>([])
  const [error, setError] = useState('')
  useEffect(() => { api<AuditEvent[]>(`/api/audit/runs/${runId}/events`).then(setEvents).catch(() => setError('Could not load run details.')) }, [runId])
  return <section><h3>Run timeline</h3>
    {error && <p role="alert">{error}</p>}
    <ol>{events.map(event => <li key={event.sequence}><TimelineEvent event={event} /></li>)}</ol>
  </section>
}

export function Audit() {
  const [runs, setRuns] = useState<AuditRun[]>([])
  const [error, setError] = useState('')
  const [selected, setSelected] = useState<string>()
  const [revision, setRevision] = useState(0)
  useEffect(() => { api<AuditRun[]>('/api/audit/runs').then(setRuns).catch(() => setError('Could not load recent runs.')) }, [])
  return <section className="audit"><h2>Security audit</h2>
    {error && <p role="alert">{error}</p>}
    {!error && runs.length === 0 && <p>No recent runs.</p>}
    <ul>{runs.map(run => <li key={run.id}><button type="button" aria-pressed={selected === run.id} onClick={() => setSelected(run.id)}>{run.user_id} · {run.status.replaceAll('_', ' ')} · {run.request}</button></li>)}</ul>
    {selected && <Timeline key={`${selected}:${revision}`} runId={selected} />}
    <Approvals onDecision={() => setRevision(current => current + 1)} />
  </section>
}
