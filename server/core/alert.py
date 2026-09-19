# server/core/alert.py
"""
Telegram Bot Alert untuk notifikasi BAHAYA.

Fitur UNGGULAN yang tidak ada di peatfr:
- Notifikasi real-time ke Telegram
- Support multi-chat-id (admin + petugas)
- Rate limiting (hindari spam)
- Template pesan informatif
"""
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock
from typing import Optional

import requests

BASE_DIR = Path(__file__).resolve().parents[2]
ALERT_CONFIG_PATH = BASE_DIR / "server" / "data" / "alert_config.json"

_lock = Lock()
_last_sent = {}  # {chat_id: timestamp} untuk rate limiting


# ============================================================
# CONFIG MANAGEMENT
# ============================================================
DEFAULT_CONFIG = {
    "enabled": False,
    "bot_token": "",
    "chat_ids": [],       # list of chat_id (string)
    "min_status": "BAHAYA",   # BAHAYA | SIAGA
    "cooldown_minutes": 30,   # minimal jeda antar alert ke chat yang sama
    "include_link": True,     # sertakan link dashboard
    "dashboard_url": "",
}


def get_alert_config() -> dict:
    """Baca config alert."""
    if not ALERT_CONFIG_PATH.exists():
        return DEFAULT_CONFIG.copy()
    try:
        with open(ALERT_CONFIG_PATH, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        # Merge dengan default (untuk field yang belum ada)
        merged = DEFAULT_CONFIG.copy()
        merged.update(cfg)
        return merged
    except Exception:
        return DEFAULT_CONFIG.copy()


def save_alert_config(cfg: dict) -> None:
    """Simpan config alert."""
    ALERT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ALERT_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)


# ============================================================
# TELEGRAM API
# ============================================================
def send_telegram_message(bot_token: str, chat_id: str,
                          text: str, parse_mode: str = "HTML") -> dict:
    """Kirim pesan ke Telegram."""
    if not bot_token or not chat_id:
        return {"ok": False, "error": "bot_token atau chat_id kosong"}

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }

    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ============================================================
# MESSAGE TEMPLATE
# ============================================================
STATUS_EMOJI = {
    "BAHAYA": "🔴",
    "SIAGA": "🟡",
    "AMAN": "🟢",
}


def build_alert_message(score: float, status: str,
                        data: dict, cfg: dict,
                        region: str = None) -> str:
    """Bangun pesan alert dengan info region."""
    emoji = STATUS_EMOJI.get(status, "⚠️")

    # Header dengan region
    region_upper = (region or "INDONESIA").upper()
    header = f"<b>{emoji} PEATFR ALERT — {status}</b>"
    if region:
        header = f"<b>{emoji} PEATFR ALERT — {region_upper}</b>\n<b>Status: {status}</b>"

    lines = [
        header,
        "",
        f"<b>Skor Kerawanan:</b> <code>{score:.1f}/100</code>",
    ]

    if region:
        lines.append(f"<b>Region:</b> <code>{region_upper}</code>")

    lines.append("")
    lines.append("<b>Data Pengukuran:</b>")

    if "wt" in data:
        lines.append(f"  • Muka Air (WT): <code>{float(data['wt']):.1f} cm</code>")
    if "sm" in data:
        lines.append(f"  • Kelembapan Tanah: <code>{float(data['sm']):.1f} %</code>")
    if "rf" in data:
        lines.append(f"  • Curah Hujan: <code>{float(data['rf']):.1f} mm</code>")
    if "temp" in data:
        lines.append(f"  • Suhu: <code>{float(data['temp']):.1f} °C</code>")
    if "tanggal" in data:
        lines.append(f"  • Tanggal: <code>{data['tanggal']}</code>")

    lines.append("")
    lines.append(f"<i>🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB</i>")

    if cfg.get("include_link") and cfg.get("dashboard_url"):
        lines.append("")
        lines.append(f'🔗 <a href="{cfg["dashboard_url"]}">Buka Dashboard</a>')

    return "\n".join(lines)


# ============================================================
# MAIN — SEND ALERT
# ============================================================
def send_alert(score: float, status: str, data: dict,
               region: str = None, force: bool = False) -> dict:
    """
    Kirim alert ke semua chat_id terdaftar.

    Args:
        score: skor PFVI
        status: "BAHAYA" | "SIAGA" | "AMAN"
        data: dict data pengukuran
        region: nama region (opsional) — untuk info di pesan
        force: bypass config check
    """
    cfg = get_alert_config()

    if not force:
        if not cfg.get("enabled"):
            return {"sent": 0, "failed": 0, "skipped": 1,
                    "reason": "Alert disabled"}

        min_status = cfg.get("min_status", "BAHAYA")
        priority = {"AMAN": 0, "SIAGA": 1, "BAHAYA": 2}
        if priority.get(status, 0) < priority.get(min_status, 2):
            return {"sent": 0, "failed": 0, "skipped": 1,
                    "reason": f"Status {status} < threshold {min_status}"}

    bot_token = cfg.get("bot_token")
    chat_ids = cfg.get("chat_ids", [])

    if not bot_token or not chat_ids:
        return {"sent": 0, "failed": 0, "skipped": 1,
                "reason": "Bot token atau chat_id belum diset"}

    message = build_alert_message(score, status, data, cfg, region=region)
    cooldown = cfg.get("cooldown_minutes", 30) * 60

    sent, failed, skipped = 0, 0, 0
    errors = []

    with _lock:
        now = time.time()
        for chat_id in chat_ids:
            if not force:
                last = _last_sent.get(chat_id, 0)
                if now - last < cooldown:
                    skipped += 1
                    continue

            result = send_telegram_message(bot_token, chat_id, message)
            if result.get("ok"):
                sent += 1
                _last_sent[chat_id] = now
            else:
                failed += 1
                errors.append(f"Chat {chat_id}: {result.get('description', 'unknown')}")

    return {
        "sent": sent,
        "failed": failed,
        "skipped": skipped,
        "errors": errors[:5],
    }

# ============================================================
# TEST & UTILITIES
# ============================================================
def test_bot_connection(bot_token: str) -> dict:
    """Test koneksi ke Telegram Bot API."""
    if not bot_token:
        return {"ok": False, "error": "bot_token kosong"}
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        r = requests.get(url, timeout=10)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}


def send_test_message(bot_token: str, chat_id: str) -> dict:
    """Kirim pesan test."""
    text = (
        "🔥 <b>PeatFR Alert — TEST</b>\n\n"
        "Bot berhasil terhubung! ✅\n"
        "Anda akan menerima notifikasi BAHAYA jika:\n"
        "  • Skor kerawanan ≥ 65\n"
        "  • Ada anomali data\n\n"
        f"<i>🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
    )
    return send_telegram_message(bot_token, chat_id, text)


def get_alert_status() -> dict:
    """Status konfigurasi alert."""
    cfg = get_alert_config()
    return {
        "enabled": cfg.get("enabled", False),
        "has_token": bool(cfg.get("bot_token")),
        "n_chats": len(cfg.get("chat_ids", [])),
        "min_status": cfg.get("min_status", "BAHAYA"),
        "cooldown_minutes": cfg.get("cooldown_minutes", 30),
    }

# ============================================================
# REGION-SPECIFIC HELPERS
# ============================================================
def send_region_alert(region: str, score: float, status: str,
                      data: dict, force: bool = False) -> dict:
    """
    Kirim alert spesifik region.
    Wrapper dari send_alert() dengan region sebagai argumen utama.
    """
    return send_alert(
        score=score,
        status=status,
        data=data,
        region=region,
        force=force,
    )


def send_batch_region_alerts(regions_data: list, force: bool = False) -> dict:
    """
    Kirim alert untuk multiple region sekaligus.

    Args:
        regions_data: [
            {"region": "kalimantan", "score": 90.1, "status": "BAHAYA", "data": {...}},
            ...
        ]
        force: bypass config check

    Returns:
        {"total": int, "sent": int, "skipped": int, "results": [...]}
    """
    results = []
    total_sent = 0
    total_skipped = 0

    # Sort by priority (BAHAYA dulu)
    priority = {"BAHAYA": 2, "SIAGA": 1, "AMAN": 0}
    sorted_regions = sorted(
        regions_data,
        key=lambda x: priority.get(x.get("status", "AMAN"), 0),
        reverse=True,
    )

    for item in sorted_regions:
        r = send_alert(
            score=item["score"],
            status=item["status"],
            data=item.get("data", {}),
            region=item["region"],
            force=force,
        )
        results.append({
            "region": item["region"],
            "status": item["status"],
            "score": item["score"],
            "result": r,
        })
        total_sent += r.get("sent", 0)
        total_skipped += r.get("skipped", 0)

    return {
        "total": len(sorted_regions),
        "sent": total_sent,
        "skipped": total_skipped,
        "results": results,
    }