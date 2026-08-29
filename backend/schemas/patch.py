from pydantic import BaseModel, Field


class PatchEdit(BaseModel):
    """
    A single targeted edit to fix a CI/CD failure.
    
    This is intentionally simple: find → replace.
    No arbitrary operations yet (insert, delete, create_file, etc.).
    
    The LLM proposes the edit. Our code validates and applies it.
    
    Example:
        diagnosis: MISSING_DEPENDENCY (requests not installed)
        
        PatchEdit(
            file_path="requirements.txt",
            find="pytest",
            replace="pytest\nrequests",
            explanation="Add requests as a required dependency."
        )
    
    Important:
        The LLM does NOT modify the repository.
        SpriteSRE receives the edit, validates it, applies it,
        and generates a diff for the pull request.
    """

    file_path: str = Field(
        ...,
        description="Path of the file to modify (relative to repo root).",
    )

    find: str = Field(
        ...,
        description="Exact text that should be found in the file. Must match exactly once.",
    )

    replace: str = Field(
        ...,
        description="Text that should replace the matched text.",
    )

    explanation: str = Field(
        ...,
        description="Why this edit should fix the diagnosed failure.",
    )