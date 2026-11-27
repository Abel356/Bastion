# TODO — November 28, 2026

**Keep document searches available when Cohere Rerank is rate-limited.** On HTTP 429 from Rerank,
reuse the four-passage lexical fallback and show a distinct reason in the Security timeline.
Verify with mocked HTTP that the run returns cited, scanner-cleared evidence on a single Rerank
attempt and that provider authorization failures still stop the run.
