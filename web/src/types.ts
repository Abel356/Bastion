export type Persona = { id: string; name: string; departments: string[]; clearance: number; role: string }
export type Citation = { start: number; end: number; text: string; source_ids: string[] }
export type Run = {
  run_id: string; status: string; answer: string | null; blocked_reason: string | null
  citations: Citation[]; usage: { steps: number; input_tokens: number; output_tokens: number }
  tool_results: { name: string; status: string; data: Record<string, unknown>; source_ids: string[] }[]
}
