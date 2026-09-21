"""Generate & verifikasi JWT token."""
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from jose import JWTError, jwt

# ─── Load .env dari root proyek ──────────────────
try:
    from dotenv import load_dotenv
    ROOT = Path(__file__).resolve().parents[2]
    ENV_PATH = ROOT / ".env"
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH, override=True)
except ImportError:
    pass


SECRET_KEY = os.environ.get("PEATFR_SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = "dev-only-change-this-in-production-please-32bytes-min"
    print("⚠️ [JWT] PEATFR_SECRET_KEY tidak di-set. Pakai default dev.")
else:
    print(f"✅ [JWT] PEATFR_SECRET_KEY loaded ({len(SECRET_KEY)} chars).")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None