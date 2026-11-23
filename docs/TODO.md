# TODO — November 24, 2026

**Audit completed model calls that exceed the token budget.** Preserve the provider's reported input and output usage in a `model_call` event before recording `budget_stopped` when actual usage exceeds a limit. Use a scripted provider to verify audit order and totals and confirm the runtime stops before releasing the answer or executing a proposed tool.
