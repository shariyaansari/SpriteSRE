
# TODO - Implement a webhook parser that can parse incoming webhook requests and extract relevant information from them. This will involve defining a set of rules for parsing different types of webhook requests and extracting the necessary data from them.
# Translate GitHub JSON → Incident.
# Nothing else.
# Notice the pattern?
# Exactly like
# GitHubClient
# ↓
# Repository Mapper

from uuid import uuid4

from backend.models.incident import Incident
from backend.models.status import IncidentStatus


def parse_workflow_run(event: str, payload: dict) -> Incident | None:
    """
    Inspect an incoming GitHub webhook event and, if it represents a failed
    workflow run, build an Incident from it.
    Returns:
        Incident if the event is a failed workflow_run, otherwise None.
    """

    # 1. Only care about workflow_run events.
    if event != "workflow_run":
        return None

    workflow_run = payload.get("workflow_run")
    if workflow_run is None:
        return None

    # 2. Only care about completed runs.
    if payload.get("action") != "completed":
        return None

    # 3. Only care about failures.
    if workflow_run.get("conclusion") != "failure":
        return None

    # 4. Extract fields for Incident.
    repository_full_name = workflow_run.get("repository", {}).get("full_name")
    workflow_name = workflow_run.get("name")
    run_id = workflow_run.get("id")
    created_at = workflow_run.get("created_at")

    if not all([repository_full_name, workflow_name, run_id, created_at]):
        # Payload didn't have what we need — don't build a broken Incident.
        return None

    return Incident(
        id=uuid4(),
        source="GitHub",
        repository=repository_full_name,
        workflow_name=workflow_name,
        run_id=run_id,
        status=IncidentStatus.DETECTED,
        failure_reason=None,
        created_at=created_at,
    )