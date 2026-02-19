"""Utilities for document ingestion and simple retrieval.

This module provides helpers to:
- Split long text into small overlapping chunks (`chunk_text`).
- Persist and load chunk metadata (`save_chunks` / `load_chunks`).
- Compute a very small keyword match score (`keyword_score`).
- Format context for RAG-style prompts (`format_context`).
"""

from pathlib import Path
from typing import List, Dict, Any
import json
import re

from app.core.models import SearchHit


DOCS_DIR = Path("docs")
DATA_DIR = Path("data")
CHUNKS_PATH = DATA_DIR / "chunks.json"


def chunk_text(text: str, max_chars: int = 600, overlap: int = 80) -> List[str]:
    """Split `text` into character chunks of at most `max_chars`.

    - Normalizes whitespace before chunking.
    - `overlap` controls how many characters are shared between adjacent
      chunks (default 80).
    - Returns an empty list for empty input.
    """

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
    """Load previously saved chunk rows from `data/chunks.json`.

    Returns an empty list if the file does not exist.
    """

    if not CHUNKS_PATH.exists():
        return []
    return json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))


def save_chunks(rows: List[Dict[str, Any]]) -> None:
    """Write `rows` to `data/chunks.json`, creating directories as needed."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_PATH.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def keyword_score(query: str, text: str) -> int:
    """Return a simple integer score based on term counts.

    Splits the `query` into lowercase alpha-numeric tokens and sums their
    occurrences in `text` (case-insensitive).
    """

    q_terms = [t for t in re.findall(r"[a-z0-9]+", query.lower()) if t]
    t = text.lower()
    return sum(t.count(term) for term in q_terms)


def format_context(hits: List[SearchHit]) -> str:
    """Format a list of `SearchHit` into a plain-text SOURCES block.

    This is used by the RAG endpoint to build a prompt that includes
    the selected source text blocks.
    """

    lines = []
    for h in hits:
        lines.append(f"SOURCE [{h.file}::{h.chunk_id}]\n{h.text}\n")
    return "\n".join(lines)

