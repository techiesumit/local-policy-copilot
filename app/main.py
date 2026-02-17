import time, uuid, logging
from fastapi import FastAPI, Header
from pydantic import BaseModel
from app.settings import settings
from app.providers.mock import MockProvider
from app.providers.bedrock import BedrockProvider

log = logging.getLogger("uvicorn.error")
app = FastAPI(title="AI Platform MVP (Spiral 0)")

class ChatIn(BaseModel):
    text: str

class ChatOut(BaseModel):
    request_id: str
    provider: str
    latency_ms: int
    answer: str

def get_provider():
    if settings.model_provider == "bedrock":
        return BedrockProvider(settings.aws_region, settings.bedrock_model_id, settings.bedrock_timeout_seconds)
    return MockProvider()

@app.post("/chat", response_model=ChatOut)
def chat(req: ChatIn, x_request_id: str | None = Header(default=None)):
    rid = x_request_id or str(uuid.uuid4())
    t0 = time.time()
    answer = get_provider().chat(req.text)
    ms = int((time.time() - t0) * 1000)
    log.info("chat request_id=%s provider=%s latency_ms=%s", rid, settings.model_provider, ms)
    return ChatOut(request_id=rid, provider=settings.model_provider, latency_ms=ms, answer=answer)
