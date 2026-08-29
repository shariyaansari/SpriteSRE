from pydantic import BaseModel, Field


class File(BaseModel):
    """
    Represents a file in the repository.
    
    The LLM needs to know:
    1. What files exist (file_path)
    2. What's in them (content)
    
    This prevents the LLM from proposing edits to non-existent files
    or making assumptions about file structure.
    
    Example:
        File(
            path="requirements.txt",
            content="pytest==7.0.0\nblack==22.0.0"
        )
    """

    path: str = Field(
        ...,
        description="File path relative to repository root.",
    )

    content: str = Field(
        ...,
        description="The actual content of the file.",
    )