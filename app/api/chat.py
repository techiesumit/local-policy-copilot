"""Router for `/chat` endpoints.

Small wrapper around pluggable model providers. The provider factory is
kept here to keep the API layer thin and easy to test.
"""

import time, uuid, logging
from fastapi import APIRouter, Header

from app.settings import settings
from app.providers.mock import MockProvider
from app.providers.bedrock import BedrockProvider
from app.core.models import ChatIn, ChatOut

router = APIRouter()
log = logging.getLogger("uvicorn.error")


def get_provider():
    """Return the configured `ModelProvider` instance.

    Uses `settings.model_provider` to decide between `BedrockProvider` and
    `MockProvider`.
    """

    if settings.model_provider == "bedrock":
        return BedrockProvider(
            settings.aws_region,
            settings.bedrock_model_id,
            settings.bedrock_timeout_seconds,
        )
    return MockProvider()


@router.post("/chat", response_model=ChatOut)
def chat(req: ChatIn, x_request_id: str | None = Header(default=None)):
    """Endpoint that forwards `req.text` to the selected provider.

    Returns a `ChatOut` with timing and provider info for observability.

    Example curl:

        curl -X POST http://localhost:8000/chat \
            -H "Content-Type: application/json" \
            -d '{"text": "hello"}'

    Sample response:

        {
            "request_id": "...",
            "provider": "mock",
            "latency_ms": 5,
            "answer": "[mock response] received: hello"
        }
    """

    rid = x_request_id or str(uuid.uuid4())
    t0 = time.time()
    provider = get_provider()
    answer = provider.chat(req.text)
    ms = int((time.time() - t0) * 1000)
    log.info(
        "chat request_id=%s provider=%s latency_ms=%s", rid, settings.model_provider, ms
    )
    return ChatOut(
        request_id=rid, provider=settings.model_provider, latency_ms=ms, answer=answer
    )
