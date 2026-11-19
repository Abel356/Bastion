from pydantic import BaseModel, Field


class BudgetLimits(BaseModel):
    max_steps: int = Field(default=3, ge=1)
