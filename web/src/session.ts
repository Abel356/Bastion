import { useEffect, useState } from 'react'
import { api } from './api'
import type { Persona } from './types'

export function useDemoSession() {
  const [people, setPeople] = useState<Persona[]>([])
  const [error, setError] = useState('')
  return { people, error }
}
