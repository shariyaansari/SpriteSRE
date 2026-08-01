from pydantic import BaseModel

class File(BaseModel):
    name: str
    path: str
    sha: str
    size: int
    url: str
    html_url: str
    git_url: str
    download_url: str | None = None
    type: str
    content: str | None = None
    encoding: str | None = None