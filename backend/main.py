from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import sqlite3, hashlib, secrets, os, httpx
from contextlib import contextmanager
from backend.middleware.admin import require_admin

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://yvpjfmjxunoxmfljixwo.supabase.co")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

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

@app.get("/api/stats")
def stats():
    with get_db() as conn:
        drivers  = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        vehicles = conn.execute("SELECT COUNT(*) FROM cars  WHERE 1").fetchone()[0] if _table_exists(conn, "cars") else 0
    return {"drivers": drivers, "partners": 1, "vehicles": vehicles, "offers": 0}

def _table_exists(conn, name: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone() is not None

# ── Admin endpoints ─────────────────────────────────

def _sb_headers():
    return {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
    }


@app.get("/admin/stats")
async def admin_stats(admin=Depends(require_admin)):
    async with httpx.AsyncClient() as client:
        v_resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/vehicles?select=status",
            headers=_sb_headers(),
        )
        o_resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/offers?select=id",
            headers=_sb_headers(),
        )
    vehicles = v_resp.json() if v_resp.status_code == 200 else []
    offers = o_resp.json() if o_resp.status_code == 200 else []
    with get_db() as conn:
        users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    return {
        "users": users,
        "vehicles": len(vehicles),
        "offers": len(offers),
        "pending": sum(1 for v in vehicles if isinstance(v, dict) and v.get("status") == "pending"),
    }


@app.get("/admin/vehicles")
async def admin_vehicles(admin=Depends(require_admin)):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/vehicles?select=*&order=plate.asc",
            headers=_sb_headers(),
        )
    if resp.status_code != 200:
        raise HTTPException(502, "Eroare Supabase")
    return resp.json()


@app.get("/admin/offers")
async def admin_offers(admin=Depends(require_admin)):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/offers?select=*&order=partner.asc",
            headers=_sb_headers(),
        )
    if resp.status_code != 200:
        raise HTTPException(502, "Eroare Supabase")
    return resp.json()


@app.get("/admin/users")
async def admin_users(admin=Depends(require_admin)):
    with get_db() as conn:
        rows = conn.execute("SELECT id, email, token FROM users ORDER BY id DESC").fetchall()
    return [{"id": r[0], "email": r[1], "has_token": bool(r[2])} for r in rows]


@app.patch("/admin/vehicles/{vin}/status")
async def admin_vehicle_status(vin: str, body: dict, admin=Depends(require_admin)):
    status = body.get("status")
    if status not in ("verified", "pending", "rejected"):
        raise HTTPException(400, "Status invalid")
    async with httpx.AsyncClient() as client:
        resp = await client.patch(
            f"{SUPABASE_URL}/rest/v1/vehicles?vin=eq.{vin}",
            headers=_sb_headers(),
            json={"status": status},
        )
    if resp.status_code not in (200, 204):
        raise HTTPException(502, "Eroare Supabase")
    return {"ok": True, "vin": vin, "status": status}


# ── Static files (trebuie să fie ultimul) ───────────
app.mount("/", StaticFiles(directory=".", html=True), name="root")
