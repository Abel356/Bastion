import { useEffect, useState } from 'react'
import { api } from './api'
import type { AuditRun, AuditEvent } from './types'

export function Audit() {
  const [runs, setRuns] = useState<AuditRun[]>([])
  const [error, setError] = useState('')
  const [selected, setSelected] = useState<string>()
  useEffect(() => { api<AuditRun[]>('/api/audit/runs').then(setRuns).catch(() => setError('Could not load recent runs.')) }, [])
  return <section className="audit"><h2>Security audit</h2>
    {error && <p role="alert">{error}</p>}
    {!error && runs.length === 0 && <p>No recent runs.</p>}
    <ul>{runs.map(run => <li key={run.id}><button type="button" aria-pressed={selected === run.id} onClick={() => setSelected(run.id)}>{run.user_id} · {run.status.replaceAll('_', ' ')} · {run.request}</button></li>)}</ul>
  </section>
}
