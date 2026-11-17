# PRD: Bastion — A Governed Enterprise Knowledge Agent

**Author:** Abel  
**Version:** 0.2 (lean prototype)  
**Date:** November 16, 2026  
**Status:** Ready to prototype  
**Target build:** 15 focused working days, or 4 part-time weeks

## 1. Product decision

Bastion will be a small, public, North-inspired demonstration of how to build an enterprise knowledge agent with Cohere models while enforcing access control, tool policy, cost limits, and prompt-injection defenses.

The prototype will not attempt to reproduce an enterprise agent platform. It will prove one narrow claim:

> An agent can answer from private company documents, cite its evidence, and remain inside deterministic permission, action, and budget boundaries—even when retrieved documents contain hostile instructions.

The project is designed to be:

- impressive in a three-minute product demo;
- technically credible in a ten-minute engineering walkthrough;
- runnable locally with one command;
- accessible through a stable public demo URL;
- small enough for one person to finish and polish.

## 2. Why this version should exist

The original Bastion concept was technically feasible but carried too many independent deliverables: a broad agent platform, four defense layers, multiple infrastructure services, a large red-team suite, observability, dashboards, and several tools.

This version concentrates effort on the parts most relevant to Cohere:

1. enterprise retrieval using Embed and Rerank;
2. grounded generation with fine-grained citations;
3. reliable tool use through strict schemas;
4. private-data authorization before model context is assembled;
5. measurable governance rather than a generic chat wrapper.

The result should feel adjacent to the problems North addresses without claiming to be North or copying its product surface.

## 3. Target audience

### Primary

- Cohere engineers and hiring teams evaluating applied AI, backend, ML evaluation, or solutions-engineering ability.

### Secondary

- Engineers and recruiters who want evidence of end-to-end product judgment.
- Developers who want a compact reference implementation for governed RAG.

## 4. Demo narrative

The public demo uses a fictional company named **Acme Systems** and three selectable personas. Persona selection creates a short-lived signed demo session; it is not presented as production authentication.

### Three-minute walkthrough

1. **Grounded answer:** Sign in as Maya, an Engineering employee. Ask about the incident-response policy. Bastion answers with fine-grained citations to authorized documents.
2. **Permission boundary:** Ask Maya for Finance compensation data. The retrieval trace shows that restricted chunks were excluded before reranking and before any model call.
3. **Indirect injection:** Ask a question whose best-matching document contains a planted instruction to disclose a canary and draft an external email. Bastion quarantines the suspicious passage and blocks the action.
4. **Auditability:** Switch to the Security persona and open the run timeline showing retrieved sources, policy decisions, proposed tool calls, token usage, and the final outcome.
5. **Measured result:** Open the evaluation page and compare baseline versus governed attack-success and benign-task-success rates.

### Demo fallback

The repository includes a recorded run replay and a committed evaluation report. If the hosted model quota is unavailable, the UI may replay those events only when clearly labelled **Recorded run**. It must never present cached output as a new live model response.

## 5. Goals and non-goals

### Goals

- **G1:** Demonstrate correct access-controlled retrieval with tests proving unauthorized chunks never enter model context.
- **G2:** Showcase Cohere Chat, Embed, Rerank, strict tool schemas, and citations in one coherent workflow.
- **G3:** Demonstrate a deterministic policy layer that remains authoritative over model behavior.
- **G4:** Quantify the effect of governance using a small, reproducible adversarial benchmark.
- **G5:** Provide an attractive public demo plus a one-command local setup.
- **G6:** Keep recurring hosting cost low enough to leave the project online during recruiting.

### Non-goals

- Production SSO, password authentication, SCIM, or real multi-tenancy.
- A general-purpose agent framework.
- Real email, ticketing, browsing, or other external side effects.
- Model training, fine-tuning, or a claim of complete prompt-injection prevention.
- A model-based security judge in the live request path.
- Redis, Kafka, background workers, Kubernetes, Terraform, or distributed services.
- OpenTelemetry infrastructure or a general observability product.
- A large synthetic benchmark or claims of statistical significance.
- Offline/private model deployment in v1.

## 6. Product surface

The application has three primary screens.

### 6.1 Workspace

- Persona switcher with visible department, role, and clearance.
- Chat interface with suggested demo prompts.
- Streaming answer with citation markers.
- Expandable source drawer showing document, passage, relevance score, and access label.
- Governance result card showing allowed, flagged, approval required, or blocked.
- Per-run budget meter showing steps and model tokens.

### 6.2 Audit

- List of recent runs available to the Security persona.
- Timeline for one run:
  - request received;
  - authorization scope resolved;
  - candidates filtered;
  - documents reranked;
  - suspicious content flagged;
  - model/tool calls proposed;
  - policy decision applied;
  - output released or blocked.
- Filters for persona, outcome, and defense event.

### 6.3 Evaluation

- Baseline versus governed headline metrics.
- Attack success by category.
- Benign task success.
- Median latency and tokens per run.
- Links to the generated Markdown report and raw JSON.
- Clear limitations statement.

An admin settings product surface is intentionally omitted. Demo policies live in version-controlled configuration so reviewers can inspect them.

## 7. Personas and access model

| Persona | Department | Clearance | Role | Tool rights |
|---|---|---:|---|---|
| Maya Chen | Engineering | 1 | Employee | Search, read, propose internal email |
| Jonah Reed | HR | 2 | Department lead | Search, read, propose internal email |
| Priya Shah | Security | 3 | Security reviewer | Search, read, inspect all audit events |

Each document has:

- `department`: Engineering, HR, Finance, Security, or Company;
- `clearance`: 1, 2, or 3;
- `trust_level`: internal, externally-supplied, or quarantined;
- `contains_test_payload`: evaluation metadata never shown to the model.

A user may retrieve a document only when:

```text
document.department is Company or in user.allowed_departments
AND document.clearance <= user.clearance
AND document.status = active
```

This condition is enforced inside the retrieval query before vector ranking. Post-filtering model results is not acceptable.

## 8. Functional requirements

### 8.1 Demo identity

- **FR-1:** A visitor selects one of the three fictional personas.
- **FR-2:** The server issues a signed, short-lived JWT in an HTTP-only cookie.
- **FR-3:** The UI clearly labels this as demo identity rather than production authentication.

### 8.2 Permission-aware retrieval

- **FR-4:** Ingest 50–70 synthetic Markdown documents across five departments and three clearance levels.
- **FR-5:** Chunk documents, generate Cohere embeddings, and store chunks plus ACL metadata in Postgres with pgvector.
- **FR-6:** Embed the query using the search-query input type.
- **FR-7:** Apply ACL and active-status filters in SQL before selecting the nearest 20 chunks.
- **FR-8:** Rerank the authorized candidates with Cohere Rerank and send at most four passages to the chat model.
- **FR-9:** Preserve stable document and chunk IDs so the answer can expose fine-grained citations.
- **FR-10:** Log candidate counts but never log or return unauthorized document contents to the requester.

### 8.3 Narrow agent loop

- **FR-11:** Support a maximum of three model steps per run.
- **FR-12:** Expose only three tools:
  - `search_documents(query)`;
  - `read_document(document_id)`;
  - `propose_email(recipients, subject, body)`.
- **FR-13:** Enable Cohere strict tool schemas and independently validate all arguments server-side.
- **FR-14:** `propose_email` creates only a pending synthetic action. No message is ever sent.
- **FR-15:** External recipients are always blocked in v1.
- **FR-16:** A pending internal email requires an explicit approval click before it is written to the demo outbox.

### 8.4 Governance controls

- **FR-17:** Treat retrieved passages and tool outputs as untrusted data and attach source IDs and trust labels.
- **FR-18:** Scan retrieved text for a documented, versioned set of suspicious instruction and exfiltration patterns.
- **FR-19:** Quarantine high-confidence suspicious passages before they reach the chat model and record the rule that matched.
- **FR-20:** Apply deterministic role, recipient-domain, argument, and approval policies to every proposed tool call.
- **FR-21:** Scan final output for planted canaries, restricted-document markers, external URLs, and Markdown image exfiltration.
- **FR-22:** If an output rule matches, replace the answer with a safe refusal and retain the original only in an access-restricted evaluation record.
- **FR-23:** Support exactly two evaluation modes: `baseline` and `governed`. Public guest traffic always uses `governed`; only the evaluation harness and Security demo may invoke `baseline` on synthetic data.

### 8.5 Cost and abuse controls

- **FR-24:** Limit a run to three model calls, 8,000 accumulated input tokens, and 1,000 accumulated output tokens.
- **FR-25:** Set an explicit output-token maximum on every generation call.
- **FR-26:** Enforce a small fixed-window request limit per demo session and IP using Postgres; a distributed rate limiter is unnecessary for one application instance.
- **FR-27:** Reject a call before execution when its remaining budget is insufficient.
- **FR-28:** Record model, latency, billed token metadata, and termination reason for each call.

### 8.6 Audit trail

- **FR-29:** Store an ordered event stream for every run.
- **FR-30:** Events include the actor, policy version, authorized source IDs, tool proposals, policy decisions, usage, and released response.
- **FR-31:** The application database role may insert audit events but may not update or delete them.
- **FR-32:** The project describes this as tamper-resistant at the application layer, not a compliance-grade immutable ledger.

## 9. Defense design

The runtime does not rely on the model to police itself.

### Layer 1: Authorization boundary

Unauthorized chunks are excluded in SQL. This is the strongest and most testable control in the system. The model cannot disclose text it never receives.

### Layer 2: Untrusted-content handling

Authorized retrieved content is still untrusted. Every passage is wrapped with a stable source ID and trust label. A deterministic scanner can quarantine passages containing patterns such as instruction-hierarchy overrides, requests to invoke tools, exfiltration URLs, or planted benchmark markers.

This scanner is intentionally narrow. The report must state that paraphrased or novel attacks can evade it.

