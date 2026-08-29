from pydantic import BaseModel, Field
 
 
class Signal(BaseModel):
    """
    A signal is evidence of a specific failure pattern.
    
    It is NOT a diagnosis — it's the raw pattern match.
    
    Example:
        type = "COMMAND_NOT_FOUND"
        evidence = "##[error] command not found: pytest"
    
    The signal says: "I found exit code 127."
    The diagnosis says: "The command is missing from PATH."
    """
 
    type: str = Field(
        ...,
        description="The signal type (e.g., COMMAND_NOT_FOUND, MISSING_DEPENDENCY)",
    )
    evidence: str = Field(
        ...,
        description="The actual log line or excerpt supporting this signal.",
    )