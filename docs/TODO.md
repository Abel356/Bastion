# TODO — November 23, 2026

**Account for input tokens on every offline chat step.** Use the runtime's deterministic message estimate for the offline provider's reply, tool proposal, and tool-result paths. Verify with a multi-step retrieval run that per-step model audit events sum to the reported input usage and that an insufficient cumulative budget stops the next step before execution.
