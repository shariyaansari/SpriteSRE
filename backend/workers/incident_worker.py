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

from backend.schemas.incident import Incident
from backend.schemas.status import IncidentStatus
from backend.queue.incident_queue import dequeue_incident, incident_queue

logger = logging.getLogger("spritesre.worker")

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
    incident.status = IncidentStatus.DIAGNOSING

async def run_incident_worker() -> None:
    """
    Continuously consume incidents from the shared queue
    and process them.
    """

    logger.info("Incident worker started, waiting for incidents...")
    print("Incident worker started...............")
    while True:
        incident = await dequeue_incident()

        try:
            await process_incident(incident)

        except Exception:
            logger.exception(
                "Failed to process incident %s",
                incident.id,
            )

        finally:
            incident_queue.task_done()