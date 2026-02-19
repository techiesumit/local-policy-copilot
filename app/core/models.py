"""Pydantic models used across the API.

This module centralizes request/response models used by the routers in
`app.api`. Keeping models here ensures consistent typing and concise
OpenAPI schema generation.
"""

from typing import List
from pydantic import BaseModel


# Chat
class ChatIn(BaseModel):
    """Request body for the `/chat` endpoint.

    - `text`: user-supplied message forwarded to the provider.
    """

    text: str


class ChatOut(BaseModel):
    """Response schema for `/chat`.

    - `request_id`: trace id for the request
    - `provider`: which provider answered (e.g. "mock", "bedrock")
    - `latency_ms`: round-trip latency measured in milliseconds
    - `answer`: textual reply from the provider
    """

    request_id: str
    provider: str
    latency_ms: int
    answer: str


# Ingest/search
class IngestOut(BaseModel):
    """Response for `/ingest` describing ingestion results."""

    files: int
    chunks: int
    output_path: str


class SearchIn(BaseModel):
    """Request body for `/search`.

    - `query`: raw keyword query
    - `top_k`: maximum number of hits to return
    """

    query: str
    top_k: int = 5


class SearchHit(BaseModel):
    """Single search hit returned by `/search`."""

    file: str
    chunk_id: str
    score: int
    text: str


class SearchOut(BaseModel):
    """Search response containing the original query and ranked hits."""

    query: str
    hits: List[SearchHit]


# RAG
class RagIn(BaseModel):
    """Request for the RAG-style answer endpoint.

    - `question`: the user question to answer
    - `top_k`: number of supporting chunks to use as context
    """

    question: str
    top_k: int = 3


class RagCitation(BaseModel):
    """A simple citation referencing a source chunk."""

    file: str
    chunk_id: str


class RagOut(BaseModel):
    """RAG response including the answer and source citations."""

    question: str
    answer: str
    citations: List[RagCitation]
    used_chunks: List[SearchHit]
