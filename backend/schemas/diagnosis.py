from pydantic import BaseModel, Field


class Diagnosis(BaseModel):
    category: str
    root_cause: str
    explanation: str
    confidence: float = Field(ge=0.0, le=1.0)
    suggested_fix: str