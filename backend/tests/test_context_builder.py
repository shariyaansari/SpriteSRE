import pytest
from unittest.mock import AsyncMock, MagicMock

from backend.diagnosis.context_builder import RepositoryContextBuilder
from backend.github.client import GitHubClient
from backend.schemas.file import File


class DummyEntry:
    def __init__(self, name, path, type="file"):
        self.name = name
        self.path = path
        self.type = type


@pytest.fixture
def mock_github_client():
    client = MagicMock(spec=GitHubClient)
    client.get_directory_contents = AsyncMock()
    client.get_contents = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_baseline_files_are_fetched(mock_github_client):
    builder = RepositoryContextBuilder(mock_github_client)
    
    mock_github_client.get_directory_contents.side_effect = lambda owner, repo, path: {
        "": [DummyEntry("requirements.txt", "requirements.txt")],
        ".github/workflows": []
    }[path]
    
    mock_github_client.get_contents.return_value = File(
        name="requirements.txt",
        path="requirements.txt",
        sha="dummy",
        url="dummy",
        html_url="dummy",
        git_url="dummy",
        type="file",
        content="pytest==7.0.0",
        size=15,
        encoding="utf-8"
    )

    files = await builder.build_context("owner", "repo", "failure", [])
    
    assert len(files) == 1
    assert files[0].path == "requirements.txt"
    assert files[0].content == "pytest==7.0.0"


@pytest.mark.asyncio
async def test_workflow_files_are_fetched(mock_github_client):
    builder = RepositoryContextBuilder(mock_github_client)
    
    mock_github_client.get_directory_contents.side_effect = lambda owner, repo, path: {
        "": [],
        ".github/workflows": [DummyEntry("ci.yml", ".github/workflows/ci.yml")]
    }[path]
    
    mock_github_client.get_contents.return_value = File(
        name="ci.yml",
        path=".github/workflows/ci.yml",
        sha="dummy",
        url="dummy",
        html_url="dummy",
        git_url="dummy",
        type="file",
        content="name: CI",
        size=8,
        encoding="utf-8"
    )

    files = await builder.build_context("owner", "repo", "failure", [])
    
    assert len(files) == 1
    assert files[0].path == ".github/workflows/ci.yml"


@pytest.mark.asyncio
async def test_nonexistent_workflows_dont_crash_builder(mock_github_client):
    builder = RepositoryContextBuilder(mock_github_client)
    
    async def mock_get_dir(owner, repo, path):
        if path == "":
            return []
        raise Exception("Not Found")
        
    mock_github_client.get_directory_contents.side_effect = mock_get_dir

    files = await builder.build_context("owner", "repo", "failure", [])
    
    assert len(files) == 0


@pytest.mark.asyncio
async def test_only_files_are_included(mock_github_client):
    builder = RepositoryContextBuilder(mock_github_client)
    
    mock_github_client.get_directory_contents.side_effect = lambda owner, repo, path: {
        "": [DummyEntry("src", "src", type="dir")],
        ".github/workflows": []
    }[path]

    files = await builder.build_context("owner", "repo", "failure", [])
    
    assert len(files) == 0
    mock_github_client.get_contents.assert_not_called()


@pytest.mark.asyncio
async def test_files_without_content_arent_included(mock_github_client):
    builder = RepositoryContextBuilder(mock_github_client)
    
    mock_github_client.get_directory_contents.side_effect = lambda owner, repo, path: {
        "": [DummyEntry("requirements.txt", "requirements.txt")],
        ".github/workflows": []
    }[path]
    
    mock_github_client.get_contents.return_value = File(
        name="requirements.txt",
        path="requirements.txt",
        sha="dummy",
        url="dummy",
        html_url="dummy",
        git_url="dummy",
        type="file",
        content=None,  # Binary or empty
        size=0,
        encoding="none"
    )

    files = await builder.build_context("owner", "repo", "failure", [])
    
    assert len(files) == 0


@pytest.mark.asyncio
async def test_duplicate_paths_arent_returned(mock_github_client):
    builder = RepositoryContextBuilder(mock_github_client)
    
    # Simulate a scenario where the same file might be requested twice
    # (e.g. baseline and later failure-specific selection). 
    # The deduplication uses the context_files_by_path dict.
    
    # We can fake it by having get_directory_contents return two entries with the same path.
    mock_github_client.get_directory_contents.side_effect = lambda owner, repo, path: {
        "": [
            DummyEntry("requirements.txt", "requirements.txt"),
            DummyEntry("requirements.txt", "requirements.txt")
        ],
        ".github/workflows": []
    }[path]
    
    mock_github_client.get_contents.return_value = File(
        name="requirements.txt",
        path="requirements.txt",
        sha="dummy",
        url="dummy",
        html_url="dummy",
        git_url="dummy",
        type="file",
        content="pytest==7.0.0",
        size=15,
        encoding="utf-8"
    )

    files = await builder.build_context("owner", "repo", "failure", [])
    
    # Should only return one File object due to deduplication dict
    assert len(files) == 1
    assert mock_github_client.get_contents.call_count == 2
