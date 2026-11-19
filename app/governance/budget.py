from pydantic import BaseModel, Field


class BudgetLimits(BaseModel):
    max_steps: int = Field(default=3, ge=1)
    max_input_tokens: int = Field(default=8000, ge=1)
    max_output_tokens: int = Field(default=1000, ge=1)


class BudgetUsage(BaseModel):
    steps: int = 0
    input_tokens: int = 0
    output_tokens: int = 0


class BudgetExceeded(RuntimeError):
    pass


class RunBudget:
    def __init__(self, limits: BudgetLimits | None = None) -> None:
        self.limits = limits or BudgetLimits()
        self.usage = BudgetUsage()

    def before_call(self, estimated_input_tokens: int = 0) -> None:
        if self.usage.steps >= self.limits.max_steps:
            raise BudgetExceeded("Agent step limit reached")
        projected = self.usage.input_tokens + estimated_input_tokens
        if projected > self.limits.max_input_tokens:
            raise BudgetExceeded("Input token budget exhausted")
        self.usage.steps += 1

    def after_call(self, input_tokens: int, output_tokens: int) -> None:
        self.usage.input_tokens += input_tokens
        self.usage.output_tokens += output_tokens
        if self.usage.input_tokens > self.limits.max_input_tokens:
            raise BudgetExceeded("Input token budget exceeded")
        if self.usage.output_tokens > self.limits.max_output_tokens:
            raise BudgetExceeded("Output token budget exceeded")

    @property
    def remaining_output_tokens(self) -> int:
        remaining = self.limits.max_output_tokens - self.usage.output_tokens
        return max(0, remaining)

    @property
    def exhausted(self) -> bool:
        return (
            self.usage.steps >= self.limits.max_steps
            or self.usage.input_tokens >= self.limits.max_input_tokens
