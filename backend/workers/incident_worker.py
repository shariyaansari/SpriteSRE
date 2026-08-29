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

import asyncio
import logging

from backend.schemas.incident import Incident
from backend.schemas.status import IncidentStatus
from backend.queue.incident_queue import (
    dequeue_incident,
    enqueue_incident,
    incident_queue,
)
from backend.github.client import GitHubClient
from backend.diagnosis.pipeline import DiagnosisPipeline


logger = logging.getLogger("spritesre.worker")

MAX_RETRIES = 3
BASE_BACKOFF_SECONDS = 2

github_client = GitHubClient()
diagnosis_pipeline = DiagnosisPipeline()

async def enrich_with_failure_reason(incident: Incident) -> None:
    """
    Phase 4 — Fetch and attach the failure_reason for an incident
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
        owner=owner,
        repo=repo,
        run_id=incident.run_id,
    )

    if not failure_reason:
        logger.warning(
            "Incident %s has no failure reason "
            "(no failed job/step found)",
            incident.id,
        )

    incident.failure_reason = failure_reason


async def diagnose_incident(incident: Incident) -> None:
    """
    Phase 5 — Diagnose the incident using the hybrid
    rule-engine + LLM diagnosis pipeline.
    """

    if not incident.failure_reason:
        logger.warning(
            "Incident %s has no failure reason available "
            "for diagnosis",
            incident.id,
        )
        return

    diagnosis = await diagnosis_pipeline.diagnose(
        incident.failure_reason
    )

    incident.diagnosis = diagnosis

    logger.info(
        "Incident %s diagnosed as %s "
        "(confidence=%.2f)",
        incident.id,
        diagnosis.category,
        diagnosis.confidence,
    )


async def process_incident(incident: Incident) -> None:
    """
    Process an incident through the current pipeline.

    Phase 4:
        Fetch failure information.

    Phase 5:
        Diagnose the failure.
    """

    logger.info(
        "Processing incident %s for %s "
        "(workflow=%s, run_id=%s)",
        incident.id,
        incident.repository,
        incident.workflow_name,
        incident.run_id,
    )

    incident.status = IncidentStatus.DIAGNOSING

    # Phase 4
    await enrich_with_failure_reason(incident)

    # Phase 5
    await diagnose_incident(incident)


async def _retry_after_delay(
    incident: Incident,
    delay: float,
    attempt: int,
) -> None:
    """
    Wait for the backoff period and re-enqueue the incident.
    """

    logger.info(
        "Retrying incident %s in %.0fs "
        "(attempt %d/%d)",
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

    logger.info(
        "Incident worker started, "
        "waiting for incidents..."
    )

    while True:
        incident = await dequeue_incident()

        incident.attempts += 1

        try:
            await process_incident(incident)

            logger.info(
                "Incident %s processed successfully "
                "(attempt %d)",
                incident.id,
                incident.attempts,
            )

        except Exception:
            logger.exception(
                "Failed to process incident %s "
                "on attempt %d",
                incident.id,
                incident.attempts,
            )

            if incident.attempts < MAX_RETRIES:
                backoff_delay = (
                    BASE_BACKOFF_SECONDS
                    * (2 ** (incident.attempts - 1))
                )

                asyncio.create_task(
                    _retry_after_delay(
                        incident,
                        backoff_delay,
                        incident.attempts,
                    )
                )

            else:
                incident.status = IncidentStatus.FAILED

                logger.error(
                    "Incident %s failed permanently "
                    "after %d attempts",
                    incident.id,
                    incident.attempts,
                )

        finally:
            incident_queue.task_done()