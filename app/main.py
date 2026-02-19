"""Application entrypoint wiring API routers.

This module constructs the `FastAPI` app and mounts the API routers from
`app.api`. The actual route implementations live under `app.api.*`.

Run locally (development):

```bash
uvicorn app.main:app --reload --port 8000
```

Then open `http://localhost:8000/docs` to view the OpenAPI UI.
"""

from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.ingest import router as ingest_router
from app.api.rag import router as rag_router

app = FastAPI(title="AI Platform MVP")

app.include_router(chat_router)
app.include_router(ingest_router)
app.include_router(rag_router)
