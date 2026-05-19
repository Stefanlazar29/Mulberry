"""
Mulberry FastAPI entrypoint.
Docker: accesat intern de nginx pe portul 10000 (PORT env).
Local:  python -m uvicorn backend.main:app --host 0.0.0.0 --port 8080

StaticFiles a fost eliminat — nginx servește fișierele statice direct din
bind-mount (.:/usr/share/nginx/html). Fără StaticFiles, POST pe rute
neimplementate returnează 404, nu 405.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mulberry API", version="0.1.0")

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
