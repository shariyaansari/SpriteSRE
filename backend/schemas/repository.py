# fields I need are 
# repository_schema = {
#     "id": int,
#     "name": str,
#     "description": str,
#     "owner": str,
#     "private": bool,
#     "visibility": str,
#     "default_branch": str,
#     "clone_url": str,
#     "language": str,
#     "created_at": str,
#     "updated_at": str,
#     "pushed_at": str
# }
from pydantic import BaseModel
from datetime import datetime

class Repository(BaseModel):
    id: int
    name: str
    description: str | None = None
    owner: str
    private: bool
    visibility: str
    default_branch: str
    clone_url: str
    language: str | None = None 
    created_at: datetime
    updated_at: datetime
    pushed_at: datetime