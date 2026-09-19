# run_hybrid_server.py
"""Jalankan FastAPI lokal + Cloudflare Tunnel sekaligus."""
import os
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  # ← D:\gambut
CLOUDFLARED_BIN = os.getenv("CLOUDFLARED_BIN", "cloudflared")
CLOUDFLARED_TUNNEL = os.getenv("CLOUDFLARED_TUNNEL", "gambut-server")
UVICORN_APP = os.getenv("UVICORN_APP", "server.main:app")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("PORT", "8000")


def start_tunnel():
    cmd = [CLOUDFLARED_BIN, "tunnel", "run", CLOUDFLARED_TUNNEL]
    print("🚀 Menjalankan Cloudflare Tunnel:", " ".join(cmd))
    return subprocess.Popen(cmd, cwd=BASE_DIR)


def start_server():
    cmd = [
        sys.executable, "-m", "uvicorn", UVICORN_APP,
        "--host", HOST, "--port", PORT, "--reload",
        "--app-dir", str(BASE_DIR),   # ← PENTING: biar uvicorn tahu root
    ]
    print("🚀 Menjalankan FastAPI:", " ".join(cmd))
    return subprocess.Popen(cmd, cwd=BASE_DIR)


def main():
    tunnel_proc = start_tunnel()
    time.sleep(2)
    server_proc = start_server()
    procs = [tunnel_proc, server_proc]

    try:
        while all(p.poll() is None for p in procs):
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Menghentikan semua proses...")
    finally:
        for p in procs:
            if p.poll() is None:
                p.terminate()
        for p in procs:
            try:
                p.wait(timeout=5)
            except Exception:
                p.kill()
        print("✅ Semua proses dihentikan.")


if __name__ == "__main__":
    main()