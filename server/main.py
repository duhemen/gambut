# server/main.py
"""
PEATFR SERVER - FastAPI Backend
Jalankan dengan: python -m uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.api.routes import router
from server.database import init_database, init_satellite_file

app = FastAPI(
    title="PeatFR Server API",
    description="Backend API untuk aplikasi Peat Fire Risk (peatfr-pyqt)",
    version="1.0.0"
)

# CORS agar client dari jaringan lain bisa akses
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Daftarkan router
app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
def startup_event():
    """Inisialisasi database dan file-file pendukung saat server dinyalakan"""
    init_database()
    init_satellite_file()
    print("✅ [SERVER] Database & satellite files siap.")


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "PeatFR Server",
        "version": "1.0.0",
        "endpoints": "/api/v1"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)