# server/api/web.py
"""Serve halaman web dashboard + PWA assets."""
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, FileResponse

router = APIRouter()

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"
STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    """Serve Web Dashboard."""
    html_file = TEMPLATES_DIR / "dashboard.html"
    if not html_file.exists():
        return HTMLResponse("<h1>404 — Dashboard belum ada</h1>", status_code=404)
    return HTMLResponse(html_file.read_text(encoding="utf-8"))


@router.get("/static/manifest.json")
def manifest():
    """PWA Manifest."""
    path = TEMPLATES_DIR / "manifest.json"
    if not path.exists():
        return {"error": "manifest not found"}
    return FileResponse(path, media_type="application/manifest+json")


@router.get("/sw.js")
def service_worker():
    """Service worker — harus di root."""
    path = TEMPLATES_DIR / "sw.js"
    if not path.exists():
        return {"error": "sw not found"}
    return FileResponse(path, media_type="application/javascript")


@router.get("/static/icons/{name}")
def icon(name: str):
    """Serve icon."""
    path = STATIC_DIR / "icons" / name
    if not path.exists() or not path.is_file():
        return {"error": "not found"}
    return FileResponse(path, media_type="image/png")