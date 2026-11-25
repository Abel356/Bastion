# TODO — November 25, 2026

**Audit retrieval decisions without logging passage contents.** Record authorized candidate,
quarantine, rerank, and released-context counts plus the selected source IDs in the run
timeline. Verify the audit payload never contains document text, rejected source IDs, or
provider credentials, and surface the counts in the Security run detail.
