import { useEffect, useState } from 'react'
import { api } from './api'

type Draft = { id: string; run_id: string; payload: { recipients: string[]; subject: string; body: string } }

export function Approvals() {
  const [drafts, setDrafts] = useState<Draft[]>([])
  const [error, setError] = useState('')
  useEffect(() => { api<Draft[]>('/api/actions').then(setDrafts).catch(() => setError('Could not load approvals.')) }, [])
  return <section><h3>Pending approvals</h3></section>
}
