# client/config.py
"""Konfigurasi client dinamis untuk mode hybrid."""
import os
from pathlib import Path

# Coba load .env dari root proyek
try:
    from dotenv import load_dotenv
    # Cari .env di root proyek (parent dari client/)
    ROOT_DIR = Path(__file__).resolve().parent.parent
    ENV_PATH = ROOT_DIR / ".env"
    if ENV_PATH.exists():
        load_dotenv(ENV_PATH)
    else:
        load_dotenv()  # fallback ke cwd
except ImportError:
    pass  # dotenv optional

# Prioritas:
# 1. GAMBUT_SERVER_URL dari environment / .env
# 2. Default localhost untuk development
SERVER_URL = os.getenv("GAMBUT_SERVER_URL", "http://127.0.0.1:8000").rstrip("/")

# Timeout request (detik)
REQUEST_TIMEOUT = int(os.getenv("GAMBUT_REQUEST_TIMEOUT", "15"))

# Info
__all__ = ["SERVER_URL", "REQUEST_TIMEOUT"]