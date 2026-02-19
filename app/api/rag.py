"""Router for RAG-style question answering.

Builds a prompt using top matching chunks and queries the provider for an
answer constrained to the provided sources.
"""

from fastapi import APIRouter
from app.providers.mock import MockProvider
from app.providers.bedrock import BedrockProvider
from app.settings import settings
from app.core.models import RagIn, RagOut, RagCitation, SearchHit
from app.core.retrieval import load_chunks, keyword_score, format_context

router = APIRouter()


def get_provider():
    """Return the configured provider (Bedrock or Mock)."""

    if settings.model_provider == "bedrock":
        return BedrockProvider(
            settings.aws_region,
            settings.bedrock_model_id,
            settings.bedrock_timeout_seconds,
        )
    return MockProvider()


@router.post("/rag_answer", response_model=RagOut)
def rag_answer(req: RagIn):
    """Return a grounded answer using top `req.top_k` chunks as sources.

    The prompt instructs the model to only answer from the provided sources
    and to return citations after the answer. The function returns both the
    answer text and a list of `RagCitation` objects pointing to the used
    chunks.
    """

    rows = load_chunks()
    scored = []
    for r in rows:
        s = keyword_score(req.question, r["text"])
        if s > 0:
            scored.append((s, r))
    scored.sort(key=lambda x: x[0], reverse=True)
    hits = [
        SearchHit(file=r["file"], chunk_id=r["chunk_id"], score=s, text=r["text"])
        for s, r in scored[: req.top_k]
    ]
    context = format_context(hits)

    prompt = (
        "You are a grounded assistant.\n"
        "Rules:\n"
        "1) Answer ONLY using the SOURCES below.\n"
        "2) If the answer is not in the sources, reply exactly: I don't know.\n"
        "3) After the answer, list citations as a JSON array of strings like "
        '["file::chunk_id", ...].\n\n'
        f"QUESTION: {req.question}\n\n"
        f"SOURCES:\n{context}\n"
    )

    answer_text = get_provider().chat(prompt)
    citations = [RagCitation(file=h.file, chunk_id=h.chunk_id) for h in hits]
    return RagOut(
        question=req.question, answer=answer_text, citations=citations, used_chunks=hits
    )
