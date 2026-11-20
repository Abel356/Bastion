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
