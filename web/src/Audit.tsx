import { useEffect, useState } from 'react'
import { api } from './api'
import type { AuditRun, AuditEvent } from './types'

export function Audit() {
  return <section className="audit"><h2>Security audit</h2></section>
}
