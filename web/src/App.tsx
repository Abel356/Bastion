import { useState } from 'react'
import { Audit } from './Audit'
import { Personas } from './Personas'
import { Workspace } from './Workspace'
import { useDemoSession } from './session'

export function App() {
  const session = useDemoSession()
  const [auditOpen, setAuditOpen] = useState(false)
  const canAudit = session.current?.role === 'security'
  return <main>
    <header><h1>Bastion</h1><Personas people={session.people} select={session.select} current={session.current?.id ?? ''} busy={session.busy} /></header>
    {session.error && <p role="alert">{session.error}</p>}
    <p className="eyebrow">Acme Systems · {session.provider === 'offline' ? 'Offline demo' : session.provider === 'cohere' ? 'Cohere' : 'Provider unavailable'}</p>
    {canAudit && <button className="audit-toggle" type="button" aria-expanded={auditOpen} onClick={() => setAuditOpen(!auditOpen)}>{auditOpen ? 'Workspace' : 'Audit'}</button>}
    {session.current && <p className="identity">{session.current.name} · {session.current.role.replaceAll('_', ' ')} · Clearance {session.current.clearance}</p>}
    {canAudit && auditOpen ? <Audit /> : session.current ? <Workspace key={session.current.id} /> : <p>Choose a demo persona to start a governed run.</p>}
  </main>
}
