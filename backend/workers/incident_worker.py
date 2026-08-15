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

logger = logging.getLogger("spritesre.worker")

MAX_RETRIES = 3  # Maximum number of times to retry processing an incident before giving up.
BASE_BACKOFF_SECONDS = 2  # Base backoff time in seconds for exponential backoff.


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

    # Temporary state transition for testing.
    # We will replace this with the real lifecycle later.
    # incident.status = IncidentStatus.DIAGNOSING

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

async def process_incident(incident: Incident) -> None:
    incident.status = IncidentStatus.DIAGNOSING

    logger.info(
        "Processing incident %s (attempt test)",
        incident.id,
    )

    raise Exception("Intentional test failure")

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