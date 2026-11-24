# TODO — November 25, 2026

**Use Cohere Rerank in the document search tool.** Send a bounded set of SQL-authorized, scanner-cleared passages to Rerank when Cohere is configured and retain lexical ranking offline. Use a scripted provider to verify the result order and confirm that unauthorized and quarantined passages never reach Rerank or the model context.
