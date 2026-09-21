# server/core/pfvi_cache.py
"""
Cache parameter PFVI global — biar konsisten di semua endpoint.

Parameter (weights + normalization) dihitung sekali,
disimpan di file, semua endpoint pakai yang sama.
"""
import json
from datetime import datetime
from pathlib import Path
from threading import Lock

BASE_DIR = Path(__file__).resolve().parents[1]
CACHE_PATH = BASE_DIR / "data" / "pfvi_params.json"
_lock = Lock()

DEFAULT_PARAMS = {
    "weights": [0.4, 0.3, 0.2, 0.1],
    "normalization": None,
    "n_samples": 0,
    "updated_at": None,
}


def get_cached_params() -> dict:
    """Ambil parameter dari cache. Kalau tidak ada, return default."""
    if not CACHE_PATH.exists():
        return DEFAULT_PARAMS.copy()
    try:
        with open(CACHE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return DEFAULT_PARAMS.copy()


def refresh_params(df) -> dict:
    """Optimize PFVI + simpan ke cache."""
    from server.core.index_calc import optimize_pfvi_params
    with _lock:
        opt = optimize_pfvi_params(df)
        cache = {
            "weights": opt['weights'],
            "normalization": opt['normalization'],
            "n_samples": opt.get('n_samples', len(df)),
            "updated_at": datetime.now().isoformat(timespec='seconds'),
        }
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_PATH, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2)
        print(f"✅ [PFVI-CACHE] Refreshed: weights={cache['weights']}")
        return cache