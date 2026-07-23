from typing import Literal

from pydantic import BaseModel, Field


class AIAnalysis(BaseModel):
    summary: str
    root_cause: str
    severity: Literal["low", "medium", "high", "critical"]
    suggested_fix: str
    confidence: float = Field(ge=0.0, le=1.0)
