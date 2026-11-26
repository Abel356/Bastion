# TODO — November 27, 2026

**Keep document searches available when Cohere Rerank times out.** Use at most four scanner-cleared
lexical matches on a Rerank timeout and record the timeout as the fallback reason in the Security
timeline. Verify with a simulated timeout that the run returns cited evidence and that Security can
distinguish the timeout from a malformed response. Preserve the existing handling of authorization errors.
