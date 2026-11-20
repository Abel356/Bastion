import { useEffect, useState } from 'react'
import { api } from './api'
import type { Persona } from './types'

export function useDemoSession() {
  const [people, setPeople] = useState<Persona[]>([])
  const [error, setError] = useState('')
  const [current, setCurrent] = useState<Persona>()
  const [busy, setBusy] = useState(false)
  useEffect(() => {
    api<Persona[]>('/api/personas').then(setPeople).catch(() => setError('Could not load demo personas.'))
  }, [])
  async function select(id: string) {
    setBusy(true)
    setError('')
    await api(`/api/session/${id}`, { method: 'POST' })
  }
  return { people, error }
}
