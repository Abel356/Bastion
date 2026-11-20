import type { Run } from './types'

export function RunResult({ run }: { run: Run }) {
  return <section aria-live="polite"><h3>Run result</h3><p>{run.status.replaceAll('_', ' ')}</p></section>
}
