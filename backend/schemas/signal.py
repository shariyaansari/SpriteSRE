from pydantic import BaseModel, Field


class FailureSignal(BaseModel):
    name: str = Field(
        ...,
        description="Identifier for the detected failure pattern.",
    )

    evidence: str = Field(
        ...,
        description="The exact piece of failure output that supports the signal.",
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence that the observed evidence matches this signal.",
    )