import { Personas } from './Personas'
import { useDemoSession } from './session'

export function App() {
  const session = useDemoSession()
  return <main>
    <header><h1>Bastion</h1><Personas people={session.people} select={session.select} current={session.current?.id ?? ''} busy={session.busy} /></header>
    {session.error && <p role="alert">{session.error}</p>}
    <p>Acme Systems knowledge workspace</p>
  </main>
}
