# The route's job initially is simply:

# Receive the request.
# Get the raw request body.
# Get the GitHub headers.
# Pass them to the verifier.
# Return an appropriate response.
from fastapi import APIRouter, Header, Request, status

from backend.config import settings
from backend.webhooks.verifier import verify_signature


router = APIRouter(
    prefix="/webhooks",
    tags=["webhooks"],
)


@router.post("/github", status_code=status.HTTP_200_OK)
async def handle_github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
):
    """
    Receive and verify GitHub webhook requests.
    """

    # 1. Get the ORIGINAL request body.
    body = await request.body()

    # 2. Verify GitHub's signature.
    verify_signature(
        payload_body=body,
        secret_token=settings.github_webhook_secret,
        signature_header=x_hub_signature_256,
    )

    # 3. Signature is valid.
    return {
        "message": "Webhook received and verified successfully"
    }