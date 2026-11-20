import { useEffect, useState } from 'react'
import { api } from './api'

type Draft = { id: string; run_id: string; payload: { recipients: string[]; subject: string; body: string } }

export function Approvals() {
  const [drafts, setDrafts] = useState<Draft[]>([])
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  useEffect(() => { api<Draft[]>('/api/actions').then(setDrafts).catch(() => setError('Could not load approvals.')) }, [])
  async function decide(id: string, decision: 'approve' | 'reject') {
    setBusy(true)
    await api(`/api/actions/${id}/${decision}`, { method: 'POST' }).then(() => setDrafts(current => current.filter(draft => draft.id !== id)))
      .catch(() => setError('Could not save the draft decision.')).finally(() => setBusy(false))
  }
  return <section><h3>Pending approvals</h3>
    {error && <p role="alert">{error}</p>}
    {!error && drafts.length === 0 && <p>No pending drafts.</p>}
    <ul>{drafts.map(draft => <li key={draft.id}><strong>{draft.payload.subject}</strong><p>To {draft.payload.recipients.join(', ')}</p><p>{draft.payload.body}</p>
      <button disabled={busy} onClick={() => decide(draft.id, 'approve')}>Approve draft</button>{' '}
      <button disabled={busy} onClick={() => decide(draft.id, 'reject')}>Reject draft</button>
    </li>)}</ul>
  </section>
}
