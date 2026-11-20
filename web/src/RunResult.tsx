import type { Run } from './types'

export function RunResult({ run }: { run: Run }) {
  return <section className="result" aria-live="polite">
    <h3>Run result <span className="status" data-status={run.status}>{run.status.replaceAll('_', ' ')}</span></h3>
    {run.answer && <p className="answer">{run.answer}</p>}
    {run.blocked_reason && <p>{run.blocked_reason}</p>}
    <p className="usage">{run.usage.steps}/3 model steps · {run.usage.input_tokens.toLocaleString()}/8,000 input · {run.usage.output_tokens.toLocaleString()}/1,000 output tokens</p>
  </section>
}
