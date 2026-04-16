# Mulberry API + frontend static (același origin ca /health, /auth, …)
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Rădăcină proiect (ROOT_DIR = parent(backend))
COPY . /app

RUN mkdir -p /data/uploads /data/chroma_db

ENV SQLITE_PATH=/data/mulberry.db \
    AUTH_AUDIT_PATH=/data/auth_audit.db \
    CHROMA_PERSIST_PATH=/data/chroma_db \
    MULBERRY_UPLOAD_DIR=/data/uploads

EXPOSE 8000

# Date persistente sub /data (volum Docker)
CMD ["sh", "-c", "mkdir -p /data/uploads /data/chroma_db && exec python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"]
