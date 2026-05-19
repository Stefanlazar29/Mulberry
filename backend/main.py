"""
Mulberry FastAPI entrypoint.
Docker: accesat intern de nginx pe portul 10000 (PORT env).
Local:  python -m uvicorn backend.main:app --host 127.0.0.1 --port 9000
StaticFiles montat ultimul — rutele API definite mai sus au prioritate.
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Mulberry API", version="0.1.0")

# allow_origins=["*"] with allow_credentials=True is invalid in Starlette ≥ 0.21
# (raises ValueError at startup). The frontend uses Authorization: Bearer headers,
# not cookies, so credentials=False is correct and wildcard origins work fine.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


# Serve the frontend.  /app in Docker; repo root locally.
# Mounted last — every API route defined above takes priority.
_STATIC_DIR = Path(__file__).resolve().parent.parent
app.mount("/", StaticFiles(directory=str(_STATIC_DIR), html=True), name="static")
