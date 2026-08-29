from pydantic import BaseModel, Field


class Diagnosis(BaseModel):
    category: str = Field(
        ...,
        description="Category of the detected failure."
    )

    root_cause: str = Field(
        ...,
        description="The likely underlying cause of the failure."
    )

    explanation: str = Field(
        ...,
        description="Explanation of the evidence supporting the diagnosis."
    )

    suggested_fix: str | None = Field(
        default=None,
        description="Suggested remediation for the failure."
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in the diagnosis from 0 to 1."
    )