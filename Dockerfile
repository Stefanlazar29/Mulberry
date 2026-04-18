# Mulberry — FastAPI (uvicorn)
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

RUN mkdir -p /data

ENV SQLITE_PATH=/data/mulberry.db

# Render (și altele) injectează PORT la runtime; în dashboard setează Port = același port sau lasă PORT din mediu.
EXPOSE 10000

# Formă shell: ${PORT:-10000} la pornire. Folosim `python -m uvicorn` ca să nu depindem de PATH (evită „uvicorn: not found”).
CMD python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}
