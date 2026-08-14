from datetime import datetime

from pydantic import BaseModel


class Workflow(BaseModel):
    id: int
    name: str
    path: str
    state: str
    created_at: datetime
    updated_at: datetime
    url: str
    html_url: str
    badge_url: str | None = None
