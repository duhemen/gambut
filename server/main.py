# server/main.py
"""
PEATFR SERVER - FastAPI Backend (v3.0 Hybrid Decentralized)
"""
# ⬇️ WAJIB DI PALING ATAS — load .env sebelum import lain
from pathlib import Path
from dotenv import load_dotenv

# Cari .env di root proyek (parent dari folder server/)
ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
    print(f"✅ [ENV] Loaded from: {ENV_PATH}")
else:
    load_dotenv()  # fallback ke cwd
    print(f"⚠️ [ENV] .env tidak ditemukan di {ENV_PATH}, pakai default")

# ─── Import setelah load_dotenv ────────────────────
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.api.routes import router
from server.database import (
    init_database, init_satellite_file,
    get_user_by_username, create_user,
)

from fastapi import Request
from server.api.web import router as web_router
from fastapi.responses import RedirectResponse 


# ============================================================
# HELPERS
# ============================================================
def get_cors_origins():
    """Ambil CORS origins dari .env."""
    raw = os.getenv("CORS_ORIGINS", "*").strip()
    if raw == "*":
        return ["*"]
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def bootstrap_admin():
    """Buat user 'admin' pertama jika belum ada."""
    try:
        if not get_user_by_username("admin"):
            create_user(
                username="admin",
                password="admin123",
                full_name="Administrator",
                role="admin",
            )
            print("🔐 [BOOTSTRAP] User 'admin' dibuat (password: admin123)")
    except Exception as e:
        print(f"⚠️ [BOOTSTRAP] Gagal membuat admin: {e}")


# ============================================================
# LIFESPAN
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    init_satellite_file()
    bootstrap_admin()
    print("✅ [SERVER] Database, satellite, users siap.")

    # Cek env penting
    if os.getenv("NASA_FIRMS_API_KEY"):
        print("✅ [ENV] NASA FIRMS API key terdeteksi.")
    else:
        print("⚠️ [ENV] NASA FIRMS API key tidak di-set.")

    if os.getenv("TELEGRAM_BOT_TOKEN"):
        print("✅ [ENV] Telegram Bot token terdeteksi.")

    # ⬇️ Refresh PFVI cache saat startup
    try:
        from server.database import get_all_data
        from server.core.pfvi_cache import refresh_params
        df_all = get_all_data()
        if len(df_all) >= 3:
            refresh_params(df_all)
            print("✅ [PFVI-CACHE] Parameter di-refresh dari data existing.")
    except Exception as e:
        print(f"⚠️ [PFVI-CACHE] Skip refresh: {e}")

    # ⬇️ Start auto-fetch scheduler
    if os.getenv("ENABLE_SCHEDULER", "false").lower() == "true":
        try:
            from server.core.scheduler import start_scheduler
            interval = int(os.getenv("SCHEDULER_INTERVAL_HOURS", "6"))
            start_scheduler(interval_hours=interval)
        except Exception as e:
            print(f"⚠️ [SCHEDULER] Gagal start: {e}")
    else:
        print("ℹ️ [SCHEDULER] Disabled (set ENABLE_SCHEDULER=true untuk aktif)")

    yield

    # Shutdown scheduler
    try:
        from server.core.scheduler import stop_scheduler
        stop_scheduler()
    except Exception:
        pass

    print("👋 [SERVER] Shutting down...")


# ============================================================
# APP
# ============================================================
app = FastAPI(
    title="PeatFR Server API",
    description="Backend API untuk Peat Fire Risk (peatfr-pyqt) — v3.0",
    version="3.0.0",
    lifespan=lifespan,
)

origins = get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False if origins == ["*"] else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
app.include_router(web_router)  # /dashboard, /sw.js, /static


# ============================================================
# ROOT & HEALTH
# ============================================================
@app.get("/")
def root(request: Request):
    """Redirect ke dashboard kalau diakses dari browser."""
    accept = request.headers.get("accept", "")
    user_agent = request.headers.get("user-agent", "").lower()

    # Kalau browser (Chrome/Firefox/Safari) → redirect
    is_browser = any(b in user_agent for b in ["mozilla", "chrome", "safari", "firefox", "edge"])
    wants_html = "text/html" in accept

    if is_browser or wants_html:
        return RedirectResponse(url="/dashboard", status_code=302)

    # API client (curl/Postman/Python) → return JSON
    return {
        "status": "ok",
        "service": "PeatFR Server",
        "version": "3.0.0",
        "auth": "JWT enabled",
        "features": [
            "ensemble-forecast", "confidence-interval",
            "cross-validation", "web-dashboard", "anomaly-detection",
            "telegram-alert", "satellite-firms",
        ],
        "endpoints": {
            "api": "/api/v1",
            "dashboard": "/dashboard",
            "docs": "/docs",
        },
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )