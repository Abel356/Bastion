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
