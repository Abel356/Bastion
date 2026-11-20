import type { Persona } from './types'

type Props = { people: Persona[]; select: (id: string) => void; current: string; busy: boolean }

export function Personas({ people, select, current, busy }: Props) {
  return <label>Demo persona <select value={current} disabled={busy} onChange={event => select(event.target.value)}>{people.map(person => <option key={person.id} value={person.id}>{person.name}</option>)}</select></label>
}
