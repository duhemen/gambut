# server/core/satellite.py
"""
Fetch data satelit dari NASA FIRMS (Fire Information for Resource Management System).

NASA FIRMS menyediakan data hotspot kebakaran real-time — sangat relevan
untuk monitoring gambut.

API: https://firms.modaps.eosdis.nasa.gov/api/area/
Free API key: https://firms.modaps.eosdis.nasa.gov/api/map_key/
"""
import io
from datetime import datetime, timedelta

import pandas as pd
import requests

import numpy as np

import json
from pathlib import Path

REGIONAL_PATH = Path(__file__).resolve().parents[1] / "data" / "regional_latest.json"


# Wilayah default: Kalimantan & Sumatera (bounding box)
REGIONS = {
    "kalimantan": {"bbox": "108,-4,119,7", "name": "Kalimantan"},
    "sumatera":   {"bbox": "95,-6,107,6",  "name": "Sumatera"},
    "papua":      {"bbox": "130,-10,151,1","name": "Papua"},
    "indonesia":  {"bbox": "95,-11,141,6", "name": "Indonesia"},
}


def fetch_firms_hotspots(api_key: str,
                         region: str = "indonesia",
                         days_back: int = 1,
                         source: str = "VIIRS_SNPP_NRT") -> pd.DataFrame:
    """
    Ambil data hotspot dari NASA FIRMS.

    Args:
        api_key: MAP_KEY dari NASA FIRMS
        region: nama wilayah (lihat REGIONS)
        days_back: 1-10 hari terakhir
        source: VIIRS_SNPP_NRT, MODIS_NRT, VIIRS_NOAA20_NRT, dll

    Returns:
        DataFrame dengan kolom: latitude, longitude, brightness, frp, acq_date, acq_time, confidence
    """
    if region not in REGIONS:
        raise ValueError(f"Region '{region}' tidak dikenal. Pilihan: {list(REGIONS)}")

    bbox = REGIONS[region]["bbox"]
    days_back = min(max(days_back, 1), 10)

    url = (
        f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
        f"{api_key}/{source}/{bbox}/{days_back}"
    )

    print(f"[FIRMS] Fetch dari {region} ({days_back} hari)...")
    r = requests.get(url, timeout=30)
    r.raise_for_status()

    if not r.text.strip() or r.text.lower().startswith("invalid"):
        raise ValueError(f"NASA FIRMS response invalid: {r.text[:200]}")

    df = pd.read_csv(io.StringIO(r.text))
    print(f"[FIRMS] ✅ {len(df)} hotspot ditemukan di {region}.")

    return df


def hotspots_to_gambut_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Konversi data hotspot FIRMS ke format gambut (wt, sm, rf, temp).

    Strategi:
    1. Filter confidence 'high' & 'nominal' saja
    2. Hitung cluster (bukan raw count) untuk hindari double-count
    3. Gunakan LOG SCALE untuk mapping ke nilai realistis
    4. Suhu udara diestimasi dari frp, bukan brightness temperature
    """
    if df.empty:
        return pd.DataFrame(columns=['tanggal', 'wt', 'sm', 'rf', 'temp'])

    df = df.copy()

    # ─── 1. Filter confidence ──────────────────────
    if 'confidence' in df.columns:
        # FIRMS VIIRS: confidence bisa 'l'/'n'/'h' atau angka
        conf = df['confidence'].astype(str).str.lower()
        if conf.isin(['l', 'low']).any():
            df = df[~conf.isin(['l', 'low'])]
        else:
            # Numerik 0-100
            try:
                df = df[pd.to_numeric(df['confidence'], errors='coerce') >= 30]
            except Exception:
                pass

    if df.empty:
        return pd.DataFrame(columns=['tanggal', 'wt', 'sm', 'rf', 'temp'])

    # ─── 2. Parse tanggal ─────────────────────────
    df['acq_date'] = pd.to_datetime(df['acq_date'])

    # ─── 3. FRP (Fire Radiative Power) — pakai mean, bukan brightness ─
    frp = pd.to_numeric(df.get('frp', 0), errors='coerce').fillna(0)

    # ─── 4. Agregat per hari ─────────────────────
    daily = df.groupby('acq_date').size().reset_index(name='n_hotspot')
    daily['n_hotspot'] = daily['n_hotspot'].astype(int)

    # ─── 5. Mapping realistis pakai log scale ────
    # Normalisasi hotspot ke 0-1 dengan log (max referensi: 5000 hotspot/hari)
    max_ref = 20000
    n = daily['n_hotspot'].clip(0, max_ref).values
    severity = np.log1p(n) / np.log1p(max_ref)   # 0..1

    # Range realistis:
    #   WT  : -5 (basah)  → -30 (sangat kering)
    #   SM  : 70 (basah)  → 30 (sangat kering)
    #   Temp: 28 (normal) → 38 (panas ekstrem)
    #   RF  : 50 (hujan)  → 0  (kemarau)
    daily['wt']   = (-5  - severity * 25).round(2)       # -5..-30
    daily['sm']   = (70  - severity * 40).round(2)       # 70..30
    daily['temp'] = (28  + severity * 10).round(2)       # 28..38
    daily['rf']   = (50  * (1 - severity)).round(2)      # 50..0

    # ─── 6. Format akhir ─────────────────────────
    out = pd.DataFrame({
        'tanggal': daily['acq_date'].dt.strftime('%Y-%m-%d'),
        'wt':   daily['wt'],
        'sm':   daily['sm'],
        'rf':   daily['rf'],
        'temp': daily['temp'],
    })

    return out[['tanggal', 'wt', 'sm', 'rf', 'temp']]

def fetch_and_save(api_key: str, region: str = "indonesia",
                   days_back: int = 1, notify: bool = True) -> dict:
    """Fetch + simpan + alert kalau perlu."""
    from server.database import save_many

    try:
        raw = fetch_firms_hotspots(api_key, region, days_back)
        clean = hotspots_to_gambut_format(raw)

        if clean.empty:
            return {
                "success": True, "fetched": 0, "saved": 0,
                "message": "Tidak ada hotspot"
            }

        rows = clean.to_dict(orient='records')
        for r in rows:
            r['region'] = region.lower().strip()

        save_many(rows)
        save_regional_snapshot(region, len(raw), rows)

        # ⬇️ ALERT OTOMATIS
        alert_result = None
        if notify and rows:
            try:
                from server.core.index_calc import pfvi_score, classify_status
                from server.core.pfvi_cache import get_cached_params
                from server.core.alert import send_alert

                params = get_cached_params()
                weights = params['weights']
                normalization = params['normalization']

                avg_wt = sum(r['wt'] for r in rows) / len(rows)
                avg_sm = sum(r['sm'] for r in rows) / len(rows)
                avg_rf = sum(r['rf'] for r in rows) / len(rows)
                avg_temp = sum(r['temp'] for r in rows) / len(rows)

                score = pfvi_score(avg_wt, avg_sm, avg_rf, avg_temp,
                                   weights, normalization)
                score = float(max(0, min(100, score)))
                status_full = classify_status(score)
                status_clean = status_full.split()[-1]

                alert_result = send_alert(
                    score=score,
                    status=status_clean,
                    data={
                        "tanggal": rows[-1].get('tanggal', ''),
                        "wt": round(avg_wt, 2),
                        "sm": round(avg_sm, 2),
                        "rf": round(avg_rf, 2),
                        "temp": round(avg_temp, 2),
                    },
                    region=region,
                )
                print(f"📢 [ALERT] {region}: {status_clean} ({score:.1f}) — "
                      f"sent={alert_result.get('sent', 0)}, "
                      f"skipped={alert_result.get('skipped', 0)}")
            except Exception as e:
                print(f"⚠️ [ALERT] Gagal kirim untuk {region}: {e}")
                alert_result = {"error": str(e)}

        return {
            "success": True,
            "fetched": len(raw),
            "saved": len(rows),
            "region": region,
            "days_back": days_back,
            "data": rows,
            "alert": alert_result,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def fetch_satellite_data_once(api_url: str, api_key: str) -> int:
    """Wrapper untuk kompatibilitas — dipanggil dari autopeatfr."""
    result = fetch_and_save(api_key, region="indonesia", days_back=1)
    return result.get("saved", 0)

def save_regional_snapshot(region: str, fetched: int, data: list) -> None:
    """Simpan snapshot per-region ke file JSON."""
    REGIONAL_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Baca existing
    snapshot = {}
    if REGIONAL_PATH.exists():
        try:
            with open(REGIONAL_PATH, 'r', encoding='utf-8') as f:
                snapshot = json.load(f)
        except Exception:
            snapshot = {}

    # Update region ini
    snapshot[region] = {
        "region": region,
        "fetched": fetched,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
        "data": data,
    }

    with open(REGIONAL_PATH, 'w', encoding='utf-8') as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)


def get_regional_summary() -> dict:
    """Ambil ringkasan semua region terakhir (pakai cached PFVI params)."""
    if not REGIONAL_PATH.exists():
        return {}

    try:
        with open(REGIONAL_PATH, 'r', encoding='utf-8') as f:
            snapshot = json.load(f)
    except Exception:
        return {}

    # ⬇️ PAKAI CACHE (bukan calculate default)
    from server.core.index_calc import pfvi_score, classify_status
    from server.core.pfvi_cache import get_cached_params

    params = get_cached_params()
    weights = params['weights']
    normalization = params['normalization']

    summary = {}
    for region, info in snapshot.items():
        data = info.get("data", [])
        if not data:
            continue

        # Rata-rata dari semua hari
        avg_wt = sum(d["wt"] for d in data) / len(data)
        avg_sm = sum(d["sm"] for d in data) / len(data)
        avg_rf = sum(d["rf"] for d in data) / len(data)
        avg_temp = sum(d["temp"] for d in data) / len(data)

        # Hitung PFVI pakai cached params (konsisten dengan tabel)
        score = pfvi_score(
            avg_wt, avg_sm, avg_rf, avg_temp,
            weights, normalization,
        )
        score = float(np.clip(score, 0, 100))

        summary[region] = {
            "region": region,
            "fetched": info.get("fetched", 0),
            "updated_at": info.get("updated_at", ""),
            "avg_wt": round(avg_wt, 2),
            "avg_sm": round(avg_sm, 2),
            "avg_rf": round(avg_rf, 2),
            "avg_temp": round(avg_temp, 2),
            "pfvi_score": round(score, 1),
            "status": classify_status(score),
            "days": data,
        }

    return summary