# server/main.py
"""
PEATFR SERVER - FastAPI Backend (v2.0 dengan JWT Auth)
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.api.routes import router
from server.database import (
    init_database, init_satellite_file,
    get_user_by_username, create_user,
)


def bootstrap_admin():
    """Buat user 'admin' pertama jika belum ada."""
    try:
        if not get_user_by_username("admin"):
            create_user(
                username="admin",
                password="admin123",   # ⚠️ minta ganti saat login pertama
                full_name="Administrator",
                role="admin",
            )
            print("🔐 [BOOTSTRAP] User 'admin' dibuat (password: admin123)")
    except Exception as e:
        print(f"⚠️ [BOOTSTRAP] Gagal membuat admin: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ganti @app.on_event('startup') yang sudah deprecated."""
    init_database()
    init_satellite_file()
    bootstrap_admin()
    print("✅ [SERVER] Database, satellite & users siap.")
    yield
    print("👋 [SERVER] Shutting down...")


app = FastAPI(
    title="PeatFR Server API",
    description="Backend API untuk Peat Fire Risk (peatfr-pyqt) — v2.0",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "PeatFR Server",
        "version": "2.0.0",
        "auth": "JWT enabled",
        "endpoints": "/api/v1",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)