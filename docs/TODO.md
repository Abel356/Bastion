# TODO — November 26, 2026

**Validate Cohere Rerank responses before selecting context.** Check that returned indices are
unique, within the submitted candidate list, and within the requested result count. On a malformed
response, use the scanner-cleared lexical order and record that fallback in the Security timeline.
Verify the behavior with a scripted provider and preserve the four-passage context cap.
