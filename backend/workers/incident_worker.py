# Consume incidents and process them
# This worker will continously do  
# wait for Incident
#      ↓
# get Incident from queue
#      ↓
# process it
#      ↓
# mark task complete

# It has to be started once (e.g. at FastAPI startup) as a background asyncio.Task, and just keep looping for the lifetime of the app.

import logging
import asyncio

from backend.schemas.incident import Incident
from backend.schemas.status import IncidentStatus
from backend.queue.incident_queue import dequeue_incident, enqueue_incident, incident_queue
from backend.github.client import GitHubClient

logger = logging.getLogger("spritesre.worker")

MAX_RETRIES = 3  # Maximum number of times to retry processing an incident before giving up.
BASE_BACKOFF_SECONDS = 2  # Base backoff time in seconds for exponential backoff.

github_client = GitHubClient()  # Initialize the GitHub client once for the worker.

async def enrich_wit_failure_reason(incident:Incident) -> None:
    """
    Phase 4.3 — fetch and attach the failure_reason for an incident
    by inspecting the failed job's logs on GitHub.
    """
    if "/" not in incident.repository:
        logger.warning(
            "Incident %s has invalid repository format: %s",
            incident.id,
            incident.repository,
        )
        return 
    owner, repo = incident.repository.split("/", 1)
    failure_reason = await github_client.get_failure_reason(
        owner = owner, 
        repo = repo, 
        run_id = incident.run_id
        )
    if not failure_reason:
        logger.warning(
            "Incident %s has no failure reason (no failed job/step found)",
            incident.id
        )
    incident.failure_reason = failure_reason


async def diagnose_incident(incident: Incident) -> None:
    """
    Phase 4.4 — analyze the failure.
    Placeholder for now; Phase 5 will replace this with real AI diagnosis
    (Gemini primary, GPT-4o / Claude fallback).
    """
    if incident.failure_reason is None:
        logger.warning(
            "Incident %s has no failure reason available for diagnosis",
            incident.id
        )
        return
    logger.info(
        "Diagnosing incident %s with failure reason: %s",
        incident.id,
        incident.failure_reason
    )
    # TODO: Real AI diagnosis logic goes here in Phase 5.

async def process_incident(incident: Incident) -> None:
    """
    Placeholder for actual incident processing.
    Later phases will replace this with diagnosis,
    patch generation, testing, etc.
    """
    logger.info(
        "Processing incident %s for %s (workflow=%s, run_id=%s)",
        incident.id,
        incident.repository,
        incident.workflow_name,
        incident.run_id,
    )

    incident.status = IncidentStatus.DIAGNOSING
    await enrich_wit_failure_reason(incident)
    await diagnose_incident(incident)


async def _retry_after_delay(incident: Incident, delay: float, attempt: int) -> None:
    """
    Wait `delay` seconds, then re-enqueue the incident.
    Runs as a detached task so it never blocks the main worker loop.
    """
    logger.info(
        "Retrying incident %s in %.0fs (attempt %d/%d)",
        incident.id,
        delay,
        attempt,
        MAX_RETRIES,
    )
    await asyncio.sleep(delay)
    incident.status = IncidentStatus.QUEUED
    await enqueue_incident(incident)

async def run_incident_worker() -> None:
    """
    Continuously consume incidents from the shared queue
    and process them.
    """
    logger.info("Incident worker started, waiting for incidents...")

    attempts: dict[str, int] = {}  # Track attempts for each incident by ID.

    while True:
        incident = await dequeue_incident()

        incident_id = str(incident.id)
        current_attempts = attempts.get(incident_id, 0) + 1
        attempts[incident_id] = current_attempts

        try:
            await process_incident(incident)
            logger.info(
                "Incident %s processed successfully (attempt %d)",
                incident.id,
                current_attempts,
            )
            attempts.pop(incident_id, None)

        except Exception:
            logger.exception(
                "Failed to process incident %s on attempt %d",
                incident.id,
                current_attempts,
            )

            if current_attempts < MAX_RETRIES:
                backoff_delay = BASE_BACKOFF_SECONDS * (2 ** (current_attempts - 1))
                # Detached — do not await here, or we block the loop for `backoff_delay` seconds.
                asyncio.create_task(_retry_after_delay(incident, backoff_delay, current_attempts))
            else:
                incident.status = IncidentStatus.FAILED
                logger.error(
                    "Incident %s failed permanently after %d attempts",
                    incident.id,
                    current_attempts,
                )
                attempts.pop(incident_id, None)
        finally:
            incident_queue.task_done()