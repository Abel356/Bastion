import { useState, type FormEvent } from 'react'
import { post } from './api'
import { RunResult } from './RunResult'
import type { Run } from './types'

export function Workspace() {
  const [message, setMessage] = useState('')
  const [run, setRun] = useState<Run>()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (busy || !message.trim()) return
    setBusy(true)
    setError('')
    await post<Run>('/api/chat', { message: message.trim() }).then(setRun)
      .catch(() => setError('Could not run the request. Check your session and try again.'))
      .finally(() => setBusy(false))
  }
  return <section className="workspace"><h2>Knowledge workspace</h2>
    <form onSubmit={submit}>
      <label>Ask Bastion<textarea value={message} onChange={event => setMessage(event.target.value)} maxLength={4000} required /></label>
      <button disabled={busy || !message.trim()}>{busy ? 'Running…' : 'Run request'}</button>
    </form>
    {error && <p role="alert">{error}</p>}
  </section>
}
