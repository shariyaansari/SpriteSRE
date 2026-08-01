from fastapi import APIRouter, HTTPException
from httpx import HTTPStatusError
from github.client import GitHubClient


router = APIRouter(
    prefix="/github",
    tags=["github"],
)

# * make an instance of the GitHubClient class to use in the FastAPI routes
# * get all the methods from the GitHubClient class
github_client = GitHubClient()


def _raise_github_http_exception(exc: HTTPStatusError, resource: str) -> None:
    response = exc.response
    try:
        detail = response.json()
    except ValueError:
        detail = response.text or f"GitHub API returned {response.status_code} for {resource}"
    raise HTTPException(status_code=response.status_code, detail=detail)


@router.get("/repositories")
async def get_repositories(owner: str, repo: str):
    try:
        return await github_client.get_repository(owner, repo)
    except HTTPStatusError as exc:
        _raise_github_http_exception(exc, "repository")


@router.get("/get_repository_content")
async def get_repository_content(owner: str, repo: str, path: str):
    try:
        return await github_client.get_contents(owner, repo, path)
    except HTTPStatusError as exc:
        _raise_github_http_exception(exc, "repository content")


@router.get("/get_workflows")
async def get_workflows(owner: str, repo: str):
    try:
        return await github_client.get_workflows(owner, repo)
    except HTTPStatusError as exc:
        _raise_github_http_exception(exc, "workflows")
