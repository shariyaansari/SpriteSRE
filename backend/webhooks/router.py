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
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None, alias="X-GitHub-Event"),
):
    """
    Receive, verify, parse, and enqueue GitHub webhook events.
    """

    # 1. Get the ORIGINAL request body.
    body = await request.body()

    # 2. Verify GitHub's signature.
    verify_signature(
        payload_body=body,
        secret_token=settings.github_webhook_secret,
        signature_header=x_hub_signature_256,
    )

    # 3. Parse the payload into an Incident (or None if irrelevant).
    payload = await request.json()
    incident = parse_workflow_run(event=x_github_event, payload=payload)

    # 4. If it's a real incident, enqueue it and return immediately.
    if incident is not None:
        await enqueue_incident(incident)

    return {
        "message": "Webhook received and verified successfully"
    }