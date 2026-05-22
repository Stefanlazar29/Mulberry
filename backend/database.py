"""
database.py — PostgreSQL via psycopg2.
DATABASE_URL env: postgresql://user:pass@host/dbname
"""
from __future__ import annotations

import os
from typing import Optional, Dict, Any

import psycopg2
import psycopg2.extras


def _db_url() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql://mulberry_user:mulberry_pass@localhost/mulberry"
    )


class DatabaseConnection:
    def __init__(self):
        self.url = _db_url()

    def _conn(self):
        return psycopg2.connect(self.url)

    def init_db(self) -> None:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id          SERIAL PRIMARY KEY,
                        email       TEXT UNIQUE,
                        phone       TEXT UNIQUE,
                        password_hash TEXT NOT NULL,
                        created_at  TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS cars (
                        id         SERIAL PRIMARY KEY,
                        user_id    INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        ycr_id     TEXT,
                        plate      TEXT,
                        vin        TEXT,
                        rca_expiry DATE,
                        ycs_score  NUMERIC(5,2),
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    )
                """)

    # ── Users ─────────────────────────────────────────────
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                row = cur.fetchone()
                return dict(row) if row else None

    def get_user_by_phone(self, phone: str) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT * FROM users WHERE phone = %s", (phone,))
                row = cur.fetchone()
                return dict(row) if row else None

    def create_user(
        self,
        email: Optional[str],
        phone: Optional[str],
        password_hash: str,
    ) -> Dict[str, Any]:
        with self._conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO users (email, phone, password_hash)
                    VALUES (%s, %s, %s)
                    RETURNING id, email, phone, created_at
                    """,
                    (email, phone, password_hash),
                )
                return dict(cur.fetchone())

    # ── Stats ─────────────────────────────────────────────
    def get_stats(self) -> Dict[str, int]:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM users")
                drivers = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM cars")
                vehicles = cur.fetchone()[0]
                return {"drivers": drivers, "partners": 1, "vehicles": vehicles, "offers": 0}
