# The route's job initially is simply:

# Receive the request.
# Get the raw request body.
# Get the GitHub headers.
# Pass them to the verifier.
# Return an appropriate response.

from fastapi import APIRouter, Header, Request, status

from backend.config import settings
from backend.webhooks.verifier import verify_signature
from backend.webhooks.parser import parse_workflow_run
from backend.queue.incident_queue import enqueue_incident


router = APIRouter(
    prefix="/webhooks",
    tags=["webhooks"],
)


@router.post("/github", status_code=status.HTTP_200_OK)
async def handle_github_webhook(
    request: Request,
    x_github_event: str | None = Header(default=None),
    x_hub_signature_256: str | None = Header(default=None),
):
    # 1. Get the original request body.
    body = await request.body()

    # 2. Verify that the request came from GitHub.
    verify_signature(
        payload_body=body,
        secret_token=settings.github_webhook_secret,
        signature_header=x_hub_signature_256,
    )

    # 3. Convert JSON body into a Python dictionary.
    payload = await request.json()

    # 4. Convert GitHub payload → Incident.
    incident = parse_workflow_run(
        event=x_github_event,
        payload=payload,
    )

    # 5. Ignore GitHub events that aren't failed workflow runs.
    if incident is None:
        return {
            "message": "Event received but no incident detected."
        }

    # 6. Put the Incident into the shared queue.
    await enqueue_incident(incident)

    # 7. Webhook responds immediately.
    return {
        "message": "Incident detected and queued.",
        "incident_id": str(incident.id),
    }