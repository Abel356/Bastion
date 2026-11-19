from pydantic import BaseModel, Field


class BudgetLimits(BaseModel):
    max_steps: int = Field(default=3, ge=1)
    max_input_tokens: int = Field(default=8000, ge=1)
    max_output_tokens: int = Field(default=1000, ge=1)


class BudgetUsage(BaseModel):
    steps: int = 0
    input_tokens: int = 0
    output_tokens: int = 0


