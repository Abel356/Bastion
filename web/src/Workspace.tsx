import { useState, type FormEvent } from 'react'
import { post } from './api'
import type { Run } from './types'

export function Workspace() {
  const [message, setMessage] = useState('')
  const [run, setRun] = useState<Run>()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  return <section className="workspace"><h2>Knowledge workspace</h2></section>
}
