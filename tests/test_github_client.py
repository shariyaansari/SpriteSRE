from backend.github.client import GitHubClient


def test_map_workflow_creates_workflow_model():
    client = GitHubClient.__new__(GitHubClient)
    payload = {
        "id": 123,
        "name": "CI",
        "path": ".github/workflows/ci.yml",
        "state": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
        "url": "https://api.github.com/repos/octo/repo/actions/workflows/123",
        "html_url": "https://github.com/octo/repo/actions/workflows/ci.yml",
        "badge_url": "https://github.com/octo/repo/workflows/CI/badge.svg",
    }

    workflow = client._GitHubClient__map_workflow(payload)

    assert workflow.id == 123
    assert workflow.name == "CI"
    assert workflow.state == "active"
    assert workflow.badge_url.endswith("badge.svg")
