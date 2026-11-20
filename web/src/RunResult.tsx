import type { Run } from './types'

export function RunResult({ run }: { run: Run }) {
  return <section className="result" aria-live="polite">
    <h3>Run result <span className="status" data-status={run.status}>{run.status.replaceAll('_', ' ')}</span></h3>
    {run.answer && <p className="answer">{run.answer}</p>}
    {run.blocked_reason && <p>{run.blocked_reason}</p>}
  </section>
}
