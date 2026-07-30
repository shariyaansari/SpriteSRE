# GitHubClient
# │
# ├── base_url
# ├── token
# ├── headers
# ├── AsyncClient
# │
# ├── get_repository()
# ├── get_workflows()
# ├── get_workflow_runs()
# ├── get_jobs()
# ├── get_logs()
# └── create_pull_request()
import httpx
from .config import github_api_url, github_token

class GitHubClient:
    """An asynchronous GitHub client utilizing centralized configuration."""     
    
    def __init__(self):
        self.github_api_url = github_api_url.rstrip("/")
        self.github_token = github_token
        
        #* Set default headers for GitHub API requests
        self.default_headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "GitHubClient",
        }
        if self.github_token:
            self.default_headers["Authorization"] = f"Bearer {self.github_token}"

        # initialize the single AsyncClient instance
        self.client = httpx.AsyncClient(
            base_url=self.github_api_url, 
            headers=self.default_headers
        )
        
    # get_repository(owner, repo)
    async def get_repository(self, owner:str, repo:str):
        """Fetch repository details from Github API. """
        url = f"repos/{owner}/{repo}"
        
        # * 1. Make GET request using HTTPX relative URL pathing
        response = await self.client.get(url)
        
        # * 2. Check response status (raises httpx.HTTPStatusError if 4xx or 5xx)
        response.raise_for_status()   
        
        # * 3. Parse JSON from response
        data = response.json()
        
        # * 4. Create Repository schema & 5. Return Repository object
        return Repository(**data)