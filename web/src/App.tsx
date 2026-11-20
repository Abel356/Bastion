import { Personas } from './Personas'
import { useDemoSession } from './session'

export function App() {
  const session = useDemoSession()
  return <main><h1>Bastion</h1><p>Acme Systems knowledge workspace</p></main>
}
