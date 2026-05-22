"""
SQLite helpers for the Streamlit YourCar app (`app.py`).
Path: SQLITE_PATH env (Docker /data/mulberry.db) or backend/dev.db locally.
"""
from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


def _db_path() -> Path:
    raw = os.environ.get("SQLITE_PATH")
    if raw:
        return Path(raw)
    return Path(__file__).resolve().parent / "dev.db"


@dataclass
class Car:
    ycr_id: Optional[str]
    rca_expiry: Optional[str]
    ycs_score: Optional[float]


def _conn() -> sqlite3.Connection:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(path))


def init_db() -> None:
    with _conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ycr_id TEXT,
                rca_expiry TEXT,
                ycs_score REAL
            )
            """
        )


def get_first_car() -> Optional[Car]:
    init_db()
    with _conn() as c:
        row = c.execute(
            "SELECT ycr_id, rca_expiry, ycs_score FROM cars ORDER BY id LIMIT 1"
        ).fetchone()
    if not row:
        return None
    ycr_id, rca_expiry, ycs_score = row
    return Car(
        ycr_id=ycr_id,
        rca_expiry=rca_expiry if rca_expiry else None,
        ycs_score=float(ycs_score) if ycs_score is not None else None,
    )
