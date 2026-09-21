# server/core/scheduler.py
"""
Auto-fetch scheduler untuk NASA FIRMS satellite data.

Jadwal default:
- Setiap 6 jam (4x sehari)
- Fetch 3 region: kalimantan, sumatera, papua
- Alert otomatis ke Telegram kalau BAHAYA/SIAGA
"""
import os
from datetime import datetime
from threading import Lock

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

_scheduler = None
_lock = Lock()
_state = {
    "running": False,
    "last_run": None,
    "last_result": {},
    "next_run": None,
    "interval_hours": 6,
    "regions": ["kalimantan", "sumatera", "papua"],
    "total_runs": 0,
    "total_errors": 0,
}


def _run_fetch_job():
    """Job yang dijalankan scheduler."""
    global _state

    print(f"\n⏰ [SCHEDULER] Auto-fetch dimulai: {datetime.now().isoformat()}")
    _state["last_run"] = datetime.now().isoformat()

    try:
        from server.core.satellite import fetch_and_save
        from server.database import get_config

        api_key = os.getenv("NASA_FIRMS_API_KEY") or get_config().get("api_key", "")

        if not api_key or api_key == "PASTE_YOUR_API_KEY_HERE":
            msg = "NASA API key tidak tersedia, skip."
            print(f"⚠️ [SCHEDULER] {msg}")
            _state["last_result"] = {"error": msg}
            return

        results = {}
        for region in _state["regions"]:
            try:
                r = fetch_and_save(
                    api_key, region=region, days_back=1, notify=True
                )
                results[region] = {
                    "fetched": r.get("fetched", 0),
                    "saved": r.get("saved", 0),
                    "alert_sent": r.get("alert", {}).get("sent", 0) if r.get("alert") else 0,
                }
                print(f"✅ [SCHEDULER] {region}: {r.get('fetched', 0)} hotspot")
            except Exception as e:
                results[region] = {"error": str(e)}
                _state["total_errors"] += 1
                print(f"❌ [SCHEDULER] {region}: {e}")

        _state["last_result"] = results
        _state["total_runs"] += 1
        print(f"✅ [SCHEDULER] Auto-fetch selesai. Total runs: {_state['total_runs']}\n")
    except Exception as e:
        print(f"❌ [SCHEDULER] Error: {e}")
        _state["last_result"] = {"error": str(e)}
        _state["total_errors"] += 1


def start_scheduler(interval_hours: int = 6, regions: list = None):
    """Start scheduler. Idempotent — kalau sudah jalan, tidak dobel."""
    global _scheduler, _state

    with _lock:
        if _scheduler is not None and _scheduler.running:
            print("⚠️ [SCHEDULER] Sudah berjalan, skip start.")
            return

        if regions:
            _state["regions"] = regions
        _state["interval_hours"] = interval_hours

        _scheduler = BackgroundScheduler(timezone="Asia/Jakarta")
        _scheduler.add_job(
            _run_fetch_job,
            trigger=IntervalTrigger(hours=interval_hours),
            id="satellite_fetch",
            name="NASA FIRMS Auto-Fetch",
            replace_existing=True,
            max_instances=1,
            next_run_time=datetime.now(),  # langsung jalan sekali saat start
        )
        _scheduler.start()
        _state["running"] = True

        jobs = _scheduler.get_jobs()
        if jobs:
            _state["next_run"] = str(jobs[0].next_run_time)

        print(f"✅ [SCHEDULER] Aktif — interval {interval_hours} jam, "
              f"region: {', '.join(_state['regions'])}")


def stop_scheduler():
    """Stop scheduler."""
    global _scheduler, _state
    with _lock:
        if _scheduler and _scheduler.running:
            _scheduler.shutdown(wait=False)
            _state["running"] = False
            print("👋 [SCHEDULER] Dihentikan.")


def get_scheduler_status() -> dict:
    """Status scheduler."""
    global _scheduler

    status = dict(_state)

    if _scheduler and _scheduler.running:
        jobs = _scheduler.get_jobs()
        if jobs:
            status["next_run"] = str(jobs[0].next_run_time)
            status["job_name"] = jobs[0].name

    return status


def trigger_now() -> dict:
    """Trigger fetch manual (di luar jadwal)."""
    _run_fetch_job()
    return {
        "success": True,
        "message": "Auto-fetch dipicu manual.",
        "result": _state["last_result"],
    }