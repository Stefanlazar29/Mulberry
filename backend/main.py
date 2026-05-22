from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import sqlite3, hashlib, secrets, os
from contextlib import contextmanager

app = FastAPI(title="Mulberry API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.getenv("SQLITE_PATH", "/data/mulberry.db")
security = HTTPBearer()

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                token TEXT
            )
        """)

init_db()

class LoginRequest(BaseModel):
    identifier: str
    password: str

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, email FROM users WHERE token = ?", (token,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"id": row[0], "email": row[1]}

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/auth/login")
def login(req: LoginRequest):
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, email, password_hash FROM users WHERE email = ?",
            (req.identifier,)
        ).fetchone()
        if not row:
            token = secrets.token_hex(32)
            conn.execute(
                "INSERT INTO users (email, password_hash, token) VALUES (?, ?, ?)",
                (req.identifier, hash_password(req.password), token)
            )
            return {"token": token, "email": req.identifier}
        if row[2] != hash_password(req.password):
            raise HTTPException(status_code=401, detail="Parola incorecta")
        token = secrets.token_hex(32)
        conn.execute("UPDATE users SET token = ? WHERE id = ?", (token, row[0]))
        return {"token": token, "email": row[1]}

@app.get("/me")
def me(user=Depends(get_current_user)):
    return user
    