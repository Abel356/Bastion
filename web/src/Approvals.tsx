type Draft = { id: string; run_id: string; payload: { recipients: string[]; subject: string; body: string } }

export function Approvals() {
  return <section><h3>Pending approvals</h3></section>
}
