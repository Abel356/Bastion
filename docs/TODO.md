# TODO — November 22, 2026

**Make the local audit log append-only.** Install idempotent database guards for `run_events` in fresh and existing SQLite demo databases. Verify that the application can append and read events in sequence, and that direct SQL UPDATE and DELETE fail without changing existing events.
