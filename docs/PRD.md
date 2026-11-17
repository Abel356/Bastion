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
