# server/core/audit.py
"""Audit trail untuk semua aktivitas user."""
import json
from datetime import datetime
from pathlib import Path
from threading import Lock

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
AUDIT_PATH = DATA_DIR / "audit_log.jsonl"
_lock = Lock()


def log_action(
    action: str,
    user: str = "system",
    ip: str = "",
    target: str = "",
    details: dict = None,
):
    """
    Catat satu aktivitas ke audit log.

    Args:
        action: "LOGIN", "LOGOUT", "CREATE_DATA", "UPDATE_DATA",
                "DELETE_DATA", "FETCH_SATELLITE", "SEND_ALERT",
                "REGISTER_USER", "EXPORT", etc.
        user: username pelaku
        ip: IP address
        target: objek yang disentuh (contoh: "kalimantan/kalteng/palangka_raya")
        details: dict info tambahan
    """
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "action": action,
        "user": user,
        "ip": ip,
        "target": target,
        "details": details or {},
    }

    with _lock:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")


def get_recent_logs(limit: int = 100, user: str = None,
                    action: str = None) -> list:
    """Ambil log terbaru, dengan filter opsional."""
    if not AUDIT_PATH.exists():
        return []

    entries = []
    with open(AUDIT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
                if user and e.get("user") != user:
                    continue
                if action and e.get("action") != action:
                    continue
                entries.append(e)
            except Exception:
                continue

    return list(reversed(entries[-limit:]))


def get_stats() -> dict:
    """Statistik audit log."""
    if not AUDIT_PATH.exists():
        return {"total": 0, "by_action": {}, "by_user": {}}

    by_action = {}
    by_user = {}
    total = 0

    with open(AUDIT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line.strip())
                total += 1
                a = e.get("action", "UNKNOWN")
                u = e.get("user", "unknown")
                by_action[a] = by_action.get(a, 0) + 1
                by_user[u] = by_user.get(u, 0) + 1
            except Exception:
                continue

    return {
        "total": total,
        "by_action": dict(sorted(by_action.items(), key=lambda x: -x[1])[:10]),
        "by_user": dict(sorted(by_user.items(), key=lambda x: -x[1])[:10]),
    }