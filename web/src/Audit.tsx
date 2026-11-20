import { useEffect, useState } from 'react'
import { api } from './api'
import { Approvals } from './Approvals'
import type { AuditRun, AuditEvent } from './types'

function Timeline({ runId }: { runId: string }) {
  const [events, setEvents] = useState<AuditEvent[]>([])
  const [error, setError] = useState('')
  useEffect(() => { api<AuditEvent[]>(`/api/audit/runs/${runId}/events`).then(setEvents).catch(() => setError('Could not load run details.')) }, [runId])
  return <section><h3>Run timeline</h3>
    {error && <p role="alert">{error}</p>}
    <ol>{events.map(event => <li key={event.sequence}><details><summary>{event.event_type.replaceAll('_', ' ')}</summary><pre>{JSON.stringify(event.payload, null, 2)}</pre></details></li>)}</ol>
  </section>
}

export function Audit() {
  const [runs, setRuns] = useState<AuditRun[]>([])
  const [error, setError] = useState('')
  const [selected, setSelected] = useState<string>()
  useEffect(() => { api<AuditRun[]>('/api/audit/runs').then(setRuns).catch(() => setError('Could not load recent runs.')) }, [])
  return <section className="audit"><h2>Security audit</h2>
    {error && <p role="alert">{error}</p>}
    {!error && runs.length === 0 && <p>No recent runs.</p>}
    <ul>{runs.map(run => <li key={run.id}><button type="button" aria-pressed={selected === run.id} onClick={() => setSelected(run.id)}>{run.user_id} · {run.status.replaceAll('_', ' ')} · {run.request}</button></li>)}</ul>
    {selected && <Timeline key={selected} runId={selected} />}
    <Approvals />
  </section>
}
