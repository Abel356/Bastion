import type { Persona } from './types'

export function Personas({ people }: { people: Persona[] }) {
  return <p>{people.length} demo personas</p>
}
