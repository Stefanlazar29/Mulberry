"""
Mulberry FastAPI entrypoint (minimal). Full API routes from older builds were never in Git;
extend here as needed. Run: python -m uvicorn backend.main:app --host 127.0.0.1 --port 9000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mulberry API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}
