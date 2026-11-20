import type { Run } from './types'

export function RunResult({ run }: { run: Run }) {
  const quarantined = run.tool_results.flatMap(tool => Array.isArray(tool.data.quarantined_ids) ? tool.data.quarantined_ids : []).length
  return <section className="result" aria-live="polite">
    <h3>Run result <span className="status" data-status={run.status}>{run.status.replaceAll('_', ' ')}</span></h3>
    {run.answer && <p className="answer">{run.answer}</p>}
    {run.blocked_reason && <p>{run.blocked_reason}</p>}
    {quarantined > 0 && <p className="notice">{quarantined} suspicious {quarantined === 1 ? 'passage' : 'passages'} quarantined before generation.</p>}
    {run.status === 'approval_required' && <p>Switch to Priya Shah and open Audit to review the synthetic draft.</p>}
    {run.citations.length > 0 && <details><summary>Sources ({run.citations.length})</summary>
      <ol>{run.citations.map(citation => <li key={`${citation.start}-${citation.end}`}><p>{citation.text}</p><small>{citation.source_ids.join(', ')}</small></li>)}</ol>
    </details>}
    {run.tool_results.length > 0 && <details><summary>Tool decisions ({run.tool_results.length})</summary>
      <ul>{run.tool_results.map((tool, index) => <li key={index}>{tool.name.replaceAll('_', ' ')} · {tool.status.replaceAll('_', ' ')}</li>)}</ul>
    </details>}
    <p className="usage">{run.usage.steps}/3 model steps · {run.usage.input_tokens.toLocaleString()}/8,000 input · {run.usage.output_tokens.toLocaleString()}/1,000 output tokens</p>
  </section>
}
