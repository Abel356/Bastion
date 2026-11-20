import type { Persona } from './types'

type Props = { people: Persona[]; select: (id: string) => void; current: string; busy: boolean }

export function Personas({ people }: { people: Persona[] }) {
  return <p>{people.length} demo personas</p>
}
