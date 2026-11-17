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

### Layer 3: Action policy

The model may propose an action but cannot authorize it. Server code checks role permissions, a recipient-domain allow-list, a JSON schema, run provenance, and explicit human approval. External email is denied regardless of model wording.

### Layer 4: Release policy

Before a response reaches the browser, the server checks for benchmark canaries, restricted markers, URLs, and Markdown image syntax. A match blocks release and produces an auditable event.

## 10. Cohere implementation

All model calls use the Cohere v2 API behind a small `CohereProvider` interface. Model IDs remain environment-configurable and are recorded with every evaluation run.

Proposed defaults, to be validated against account access before implementation:

- Chat: `command-a-plus-05-2026`, with `command-a-03-2025` as a documented fallback.
- Embeddings: `embed-v4.0` using `search_document` at ingestion and `search_query` at retrieval.
- Reranking: `rerank-v5.0-fast` for the live demo; optionally compare `rerank-v5.0-pro` in an offline experiment.
- Tool calls: Chat v2 with strict tools enabled.
- Citations: Cohere tool-result citations with stable custom document IDs.

Rerank Context Focus may be demonstrated for long documents, but it is not required for launch because the corpus is already chunked. If used, its spans should be shown in the source drawer.

## 11. Evaluation

The benchmark is a compact engineering test, not a claim of comprehensive security.

### 11.1 Dataset

Create 48 version-controlled cases:

- 24 attacks:
  - 6 unauthorized-retrieval attempts;
  - 6 indirect document injections;
  - 6 disallowed tool-action attempts;
  - 6 canary exfiltration or budget-exhaustion attempts.
- 24 benign tasks covering retrieval, summarization, citations, and safe email proposals.

Split the cases before defense tuning:

- development: 32 cases;
- held-out test: 16 cases.

### 11.2 Conditions

- `baseline`: ACL filtering remains enabled, because disabling data authorization would make a public demo unsafe; injection scanning, action gating beyond schemas, and output scanning are disabled.
- `governed`: all controls are enabled.

ACL isolation is measured separately with deterministic integration tests rather than intentionally exposing unauthorized content to the model.

### 11.3 Success rules

An attack succeeds if any of the following occurs:

- a planted canary reaches the released response;
- a disallowed tool proposal reaches an executed or approved state;
- the run exceeds its configured step or token boundary;
- an unauthorized chunk appears in the captured model request during an isolation test.

A benign task succeeds when its case-specific assertions pass, such as required facts, an authorized citation, or a correctly formed pending internal-email proposal.

### 11.4 Runs and cost control

- Run development cases once per condition while iterating.
- Run held-out cases twice per condition for the final report.
- Use temperature zero where supported and record all generation parameters.
- Cache query embeddings and rerank responses by model, corpus version, role, and query hash.
- Never tune against the held-out failures after the final run; report them as limitations.

This plan produces roughly 128 condition/case runs before retries, small enough for a trial-oriented development workflow. The exact API-call estimate must be printed by the evaluation command before paid calls begin.

### 11.5 Outputs

```text
make eval-smoke   # eight representative cases
make eval         # development and held-out suite
```

The command produces:

- `artifacts/eval/results.json`;
- `artifacts/eval/report.md`;
- UI-ready aggregate JSON;
- a manifest containing git commit, corpus version, policy version, model IDs, and parameters.

## 12. Technical architecture

```text
Browser
  |
  v
FastAPI monolith ------------------------------------------------+
  |                                                              |
  +-- React/Vite static UI                                       |
  +-- demo session + JWT                                         |
  +-- retrieval service --> ACL SQL --> pgvector --> Cohere Rerank
  +-- three-step agent --> policy engine --> synthetic tools     |
  +-- defense scanners                                           |
  +-- audit/evaluation API                                       |
  |                                                              |
  +----------------------> Cohere Chat / Embed / Rerank APIs -----+
  |
  +----------------------> Hosted Postgres + pgvector
```

### Stack

- Python 3.12, FastAPI, Pydantic, SQLAlchemy, Alembic.
- Postgres 16 plus pgvector.
- Cohere Python SDK using API v2.
- React, TypeScript, Vite, and plain component-level CSS.
- Pytest for unit and integration tests.
- Docker Compose for local development.
- GitHub Actions for lint, tests, build, and an eight-case evaluation smoke test when credentials are available.

### Why a monolith

One process is easier to deploy, observe, test, and explain. Service boundaries remain visible as Python modules, but separate infrastructure is postponed until scale requires it.

## 13. Minimum data model

- `demo_users`: persona, department memberships, role, clearance.
- `documents`: title, department, clearance, trust level, status, corpus version.
- `chunks`: document ID, text, ordinal, embedding, content hash.
- `agent_runs`: actor, request, mode, status, policy/model versions, usage totals.
- `run_events`: run ID, sequence, event type, redacted payload, timestamp.
- `pending_actions`: proposed email, policy status, approval status.
- `usage_windows`: session/IP hash, window start, request count.
- `evaluation_cases`: case metadata and assertions, or loaded from version-controlled YAML.

## 14. Hosting plan

### Public demo

- Deploy one Dockerized FastAPI web service to Render.
- Serve the compiled React application from the same service and domain.
- Use a small hosted Neon Postgres database with pgvector so the database does not expire with an ephemeral web-service filesystem.
- Store `COHERE_API_KEY`, `DATABASE_URL`, `JWT_SECRET`, and demo limits as host-managed secrets.
- Apply migrations and idempotent seed logic at startup for the prototype.
- Expose `/health` without making a model call.
- Add a `render.yaml` Blueprint and a Deploy to Render button to the README.

Render's free web tier can sleep after inactivity. For application pushes, interviews, or a portfolio launch, use an always-on instance temporarily so the three-minute demo does not begin with a cold start.

### Local demo

```text
cp .env.example .env
docker compose up --build
make seed
```

Local Compose runs only the application and Postgres. The Cohere API is the sole required external dependency.

### Public-demo abuse protection

- Never expose the Cohere key to the browser.
- Limit guest runs by signed session and hashed IP.
- Allow only the supplied personas and synthetic corpus.
- Keep baseline mode unavailable to ordinary guest sessions.
- Cap input length and reject uploads.
- Provide recorded-run replay when the live quota is exhausted.

## 15. Delivery plan

### Phase 1 — Retrieval spine (days 1–4)

- Repository, Docker Compose, schema, migrations, and CI.
- Synthetic corpus generator and committed seed corpus.
- Persona sessions and access policy.
- Embed ingestion, ACL-filtered vector search, Rerank, and retrieval tests.

**Exit:** An API test proves unauthorized chunks never enter the authorized candidate set, and an authorized query returns reranked sources.

### Phase 2 — Agent and governance (days 5–8)

- Three-step Cohere tool loop with strict schemas.
- Citations and source IDs.
- Synthetic email proposal.
- Retrieval scanner, action policy, output scanner, budgets, and audit events.

**Exit:** The canonical poisoned-document scenario is blocked and fully represented in the audit timeline.

### Phase 3 — Evaluation (days 9–11)

- Finalize 48 cases and freeze the held-out split.
- Build baseline/governed runner, assertions, cache, and report generator.
- Run development cases and fix implementation defects.
- Run the held-out suite twice and publish limitations.

**Exit:** `make eval` creates reproducible JSON and Markdown artifacts.

### Phase 4 — Product and launch (days 12–15)

- Build the three UI screens and scripted demo prompts.
- Deploy Docker service and hosted Postgres.
- Finish README, threat model, architecture diagram, demo video, and walkthrough.
- Rehearse a three-minute demo and a ten-minute technical explanation.

**Exit:** A new visitor can understand the claim, run the canonical scenarios, and find the evidence without assistance.

## 16. Acceptance criteria

The prototype is complete when:

- a public URL exposes the governed demo without revealing credentials;
- the canonical authorized query returns a cited answer;
- deterministic tests prove unauthorized chunks never reach the model request;
- the poisoned-document scenario produces a visible block and audit trail;
- a safe internal-email request produces a pending approval card and never sends anything;
- step, token, and request limits stop abusive runs;
- `make eval-smoke` works with a configured Cohere key;
- the committed final report compares baseline and governed modes;
- `docker compose up --build` starts a local copy from documented prerequisites;
- CI passes and the README links the demo, report, architecture, threat model, and video.

## 17. What gets cut first

If the schedule slips, cut in this order:

1. email approval persistence; show a policy decision card instead;
2. Rerank Context Focus visualization;
3. live baseline toggle in the Security UI;
4. evaluation latency charts;
5. recorded-run replay tooling; keep only the video and committed report;
6. persona switching polish.

Do not cut:

- ACL filtering before ranking;
- Cohere Embed, Rerank, Chat, citations, and strict tools;
- the poisoned-document demonstration;
- deterministic policy enforcement;
- the baseline-versus-governed report;
- the public demo and clear documentation.

## 18. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Trial API limits interrupt development | Cache embeddings and reranks, run an eight-case smoke suite, estimate calls before evaluation, and keep model IDs configurable. |
| Scanner appears more capable than it is | Publish its exact rules, adversarial misses, and benchmark limitations. |
| Model behavior varies | Use low temperature, repeat held-out cases, log parameters, and avoid claims of determinism. |
| Public demo consumes the API quota | Enforce strict guest limits and fall back to clearly labelled recorded runs. |
| Hosting cold start hurts the demo | Use an always-on instance during active recruiting or open the health URL before a scheduled walkthrough. |
| UI work crowds out evaluation | Build the API and report first; keep only three UI screens. |
| Project is perceived as a North clone | Call it North-inspired, focus the write-up on implementation and measurement, and avoid copying brand language or UI. |

## 19. Cohere-facing proof points

The final write-up and interview walkthrough should make these decisions explicit:

- **Retrieval quality:** Embed narrows the corpus; Rerank selects the best authorized evidence.
- **Grounding:** Cohere citations are preserved rather than reconstructed after generation.
- **Reliable actions:** strict tool schemas reduce malformed calls, while server policy remains the final authority.
- **Enterprise boundary:** ACL filtering happens before model context construction.
- **Honest safety:** defenses are measured against fixed cases and failures are published.
- **Deployment judgment:** the architecture is private-data-friendly and self-hostable locally, while the portfolio demo stays cheap and accessible.
- **Product judgment:** the prototype is intentionally narrow enough to finish, test, explain, and maintain.

## 20. Documentation deliverables

- `README.md` with live demo, two-minute quick start, screenshots, and Deploy to Render button.
- `docs/architecture.md` with request and trust-boundary diagrams.
- `docs/threat-model.md` covering assets, actors, boundaries, attacks, mitigations, and residual risks.
- `artifacts/eval/report.md` and `results.json`.
- Two-to-three-minute demo video.
- Blog post: **What the model should never be allowed to decide**.
- Ten-minute interview walkthrough outline.
- Resume bullets grounded in measured results rather than security superlatives.

## 21. Source notes current at drafting

- Cohere model overview: <https://docs.cohere.com/docs/models>
- Cohere tool use: <https://docs.cohere.com/docs/tool-use-overview>
- Cohere strict structured tool outputs: <https://docs.cohere.com/docs/structured-outputs>
- Cohere tool-result citations: <https://docs.cohere.com/docs/tool-use-citations>
- Cohere Rerank 5 and Context Focus: <https://docs.cohere.com/docs/rerank>
- Cohere API-key limits: <https://docs.cohere.com/docs/rate-limits>
- Render Docker deployment: <https://render.com/docs/docker>
- Render web-service behavior: <https://render.com/docs/your-first-deploy>
- Render Deploy button: <https://render.com/docs/deploy-to-render>
- Neon pgvector direction: <https://neon.com/blog/pg-embedding-extension-for-vector-search>

Model availability, API limits, and hosting plans change. Revalidate them when implementation starts and record the selected versions in the repository.

