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
