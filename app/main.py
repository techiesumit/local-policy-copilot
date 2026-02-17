import time, uuid, logging
from fastapi import FastAPI, Header
from pydantic import BaseModel
from app.settings import settings
from app.providers.mock import MockProvider
from app.providers.bedrock import BedrockProvider
from pathlib import Path
import json
import re
from typing import List, Dict, Any


log = logging.getLogger("uvicorn.error")
app = FastAPI(title="AI Platform MVP (Spiral 0)")

class ChatIn(BaseModel):
    text: str

class ChatOut(BaseModel):
    request_id: str
    provider: str
    latency_ms: int
    answer: str
    
class IngestOut(BaseModel):
    files: int
    chunks: int
    output_path: str

class SearchIn(BaseModel):
    query: str
    top_k: int = 5

class SearchHit(BaseModel):
    file: str
    chunk_id: str
    score: int
    text: str

class SearchOut(BaseModel):
    query: str
    hits: List[SearchHit]

def get_provider():
    if settings.model_provider == "bedrock":
        return BedrockProvider(settings.aws_region, settings.bedrock_model_id, settings.bedrock_timeout_seconds)
    return MockProvider()
DOCS_DIR = Path("docs")
DATA_DIR = Path("data")
CHUNKS_PATH = DATA_DIR / "chunks.json"

def chunk_text(text: str, max_chars: int = 600, overlap: int = 80) -> List[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks = []
    i = 0
    while i < len(text):
        end = min(len(text), i + max_chars)
        chunks.append(text[i:end])
        i = max(0, end - overlap)
        if end == len(text):
            break
    return chunks

def load_chunks() -> List[Dict[str, Any]]:
    if not CHUNKS_PATH.exists():
        return []
    return json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))

def save_chunks(rows: List[Dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")

def keyword_score(query: str, text: str) -> int:
    q_terms = [t for t in re.findall(r"[a-z0-9]+", query.lower()) if t]
    t = text.lower()
    return sum(t.count(term) for term in q_terms)

@app.post("/chat", response_model=ChatOut)
def chat(req: ChatIn, x_request_id: str | None = Header(default=None)):
    rid = x_request_id or str(uuid.uuid4())
    t0 = time.time()
    answer = get_provider().chat(req.text)
    ms = int((time.time() - t0) * 1000)
    log.info("chat request_id=%s provider=%s latency_ms=%s", rid, settings.model_provider, ms)
    return ChatOut(request_id=rid, provider=settings.model_provider, latency_ms=ms, answer=answer)

@app.post("/search", response_model=SearchOut)
def search(req: SearchIn):
    rows = load_chunks()
    scored = []
    for r in rows:
        s = keyword_score(req.query, r["text"])
        if s > 0:
            scored.append((s, r))
    scored.sort(key=lambda x: x[0], reverse=True)

    hits = [
        SearchHit(file=r["file"], chunk_id=r["chunk_id"], score=s, text=r["text"])
        for s, r in scored[: req.top_k]
    ]
    return SearchOut(query=req.query, hits=hits)


@app.post("/ingest", response_model=IngestOut)
def ingest():
    if not DOCS_DIR.exists():
        return IngestOut(files=0, chunks=0, output_path=str(CHUNKS_PATH))

    rows: List[Dict[str, Any]] = []
    files = 0
    for p in DOCS_DIR.glob("*.md"):
        files += 1
        text = p.read_text(encoding="utf-8", errors="ignore")
        parts = chunk_text(text)
        for idx, part in enumerate(parts):
            rows.append({
                "chunk_id": f"{p.name}::chunk-{idx}",
                "file": p.name,
                "text": part,
            })

    save_chunks(rows)
    return IngestOut(files=files, chunks=len(rows), output_path=str(CHUNKS_PATH))

