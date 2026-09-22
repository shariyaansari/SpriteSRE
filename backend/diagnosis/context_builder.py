import logging
from backend.github.client import GitHubClient
from backend.schemas.file import File
from backend.schemas.signal import Signal

logger = logging.getLogger(__name__)

class RepositoryContextBuilder:
    """Builds a relevant set of repository files for diagnosis based on failure signals."""
    
    def __init__(self, github_client: GitHubClient | None = None):
        self.github_client = github_client or GitHubClient()
        self.baseline_candidates = {
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "Dockerfile"
        }

    async def build_context(self, owner: str, repo: str, failure_reason: str, signals: list[Signal]) -> list[File]:
        """
        Given the repository details and failure context, fetch a bounded set 
        of relevant repository files.
        """
        context_files_by_path: dict[str, File] = {}
        
        # 1. Fetch baseline candidates
        try:
            root_entries = await self.github_client.get_directory_contents(owner, repo, "")
            for entry in root_entries:
                if entry.type == "file" and entry.name in self.baseline_candidates:
                    try:
                        file_content = await self.github_client.get_contents(owner, repo, entry.path)
                        # We only want to append files where we successfully retrieved text content
                        if file_content.content:
                            context_files_by_path[file_content.path] = file_content
                    except Exception as e:
                        logger.warning("Failed to fetch baseline file %s: %s", entry.path, e)
        except Exception as e:
            logger.warning("Failed to list root directory for %s/%s: %s", owner, repo, e)

        # 2. Fetch workflow files
        try:
            workflow_entries = await self.github_client.get_directory_contents(owner, repo, ".github/workflows")
            for entry in workflow_entries:
                if entry.type == "file" and (entry.name.endswith(".yml") or entry.name.endswith(".yaml")):
                    try:
                        file_content = await self.github_client.get_contents(owner, repo, entry.path)
                        if file_content.content:
                            context_files_by_path[file_content.path] = file_content
                    except Exception as e:
                        logger.warning("Failed to fetch workflow file %s: %s", entry.path, e)
        except Exception as e:
            # 404 is expected if the .github/workflows directory doesn't exist
            logger.debug("Failed to list workflows for %s/%s (might not exist): %s", owner, repo, e)

        # 3. Future expansion: Fetch failure-specific files based on signals
        # For example, filtering baseline candidates further depending on signal type, 
        # or fetching additional config files based on syntax errors.
        
        return list(context_files_by_path.values())
