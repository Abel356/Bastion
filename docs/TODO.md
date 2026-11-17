# Tomorrow's TODO — November 17, 2026

## 1. Persistence and corpus
- Add SQLAlchemy database sessions and application startup wiring.
- Create Postgres models for users, documents, chunks, runs, and events.
- Add Alembic migrations with pgvector enabled for Postgres.
- Generate 50–70 synthetic Acme Systems Markdown documents.
- Seed the three personas, labeled documents, chunks, and canaries.
- Prove ACL predicates execute inside the SQL candidate query.

## 2. Cohere retrieval
- Implement the environment-configured Cohere provider interface.
- Use Embed v4 search-document inputs during ingestion.
- Embed user queries with the search-query input type.
- Call Rerank 5 Fast only with ACL-authorized candidates.
- Preserve stable chunk IDs for Cohere citation sources.
- Cache embeddings and rerank results by model and corpus version.
- Provide a clearly labeled local fallback when no API key exists.
- Add provider contract and retrieval integration tests.

## 3. Agent governance
- Add search, read-document, and propose-email tools.
- Enable Cohere strict tool schemas and validate arguments locally.
- Enforce three-step, input-token, and output-token budgets.
- Scan retrieved passages for versioned injection patterns.
