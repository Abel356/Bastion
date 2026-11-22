# Progress — November 17, 2026
- Added SQLAlchemy sessions and six persistence tables.
- Enforced department, clearance, and revocation in the SQL candidate query.
- Generated and seeded 60 documents, including three labeled poisoned documents.
- Added tested Cohere and deterministic offline provider implementations.

## November 18, 2026
- Added strict schemas and validators for all three agent tools.
- Added role, recipient-domain, provenance, and approval policies.
- Added hard step, input-token, and output-token budgets.
- Added versioned injection and output-exfiltration scanners.
- Added pending-action approval and rejection persistence.
- Persisted ordered audit events and terminal run usage.
- Quarantined poisoned retrieval results before tool output.
- Next: connect these controls through the three-step agent loop.

## November 19, 2026
- Added the governed three-step agent runtime and normalized tool messages.
- Audited model calls, tool decisions, release decisions, and terminal usage.
- Added authenticated chat, approval, and security audit APIs.
- Added idempotent lifespan startup for schema, personas, and corpus.
- Verified role enforcement and approval transitions across 60 passing tests.
- Next: build the React demo shell and evaluation harness.

**November 20, 2026.** Shipped the persona workspace, cited offline retrieval, quarantine evidence, Security timelines, synthetic draft review, and an output-scanner comparison. Pushed 140 commits today (744 total). Ruff, 62 tests, the Python wheel, the frontend build, and Chrome smoke passed. Live Cohere, pgvector, and hosting remain unverified. Offline input-token reporting and database-enforced audit immutability remain open.


## November 21, 2026

- Draft approval and rejection now commit together with a Security audit event that records the reviewer, action ID, and decision. Conflicting reviews return HTTP 409. A failed audit insert rolls back the decision, and the open Security timeline refreshes after a successful review.
- Passed Ruff, all 64 pytest tests, the Vite production build, the Python wheel build, and the offline evaluation smoke. Chrome verified approval and rejection through the UI. Twenty concurrent SQLite smoke runs confirmed unique, contiguous audit sequences while reviews and regular events were written to the same run.
- Pushed 18 commits to `Abel356/Bastion` main, including this record.
- Live Cohere citations, pgvector retrieval, and PostgreSQL transaction behavior remain unverified. This workstation had no Cohere API key, PostgreSQL runtime, or container runtime. Database-enforced audit immutability remains open.

## November 22, 2026

- Bastion startup installs persistent SQLite triggers that reject direct updates and deletes on `run_events`. Existing databases gain the guards on restart and keep their audit history. Bastion also enables recursive triggers on its SQLite connections so replacement writes cannot remove an existing audit event. Other SQLite clients need `PRAGMA recursive_triggers = ON` for that replacement protection. [SQLite conflict handling](https://www.sqlite.org/lang_conflict.html)
- Passed Ruff, all 66 pytest tests, the Vite production build, the Python wheel build, and the offline evaluation smoke. A file-backed API smoke verified that Security could read the original audit event after two startups and that new runs appended ordered events. Tests also verified the SQL guards and preserved payloads on fresh and existing databases.
- Pushed 5 commits to `Abel356/Bastion` main, including this record.
- PostgreSQL audit permissions, live Cohere citations, and pgvector retrieval remain unverified. This workstation had no Cohere API key or PostgreSQL runtime.
