import sqlite3
from pathlib import Path
from typing import Optional


class DatabaseConnection:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(Path(__file__).parent / "dev.db")
        self.db_path = db_path
        self.connection = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

    def init_db(self):
        """Initialize database and create users table if it doesn't exist."""
        with self as db:
            cursor = db.connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE,
                    phone TEXT UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.connection.commit()

    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email."""
        with self as db:
            cursor = db.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_by_phone(self, phone: str) -> Optional[dict]:
        """Get user by phone."""
        with self as db:
            cursor = db.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE phone = ?", (phone,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def create_user(self, email: Optional[str], phone: Optional[str], password_hash: str) -> dict:
        """Create a new user."""
        with self as db:
            cursor = db.connection.cursor()
            cursor.execute(
                "INSERT INTO users (email, phone, password_hash) VALUES (?, ?, ?)",
                (email, phone, password_hash)
            )
            db.connection.commit()
            user_id = cursor.lastrowid
            return {
                "id": user_id,
                "email": email,
                "phone": phone,
                "password_hash": password_hash
            }

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID."""
        with self as db:
            cursor = db.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
