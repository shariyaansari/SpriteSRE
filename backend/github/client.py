# GitHubClient sdk

import httpx
from backend.config import settings
from backend.schemas.repository import Repository
from backend.schemas.file import File
from backend.schemas.workflow import Workflow


class GitHubClient:
    """An asynchronous GitHub client utilizing centralized configuration."""

    def __init__(self):
        self.github_api_url = settings.github_api_url.rstrip("/")
        self.github_token = settings.github_token

        # * Set default headers for GitHub API requests
        self.default_headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "GitHubClient",
        }
        if self.github_token:
            self.default_headers["Authorization"] = f"Bearer {self.github_token}"

        # print(f"GitHub API URL: {self.github_api_url}")

        # initialize the single AsyncClient instance
        self.client = httpx.AsyncClient(
            base_url=self.github_api_url, headers=self.default_headers
        )

    def __map_repository(self, data):
        repository = Repository(
            id=data["id"],
            name=data["name"],
            description=data.get(
                "description"
            ),  # * for optional fields, use .get() to avoid KeyError, or a brand new repo may not have a description yet
            owner=data["owner"][
                "login"
            ],  # !  # Nested GitHub JSON → flat SpriteSRE field
            private=data["private"],
            visibility=data["visibility"],
            default_branch=data["default_branch"],
            clone_url=data["clone_url"],
            language=data.get("language"),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            pushed_at=data["pushed_at"],
        )
        return repository

    def __map_repository_file(self, data: dict) -> File:
        return File(
            name=data["name"],
            path=data["path"],
            sha=data["sha"],
            size=data["size"],
            url=data["url"],
            html_url=data["html_url"],
            git_url=data["git_url"],
            download_url=data.get("download_url"),
            type=data["type"],
            content=data.get("content"),
            encoding=data.get("encoding"),
        )

    def __map_workflow(self, data) -> Workflow:
        return Workflow(
            id=data["id"],
            name=data["name"],
            path=data["path"],
            state=data["state"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            url=data["url"],
            html_url=data["html_url"],
            badge_url=data.get("badge_url"),
        )

    # generic get request method for all GitHub API endpoints
    async def __request(self, method: str, url: str, **kwargs) -> dict:
        """
        Generic request method for all GitHub API endpoints.
        """
        # * kwargs can include params, json, data, headers, etc
        response = await self.client.request(method, url, **kwargs)

        # * for debugging purposes, you can log the response status and content
        response.raise_for_status()
        return response.json()

    # get_repository(owner, repo)
    async def get_repository(self, owner: str, repo: str) -> Repository:
        """
        1. Make HTTP request
        2. Parse HTTP response
        3. Map JSON → Repository
        """
        url = f"repos/{owner}/{repo}"
        data = await self.__request("GET", url)
        return self.__map_repository(data)

    async def get_jobs(self, owner: str, repo: str, run_id: int):
        """
        Get all jobs associated with a GitHub Actions workflow run.
        """
        url = f"repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
        data = await self.__request("GET", url)
        return data["jobs"]

    def get_failed_jobs(self, jobs: list[dict]) -> list[dict]:
        return [
            job for job in jobs if job.get("conclusion") == "failure"
        ]

    def get_failed_steps(self, job: dict) -> list[dict]:
        return [
            step
            for step in job.get("steps", [])
            if step.get("conclusion") == "failure"
        ]
    
    

    async def get_contents(self, owner: str, repo: str, path: str) -> File:
        """
        Get the contents of a file in a repository.
        """
        url = f"repos/{owner}/{repo}/contents/{path}"
        data = await self.__request("GET", url)
        return self.__map_repository_file(data)

    async def get_workflows(self, owner: str, repo: str) -> list[Workflow]:
        """
        Get the workflows for a repository.
        """
        url = f"repos/{owner}/{repo}/actions/workflows"
        data = await self.__request("GET", url)
        return [self.__map_workflow(workflow) for workflow in data["workflows"]]

    async def get_logs(self, owner: str, repo: str, run_id: str):
        """
        Returns the GitHub logs endpoint response.
        GitHub returns a redirect/ZIP archive for logs.
        We'll implement binary download handling later.
        """

        url = f"repos/{owner}/{repo}/actions/runs/{run_id}/logs"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()
