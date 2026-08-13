
# TODO -> Implement a webhook verifier that can verify the authenticity of incoming webhook requests. This will involve checking the signature of the request against a known secret key to ensure that the request is coming from a trusted source.


# ? Create a hash using my secret token.  then compare the hash to the signature in the request header.  If they match, then the request is authentic.  If they don't match, then the request is not authentic and should be rejected.


# ! important things to keep in mind when implementing the webhook verifier:
"""
1. github uses hmac hex digest to compute hash 
2. hash sign always starts with sha256=
3. hash sign -> generates -> webhook's secret token + payload body
4. if lang has character encoding, then handle it properly.  (utf-8) -> can have unicode  chars
5. Never use a plain == to compare the hash sign and the computed hash. Instead consider using a method like secure_compare or crypto.timingSafeEqual.
"""
import hashlib
import hmac

from fastapi import HTTPException, status


def verify_signature(
    payload_body: bytes,
    secret_token: str,
    signature_header: str | None,
) -> None:
    """
    Verify that the webhook request was sent by GitHub.

    Raises:
        HTTPException: 403 if the signature is missing or invalid.
    """

    if not signature_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="x-hub-signature-256 header is missing",
        )

    hash_object = hmac.new(
        key=secret_token.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256,
    )

    expected_signature = f"sha256={hash_object.hexdigest()}"

    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request signatures did not match",
        )