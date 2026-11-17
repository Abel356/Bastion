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
