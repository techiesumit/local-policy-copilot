"""Router handling document ingestion and search.

This module delegates chunking and simple keyword-based retrieval to
`app.core.retrieval` and exposes `/ingest` and `/search` endpoints.
"""

from fastapi import APIRouter
from app.core.models import IngestOut, SearchIn, SearchOut, SearchHit
from app.core.retrieval import (
    DOCS_DIR,
    CHUNKS_PATH,
    chunk_text,
    load_chunks,
    save_chunks,
    keyword_score,
)

router = APIRouter()


@router.post("/ingest", response_model=IngestOut)
def ingest():
    """Read `docs/*.md`, split into chunks, and persist them.

    Returns an `IngestOut` summarizing the operation.
    """

    if not DOCS_DIR.exists():
        return IngestOut(files=0, chunks=0, output_path=str(CHUNKS_PATH))

    rows = []
    files = 0
    for p in DOCS_DIR.glob("*.md"):
        files += 1
        text = p.read_text(encoding="utf-8", errors="ignore")
        parts = chunk_text(text)
        for idx, part in enumerate(parts):
            rows.append(
                {
                    "chunk_id": f"{p.name}::chunk-{idx}",
                    "file": p.name,
                    "text": part,
                }
            )
    save_chunks(rows)
    return IngestOut(files=files, chunks=len(rows), output_path=str(CHUNKS_PATH))


@router.post("/search", response_model=SearchOut)
def search(req: SearchIn):
    """Keyword-based search over persisted chunks.

    Scores chunks with `keyword_score` and returns the top `req.top_k`.
    """

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
