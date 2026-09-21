# server/api/routes.py
"""REST API endpoints — Hybrid Decentralized"""
import io
import os
from datetime import datetime

import pandas as pd
import sqlite3
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from server.core.regions import get_provinces_from_db
from server import database
from server.core.regions import wilayah_available
from server.database import (
    DATA_DIR, get_all_data, get_data_chronological, save_row, save_many,
    get_satellite_raw, get_config, save_config,
)
from server.models import (
    ManualInput, SyncRequest, ForecastRequest, IndexRequest, ConfigData,
    UserRegister, UserLogin, UserOut, TokenResponse,
)
from server.auth.jwt_handler import create_access_token
from server.auth.dependencies import get_current_user, require_role
from server.core.imputation import (
    knn_imputation, spline_interpolation, linear_interpolation,
)
from server.core.autopeatfr import autopeatfr
from server.core.forecasting import evaluate_forecast, run_forecast
from server.core.index_calc import (
    calculate_peat_fire_index,
    optimize_pfvi_params,
    calculate_pfvi_series,
)

from server.core.audit import log_action, get_recent_logs, get_stats as get_audit_stats
from fastapi import Request

router = APIRouter()
REQUIRED_COLS = ['tanggal', 'wt', 'sm', 'rf', 'temp']

WILAYAH_DB_PATH = DATA_DIR / "wilayah.db"


# ============ SYSTEM ============
@router.get("/system/info")
def api_system_info(_user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "message": "OK",
        "data": {
            "service": "PeatFR Server",
            "version": "2.1.0",
            "mode": "hybrid-decentralized",
        },
    }


# ============ AUTH ============
@router.post("/auth/register", response_model=UserOut, status_code=201)
def api_register(payload: UserRegister, _admin: dict = Depends(require_role("admin"))):
    """Daftarkan user baru dengan wilayah tugas (opsional)."""
    try:
        user = database.create_user(
            username=payload.username,
            password=payload.password,
            full_name=payload.full_name or "",
            role=payload.role,
            assigned_region=payload.assigned_region or "",
            assigned_province=payload.assigned_province or "",
            assigned_regency=payload.assigned_regency or "",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {k: v for k, v in user.items() if k != "password_hash"}


@router.post("/auth/login", response_model=TokenResponse)
def api_login(payload: UserLogin, request: Request):
    """Login → dapat JWT token."""
    user = database.authenticate_user(payload.username, payload.password)
    if not user:
        log_action("LOGIN_FAILED", user=payload.username,
                   ip=request.client.host if request.client else "")
        raise HTTPException(status_code=401, detail="Username atau password salah.")

    log_action("LOGIN", user=user["username"],
               ip=request.client.host if request.client else "")

    token = create_access_token({
        "sub": user["username"],
        "role": user["role"],
    })
    safe_user = {k: v for k, v in user.items() if k != "password_hash"}
    return {
        "success": True,
        "message": f"Selamat datang, {user['full_name'] or user['username']}!",
        "access_token": token,
        "token_type": "bearer",
        "user": safe_user,
    }


@router.get("/auth/me", response_model=UserOut)
def api_me(user: dict = Depends(get_current_user)):
    """Cek info user yang sedang login."""
    return {k: v for k, v in user.items() if k != "password_hash"}


@router.get("/auth/users")
def api_list_users(_: dict = Depends(require_role("admin"))):
    """Admin only: lihat daftar user."""
    return {"success": True, "message": "OK", "data": database.list_users()}


# ============ DATA ENDPOINTS ============
@router.get("/data")
def api_get_data(_user: dict = Depends(get_current_user)):
    """Ambil semua data dari database"""
    try:
        df = get_all_data()
        if df.empty:
            return {
                "success": True,
                "message": "Database kosong",
                "data": [{
                    "tanggal": datetime.now().strftime('%Y-%m-%d'),
                    "wt": 0.0, "sm": 50.0, "rf": 0.0, "temp": 30.0
                }]
            }
        records = df.to_dict(orient='records')
        return {"success": True, "message": "OK", "data": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data")
def api_save_manual(payload: ManualInput, _user: dict = Depends(get_current_user)):
    """Simpan input manual dengan cascading region (5 level)."""
    try:
        row = {
            "tanggal": datetime.now().strftime('%Y-%m-%d'),
            "region": (payload.region or "indonesia").lower().strip(),
            "province": (payload.province or "").strip(),
            "regency": (payload.regency or "").strip(),
            "district": (payload.district or "").strip(),
            "village": (payload.village or "").strip(),
            "wt": float(payload.wt),
            "sm": float(payload.sm),
            "rf": float(payload.rf),
            "temp": float(payload.temp),
        }
        total = save_row(row)

        try:
            log_action(
                "CREATE_DATA",
                user=_user.get("username", "unknown"),
                target=f"{row['region']}/{row['regency']}/{row['district']}",
                details={"wt": row["wt"], "sm": row["sm"], "rf": row["rf"], "temp": row["temp"]},
            )
        except Exception:
            pass

        # ─── Alert logic ────────────────────────────
        alert_result = None
        try:
            from server.core.index_calc import calculate_peat_fire_index, optimize_pfvi_params
            from server.core.alert import send_alert

            df_all = get_all_data()
            weights, normalization = None, None
            if len(df_all) >= 3:
                opt = optimize_pfvi_params(df_all)
                weights = opt['weights']
                normalization = opt['normalization']

            score, status = calculate_peat_fire_index(
                payload.wt, payload.sm, payload.rf, payload.temp,
                weights=weights, normalization=normalization,
            )
            status_clean = status.split()[-1] if status else "AMAN"

            location = " > ".join(filter(None, [
                row["region"], row["province"], row["regency"],
                row["district"], row["village"]
            ]))

            alert_result = send_alert(
                score=score,
                status=status_clean,
                data={**row, "location": location},
                region=row["region"],
            )
        except Exception as e:
            print(f"⚠️ [ALERT] {e}")

        return {
            "success": True,
            "message": f"Data {row['regency'] or row['region']} disimpan. Total: {total}",
            "data": [row],
            "alert": alert_result,
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

@router.post("/data/upload")
async def api_upload_file(
    file: UploadFile = File(...),
    region: str = "indonesia",
    province: str = "",
    regency: str = "",
    district: str = "",
    village: str = "",
    _user: dict = Depends(get_current_user),
):
    """Upload file CSV/Excel lapangan dengan cascading region (5 level)."""
    try:
        ext = os.path.splitext(file.filename or "")[1].lower()
        contents = await file.read()

        if ext == '.csv':
            df_new = pd.read_csv(io.BytesIO(contents))
        elif ext in ['.xlsx', '.xls']:
            df_new = pd.read_excel(io.BytesIO(contents))
        else:
            return {"success": False, "message": "Format harus .csv / .xlsx / .xls"}

        df_new.columns = [c.strip().lower() for c in df_new.columns]

        # Cek kolom wajib
        required = ['tanggal', 'wt', 'sm', 'rf', 'temp']
        missing = [c for c in required if c not in df_new.columns]
        if missing:
            return {"success": False,
                    "message": f"Kolom tidak ditemukan: {', '.join(missing).upper()}"}

        clean_df = df_new[required].copy()

        # ═══════════════════════════════════════════════
        # Region lengkap (5 level)
        # ═══════════════════════════════════════════════
        if 'region' in df_new.columns:
            clean_df['region'] = df_new['region'].fillna(region).astype(str)
        else:
            clean_df['region'] = region.lower().strip()

        clean_df['province'] = province.strip()
        clean_df['regency'] = regency.strip()
        clean_df['district'] = district.strip()
        clean_df['village'] = village.strip()

        # Reorder — pastikan urutan kolom sesuai schema
        clean_df = clean_df[[
            'tanggal', 'region', 'province', 'regency',
            'district', 'village', 'wt', 'sm', 'rf', 'temp'
        ]]

        # Konversi numerik
        for c in ['wt', 'sm', 'rf', 'temp']:
            clean_df[c] = pd.to_numeric(clean_df[c], errors='coerce').fillna(0.0)
        clean_df['tanggal'] = clean_df['tanggal'].astype(str)

        rows = clean_df.to_dict(orient='records')
        save_many(rows)

        # Label lokasi untuk response
        lokasi = regency or region
        if district:
            lokasi = f"{lokasi}, {district}"

        return {
            "success": True,
            "message": f"Sukses mengimpor {len(rows)} baris untuk {lokasi}.",
            "data": rows,
        }
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

# ============ SATELLITE SYNC ============
@router.post("/satellite/sync")
def api_satellite_sync(payload: SyncRequest, _user: dict = Depends(get_current_user)):
    """Baca file satelit mentah, imputasi, dan gabungkan ke DB"""
    try:
        df_sat = get_satellite_raw()
        if df_sat.empty:
            return {"success": False, "message": "File satelit kosong."}

        cols = ['wt', 'sm', 'temp']
        for c in cols:
            if c in df_sat.columns:
                df_sat[c] = pd.to_numeric(df_sat[c], errors='coerce')

        method = payload.method
        if "KNN" in method:
            df_clean = knn_imputation(df_sat, cols)
        elif "Spline" in method:
            df_clean = spline_interpolation(df_sat, cols)
        else:
            df_clean = linear_interpolation(df_sat, cols)

        df_clean[cols] = df_clean[cols].round(2)

        rows = df_clean.to_dict(orient='records')
        save_many(rows)

        return {
            "success": True,
            "message": f"Sinkronisasi berhasil dengan metode {method}.",
            "data": rows,
        }
    except Exception as e:
        return {"success": False, "message": f"Gagal sinkronisasi: {str(e)}"}


# ============ FORECAST ============
@router.post("/forecast")
def api_forecast(payload: ForecastRequest, _user: dict = Depends(get_current_user)):
    """Jalankan prediksi WT dengan model ARIMA/LSTM/GRU."""
    try:
        df = get_data_chronological()
        if df.empty:
            return {"success": False, "message": "Database kosong."}

        series = df['wt'].astype(float)
        hasil = run_forecast(series, model=payload.model, steps=payload.steps)

        return {
            "success": True,
            "message": f"Forecast {payload.model} selesai.",
            "data": [round(float(x), 2) for x in hasil],
        }
    except Exception as e:
        return {"success": False, "message": f"Gagal forecast: {str(e)}"}


# ============ FORECAST EVALUATION ============
@router.post("/forecast/evaluate")
def api_forecast_evaluate(
    payload: ForecastRequest,
    _user: dict = Depends(get_current_user),
):
    """Evaluasi akurasi model dengan train-test split 80/20."""
    try:
        df = get_data_chronological()
        if df.empty:
            return {"success": False, "message": "Database kosong."}

        series = df['wt'].astype(float)
        result = evaluate_forecast(series, model=payload.model, test_ratio=0.2)
        return {"success": True, "message": "Evaluasi selesai.", "data": result}
    except Exception as e:
        return {"success": False, "message": f"Gagal evaluasi: {str(e)}"}


# ============ INDEX (PFVI) ============
@router.post("/index")
def api_index(payload: IndexRequest, _user: dict = Depends(get_current_user)):
    """
    Hitung PFVI. Kalau database punya cukup data,
    bobot dioptimasi otomatis dari time series.
    """
    try:
        df = get_data_chronological()
        if len(df) >= 3:
            weights = optimize_pfvi_params(df)
        else:
            weights = None

        skor, status = calculate_peat_fire_index(
            payload.wt, payload.sm, payload.rf, payload.temp,
            weights=weights,
        )
        return {
            "success": True,
            "message": "OK",
            "data": {
                "score": round(float(skor), 2),
                "status": status,
                "weights": [round(float(w), 4) for w in (weights or [0.4, 0.3, 0.2, 0.1])],
            },
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


# ============ AUTOPEATFR (PIPELINE) ============
@router.post("/autopeatfr")
def api_autopeatfr(payload: ForecastRequest, _user: dict = Depends(get_current_user)):
    """
    Pipeline all-in-one ala peatfr::autopeatfr().
    Jalankan: imputasi → optimasi PFVI → forecast → PFVI forecast.
    """
    try:
        df = get_data_chronological()
        if df.empty:
            return {"success": False, "message": "Database kosong."}

        method = "knn"  # default
        if hasattr(payload, "imputation"):
            method = payload.imputation

        result = autopeatfr(
            df,
            imputation=method,
            model=payload.model,
            h=payload.steps,
            evaluate=True,
        )
        return {
            "success": result.get("success", False),
            "message": "Pipeline autopeatfr selesai." if result.get("success") else result.get("error"),
            "data": result,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": f"Gagal: {str(e)}"}

# ─── Cross-Validation ─────────────────────────────────
@router.post("/forecast/cross-validate")
def api_cross_validate(payload: ForecastRequest, _user: dict = Depends(get_current_user)):
    """Time Series K-Fold Cross-Validation."""
    try:
        from server.core.ensemble import time_series_cv
        df = get_data_chronological()
        if df.empty:
            return {"success": False, "message": "Database kosong."}
        series = df['wt'].astype(float)
        result = time_series_cv(series, model=payload.model, n_splits=3)
        return {"success": "error" not in result, "message": "CV selesai.", "data": result}
    except Exception as e:
        return {"success": False, "message": str(e)}


# ─── Ensemble Multi-Model ─────────────────────────────
@router.post("/forecast/ensemble")
def api_ensemble(payload: ForecastRequest, _user: dict = Depends(get_current_user)):
    """Ensemble forecast dengan confidence interval."""
    try:
        from server.core.ensemble import ensemble_forecast
        df = get_data_chronological()
        if df.empty:
            return {"success": False, "message": "Database kosong."}
        series = df['wt'].astype(float)
        result = ensemble_forecast(series, steps=payload.steps)
        return {
            "success": True,
            "message": "Ensemble forecast selesai.",
            "data": {
                "forecast": [round(float(x), 2) for x in result["forecast"]],
                "individual": {
                    k: [round(float(x), 2) for x in v]
                    for k, v in result["individual"].items()
                },
                "weights": {k: round(float(v), 4) for k, v in result["weights"].items()},
                "ci_lower": [round(float(x), 2) for x in result["ci_lower"]],
                "ci_upper": [round(float(x), 2) for x in result["ci_upper"]],
                "ci_level": 0.95,
            },
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


# ─── DL Backend Info ──────────────────────────────────
@router.get("/dl/info")
def api_dl_info(_user: dict = Depends(get_current_user)):
    """Info backend Deep Learning yang aktif."""
    from server.core.deep_learning import get_backend_info
    return {"success": True, "data": get_backend_info()}

# ============ CONFIG ============
@router.get("/config")
def api_get_config(_user: dict = Depends(require_role("admin"))):
    cfg = get_config()
    return {"success": True, "message": "OK", "data": cfg}


@router.post("/config")
def api_save_config(payload: ConfigData, _user: dict = Depends(require_role("admin"))):
    try:
        save_config({"api_url": payload.api_url, "api_key": payload.api_key})
        return {"success": True, "message": "Konfigurasi disimpan."}
    except Exception as e:
        return {"success": False, "message": str(e)}

# ============ PUBLIC READ-ONLY (untuk web dashboard) ============
@router.get("/data/public")
def api_get_data_public(limit: int = 100, region: str = None):
    """Endpoint publik — pakai PFVI params dari cache (KONSISTEN)."""
    try:
        import numpy as np
        from server.core.index_calc import pfvi_score, classify_status
        from server.core.pfvi_cache import get_cached_params

        df = get_all_data()
        if df.empty:
            return {"success": True, "data": []}

        if region and 'region' in df.columns:
            df = df[df['region'].str.lower() == region.lower()]

        df = df.head(limit).copy()

        # ⬇️ PAKAI PARAMETER DARI CACHE (bukan re-optimize)
        params = get_cached_params()
        weights = params['weights']
        normalization = params['normalization']

        scores, statuses = [], []
        for _, row in df.iterrows():
            try:
                score = pfvi_score(
                    row['wt'], row['sm'], row['rf'], row['temp'],
                    weights, normalization,
                )
                score = float(np.clip(score, 0, 100))
                scores.append(round(score, 1))
                statuses.append(classify_status(score))
            except Exception:
                scores.append(0.0)
                statuses.append("🟢 AMAN")

        df['pfvi_score'] = scores
        df['pfvi_status'] = statuses
        records = df.to_dict(orient='records')
        return {"success": True, "data": records, "count": len(records)}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e), "data": []}

# ============================================================
# ANOMALY DETECTION
# ============================================================
@router.post("/anomaly/detect")
def api_detect_anomalies(_user: dict = Depends(get_current_user)):
    """Deteksi anomali di seluruh data."""
    try:
        from server.core.anomaly import (
            detect_anomalies_ensemble, get_anomaly_summary
        )
        df = get_all_data()
        if df.empty:
            return {"success": False, "message": "Database kosong."}

        detected = detect_anomalies_ensemble(df)
        summary = get_anomaly_summary(detected)

        # Convert bool ke int untuk JSON
        records = detected.to_dict(orient='records')
        for r in records:
            if 'anomaly' in r:
                r['anomaly'] = bool(r['anomaly'])

        return {
            "success": True,
            "message": f"Terdeteksi {summary['anomalies']} anomali dari {summary['total']} baris.",
            "data": {
                "summary": summary,
                "rows": records,
            },
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e)}


@router.get("/anomaly/summary")
def api_anomaly_summary(_user: dict = Depends(get_current_user)):
    """Ringkasan anomali (tanpa detail)."""
    try:
        from server.core.anomaly import (
            detect_anomalies_ensemble, get_anomaly_summary
        )
        df = get_all_data()
        if df.empty:
            return {"success": True, "data": {"total": 0, "anomalies": 0}}
        detected = detect_anomalies_ensemble(df)
        return {"success": True, "data": get_anomaly_summary(detected)}
    except Exception as e:
        return {"success": False, "message": str(e)}


# ============================================================
# TELEGRAM ALERT
# ============================================================
@router.get("/alert/status")
def api_alert_status(_user: dict = Depends(get_current_user)):
    """Status konfigurasi Telegram alert."""
    from server.core.alert import get_alert_status
    return {"success": True, "data": get_alert_status()}


@router.get("/alert/config")
def api_get_alert_config(_user: dict = Depends(require_role("admin"))):
    """Ambil config alert lengkap."""
    from server.core.alert import get_alert_config
    cfg = get_alert_config()
    # Mask token sebagian untuk keamanan
    if cfg.get("bot_token"):
        t = cfg["bot_token"]
        cfg["bot_token"] = t[:10] + "..." + t[-4:] if len(t) > 20 else "***"
    return {"success": True, "data": cfg}


@router.post("/alert/config")
def api_save_alert_config(payload: dict,
                          _user: dict = Depends(require_role("admin"))):
    """Simpan config alert (admin only)."""
    from server.core.alert import get_alert_config, save_alert_config
    current = get_alert_config()

    # Merge dengan payload — jangan overwrite token kalau tidak dikirim
    for key in ["enabled", "chat_ids", "min_status",
                "cooldown_minutes", "include_link", "dashboard_url"]:
        if key in payload:
            current[key] = payload[key]

    # Bot token: kalau dikirim & bukan masked version
    if "bot_token" in payload and payload["bot_token"]:
        tok = payload["bot_token"]
        if not ("..." in tok):  # bukan masked
            current["bot_token"] = tok

    save_alert_config(current)
    return {"success": True, "message": "Config alert tersimpan."}


@router.post("/alert/test")
def api_alert_test(_user: dict = Depends(require_role("admin"))):
    """Kirim pesan test ke semua chat_id."""
    from server.core.alert import get_alert_config, send_test_message
    cfg = get_alert_config()
    bot_token = cfg.get("bot_token")
    chat_ids = cfg.get("chat_ids", [])

    if not bot_token:
        return {"success": False, "message": "Bot token belum diset."}
    if not chat_ids:
        return {"success": False, "message": "Chat ID belum diset."}

    results = []
    for cid in chat_ids:
        r = send_test_message(bot_token, cid)
        results.append({"chat_id": cid, "ok": r.get("ok", False)})

    n_ok = sum(1 for r in results if r["ok"])
    return {
        "success": n_ok > 0,
        "message": f"Test terkirim ke {n_ok}/{len(results)} chat.",
        "data": results,
    }


@router.post("/alert/check-bot")
def api_check_bot(payload: dict,
                  _user: dict = Depends(require_role("admin"))):
    """Cek bot token valid atau tidak."""
    from server.core.alert import test_bot_connection
    token = payload.get("bot_token", "")
    result = test_bot_connection(token)
    if result.get("ok"):
        bot = result.get("result", {})
        return {
            "success": True,
            "message": f"Bot terhubung: @{bot.get('username', 'unknown')}",
            "data": {"username": bot.get("username"), "name": bot.get("first_name")},
        }
    return {"success": False, "message": result.get("description", result.get("error", "Gagal"))}

# ============ SATELLITE ============
@router.post("/satellite/fetch")
def api_satellite_fetch(payload: dict,
                        _user: dict = Depends(require_role("admin"))):
    """Fetch data hotspot NASA FIRMS."""
    try:
        import os
        from server.core.satellite import fetch_and_save

        # Prioritas: payload → .env → config.json
        api_key = (
            payload.get("api_key")
            or os.getenv("NASA_FIRMS_API_KEY")
            or get_config().get("api_key", "")          # ← "api_key" bukan nilainya
        )

        region = payload.get("region", "indonesia")
        days_back = int(payload.get("days_back", 1))

        # Cek: kosong ATAU masih placeholder dari config.json
        if not api_key or api_key == "PASTE_YOUR_API_KEY_HERE":  # ← placeholder string
            return {
                "success": False,
                "message": "NASA FIRMS API key belum diset. "
                          "Daftar gratis di: https://firms.modaps.eosdis.nasa.gov/api/map_key/",
            }

        result = fetch_and_save(api_key, region, days_back)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e)}


@router.get("/satellite/regions")
def api_satellite_regions(_user: dict = Depends(get_current_user)):
    """List region yang tersedia."""
    from server.core.satellite import REGIONS
    return {"success": True, "data": [
        {"key": k, "name": v["name"], "bbox": v["bbox"]}
        for k, v in REGIONS.items()
    ]}

# ============ SATELLITE REGIONAL SUMMARY ============
@router.get("/satellite/regional-summary")
def api_regional_summary():
    """Public endpoint — ringkasan per-region."""
    try:
        from server.core.satellite import get_regional_summary
        summary = get_regional_summary()
        sorted_regions = sorted(
            summary.values(),
            key=lambda x: x["pfvi_score"],
            reverse=True,
        )
        return {
            "success": True,
            "count": len(sorted_regions),
            "data": sorted_regions,
        }
    except Exception as e:
        return {"success": False, "message": str(e), "data": []}

# ============================================================
# ALERT BROADCAST
# ============================================================
@router.post("/alert/broadcast-public")
def api_alert_broadcast_public():
    """
    Public endpoint untuk broadcast alert ke semua region.
    Cooldown di alert.py mencegah spam.
    """
    try:
        from server.core.satellite import get_regional_summary
        from server.core.alert import send_batch_region_alerts

        summary = get_regional_summary()
        if not summary:
            return {
                "success": False,
                "message": "Belum ada data regional. Fetch satelit terlebih dahulu.",
            }

        regions_data = []
        for region, info in summary.items():
            regions_data.append({
                "region": region,
                "score": info["pfvi_score"],
                "status": info["status"].split()[-1],
                "data": {
                    "tanggal": info.get("updated_at", "")[:10],
                    "wt": info["avg_wt"],
                    "sm": info["avg_sm"],
                    "rf": info["avg_rf"],
                    "temp": info["avg_temp"],
                },
            })

        result = send_batch_region_alerts(regions_data, force=False)
        return {
            "success": True,
            "message": f"Broadcast: Sent {result['sent']}, Skipped {result['skipped']}",
            "data": result,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e)}


@router.post("/alert/broadcast-regions")
def api_alert_broadcast_regions(
    payload: dict = None,
    _user: dict = Depends(require_role("admin")),
):
    """Admin: broadcast alert dengan force option."""
    try:
        from server.core.satellite import get_regional_summary
        from server.core.alert import send_batch_region_alerts

        payload = payload or {}
        force = bool(payload.get("force", False))

        summary = get_regional_summary()
        if not summary:
            return {
                "success": False,
                "message": "Belum ada data regional.",
            }

        regions_data = []
        for region, info in summary.items():
            regions_data.append({
                "region": region,
                "score": info["pfvi_score"],
                "status": info["status"].split()[-1],
                "data": {
                    "tanggal": info.get("updated_at", "")[:10],
                    "wt": info["avg_wt"],
                    "sm": info["avg_sm"],
                    "rf": info["avg_rf"],
                    "temp": info["avg_temp"],
                },
            })

        result = send_batch_region_alerts(regions_data, force=force)
        return {
            "success": True,
            "message": f"Broadcast selesai. Sent: {result['sent']}, Skipped: {result['skipped']}",
            "data": result,
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/alert/preview/{region}")
def api_alert_preview(region: str,
                      _user: dict = Depends(get_current_user)):
    """Preview pesan alert untuk region tertentu (TIDAK dikirim)."""
    try:
        from server.core.satellite import get_regional_summary
        from server.core.alert import build_alert_message, get_alert_config

        summary = get_regional_summary()
        if region not in summary:
            return {
                "success": False,
                "message": f"Region '{region}' belum ada data.",
            }

        info = summary[region]
        cfg = get_alert_config()

        preview = build_alert_message(
            score=info["pfvi_score"],
            status=info["status"].split()[-1],
            data={
                "tanggal": info.get("updated_at", "")[:10],
                "wt": info["avg_wt"],
                "sm": info["avg_sm"],
                "rf": info["avg_rf"],
                "temp": info["avg_temp"],
            },
            cfg=cfg,
            region=region,
        )

        return {
            "success": True,
            "data": {
                "region": region,
                "preview_html": preview,
                "score": info["pfvi_score"],
                "status": info["status"],
            },
        }
    except Exception as e:
        return {"success": False, "message": str(e)}

# ============================================================
# SCHEDULER
# ============================================================
@router.get("/scheduler/status")
def api_scheduler_status(_user: dict = Depends(get_current_user)):
    """Status auto-fetch scheduler."""
    from server.core.scheduler import get_scheduler_status
    return {"success": True, "data": get_scheduler_status()}


@router.post("/scheduler/trigger")
def api_scheduler_trigger(_user: dict = Depends(require_role("admin"))):
    """Trigger fetch manual sekarang."""
    from server.core.scheduler import trigger_now
    return trigger_now()


@router.post("/scheduler/start")
def api_scheduler_start(payload: dict = None,
                        _user: dict = Depends(require_role("admin"))):
    """Start scheduler manual."""
    from server.core.scheduler import start_scheduler
    payload = payload or {}
    interval = int(payload.get("interval_hours", 6))
    regions = payload.get("regions")
    start_scheduler(interval_hours=interval, regions=regions)
    return {"success": True, "message": f"Scheduler started ({interval}h)"}


@router.post("/scheduler/stop")
def api_scheduler_stop(_user: dict = Depends(require_role("admin"))):
    """Stop scheduler."""
    from server.core.scheduler import stop_scheduler
    stop_scheduler()
    return {"success": True, "message": "Scheduler stopped"}

# ============================================================
# REGIONS — LEVEL 4 & 5
# ============================================================
@router.get("/regions/{region_key}/{province_key}/{regency}/districts")
def api_get_districts(region_key: str, province_key: str, regency: str):
    """List kecamatan dalam kabupaten."""
    from server.core.regions import get_districts
    data = get_districts(region_key, province_key, regency)
    return {"success": True, "count": len(data), "data": data}


@router.get("/regions/{region_key}/{province_key}/{regency}/{district_id}/villages")
def api_get_villages(region_key: str, province_key: str,
                     regency: str, district_id: str):
    """List kelurahan dalam kecamatan."""
    from server.core.regions import get_villages
    data = get_villages(region_key, province_key, regency, district_id)
    return {"success": True, "count": len(data), "data": data}

# ============================================================
# WILAYAH (SQLite — Kemendagri 2025 via cahyadsn)
# Prefix /wilayah — biar tidak conflict dengan /regions (emsifa)
# ============================================================
@router.get("/wilayah/provinces")
def api_wilayah_provinces():
    """List provinsi dari wilayah.db."""
    from server.core.regions import wilayah_available, get_all_regions, WILAYAH_DB_PATH
    conn = sqlite3.connect(str(WILAYAH_DB_PATH))

    if not wilayah_available():
        return {
            "success": False,
            "message": "wilayah.db belum ada. Jalankan scripts/download_wilayah.py & build_wilayah_db.py",
            "data": [],
        }

    data = get_provinces_from_db()
    return {"success": True, "count": len(data), "data": data}


@router.get("/wilayah/{province_kode}/regencies")
def api_wilayah_regencies(province_kode: str):
    """List kabupaten dari wilayah.db."""
    from server.core.regions import get_regencies_from_db
    data = get_regencies_from_db(province_kode)
    return {"success": True, "count": len(data), "data": data}


@router.get("/wilayah/{province_kode}/{regency_kode}/districts")
def api_wilayah_districts(province_kode: str, regency_kode: str):
    """List kecamatan dari wilayah.db."""
    from server.core.regions import get_districts_from_db
    data = get_districts_from_db(regency_kode)
    return {"success": True, "count": len(data), "data": data}


@router.get("/wilayah/{province_kode}/{regency_kode}/{district_kode}/villages")
def api_wilayah_villages(province_kode: str, regency_kode: str, district_kode: str):
    """List kelurahan/desa dari wilayah.db."""
    from server.core.regions import get_villages_from_db
    data = get_villages_from_db(district_kode)
    return {"success": True, "count": len(data), "data": data}

# ============================================================
# REGIONS (dari regions.json — emsifa-compatible)
# Untuk RegionSelector level 1-3
# ============================================================
@router.get("/regions/tree")
def api_get_regions_tree():
    """Full tree structure untuk dropdown cascading (level 1-3)."""
    from server.core.regions import get_all_regions
    return {"success": True, "data": get_all_regions()}


@router.get("/regions")
def api_get_regions():
    """List region level 1 (pulau)."""
    from server.core.regions import get_region_list
    return {"success": True, "data": get_region_list()}


@router.get("/regions/{region_key}/provinces")
def api_get_provinces(region_key: str):
    """List provinsi dalam region."""
    from server.core.regions import get_provinces
    return {"success": True, "data": get_provinces(region_key)}


@router.get("/regions/{region_key}/{province_key}/regencies")
def api_get_regencies(region_key: str, province_key: str):
    """List kabupaten/kota dalam provinsi (dari regions.json)."""
    from server.core.regions import get_regencies
    return {"success": True, "data": get_regencies(region_key, province_key)}

# ============================================================
# REGIONAL DRILL-DOWN — Stats & Tree per Wilayah
# ============================================================
@router.get("/wilayah/stats/{region_key}")
def api_wilayah_stats(region_key: str):
    """
    Statistik wilayah + prediksi PFVI per kabupaten.
    - Kabupaten dengan data → PFVI dari data aktual
    - Kabupaten tanpa data → PFVI dari region induk (inherit)
    """
    from server.core.regions import (
        wilayah_available, get_all_regions, WILAYAH_DB_PATH
    )
    from server.core.satellite import get_regional_summary
    from server.core.index_calc import (
        optimize_pfvi_params, pfvi_score, classify_status
    )
    from server.database import get_all_data
    import sqlite3
    import numpy as np

    if not wilayah_available():
        return {"success": False, "message": "wilayah.db belum ada", "data": {}}

    regions_meta = get_all_regions()
    if region_key not in regions_meta:
        return {"success": False, "message": f"Region '{region_key}' tidak dikenal"}

    region_meta = regions_meta[region_key]
    region_name = region_meta["name"]
    provinces_meta = region_meta.get("provinces", {})

    # Data gambut untuk hitung per-wilayah stats
    df_data = get_all_data()

    # ⚡ PFVI level region (untuk fallback) — dari satelit
    regional_summary = get_regional_summary()
    region_pfvi = 0.0
    region_status = "❓ Belum Ada Data"
    if region_key in regional_summary:
        region_pfvi = regional_summary[region_key].get("pfvi_score", 0.0)
        region_status = regional_summary[region_key].get("status", "🟢 AMAN")

    try:
        conn = sqlite3.connect(str(WILAYAH_DB_PATH))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        result = {
            "region": region_key,
            "region_name": region_name,
            "icon": region_meta.get("icon", "📍"),
            "region_pfvi": region_pfvi,
            "region_status": region_status,
            "provinces": [],
        }

        total_kab = 0
        total_kec = 0
        total_desa = 0

        for prov_key, prov_info in provinces_meta.items():
            prov_name = prov_info["name"]

            cur.execute(
                "SELECT kode, nama FROM wilayah WHERE level = 1 AND UPPER(nama) = UPPER(?)",
                (prov_name,),
            )
            prov_row = cur.fetchone()
            if not prov_row:
                continue

            prov_kode = prov_row["kode"]

            cur.execute(
                "SELECT kode, nama FROM wilayah WHERE level = 2 AND parent_kode = ? ORDER BY kode",
                (prov_kode,),
            )
            kabupaten_list = []

            for kab_row in cur.fetchall():
                kab_kode = kab_row["kode"]
                kab_nama = kab_row["nama"]

                # Kecamatan & desa count
                cur.execute(
                    "SELECT COUNT(*) FROM wilayah WHERE level = 3 AND parent_kode = ?",
                    (kab_kode,),
                )
                n_kec = cur.fetchone()[0]

                cur.execute(
                    "SELECT COUNT(*) FROM wilayah WHERE level = 4 AND parent_kode LIKE ?",
                    (kab_kode + ".%",),
                )
                n_desa = cur.fetchone()[0]

                # ⚡ Hitung PFVI kabupaten
                n_data = 0
                kab_pfvi = region_pfvi
                kab_status = region_status
                pfvi_source = "inherit"

                if not df_data.empty and 'regency' in df_data.columns:
                    mask = df_data['regency'].str.strip().str.lower() == kab_nama.strip().lower()
                    kab_data = df_data[mask]
                    n_data = len(kab_data)

                    if n_data >= 1:
                        # Hitung PFVI dari data aktual kabupaten ini
                        try:
                            avg_wt = float(kab_data['wt'].astype(float).mean())
                            avg_sm = float(kab_data['sm'].astype(float).mean())
                            avg_rf = float(kab_data['rf'].astype(float).mean())
                            avg_temp = float(kab_data['temp'].astype(float).mean())

                            # Optimize dari seluruh data (biar konsisten)
                            opt = optimize_pfvi_params(df_data)
                            weights = opt['weights']
                            normalization = opt['normalization']

                            score = pfvi_score(
                                avg_wt, avg_sm, avg_rf, avg_temp,
                                weights, normalization,
                            )
                            kab_pfvi = float(np.clip(score, 0, 100))
                            kab_status = classify_status(kab_pfvi)
                            pfvi_source = "aktual"
                        except Exception:
                            pass

                kabupaten_list.append({
                    "kode": kab_kode,
                    "name": kab_nama,
                    "n_districts": n_kec,
                    "n_villages": n_desa,
                    "n_data": n_data,
                    "pfvi_score": round(kab_pfvi, 1),
                    "pfvi_status": kab_status,
                    "pfvi_source": pfvi_source,  # "aktual" | "inherit"
                })

                total_kab += 1
                total_kec += n_kec
                total_desa += n_desa

            result["provinces"].append({
                "key": prov_key,
                "kode": prov_kode,
                "name": prov_name,
                "n_regencies": len(kabupaten_list),
                "regencies": kabupaten_list,
            })

        result["summary"] = {
            "n_provinces": len(result["provinces"]),
            "n_regencies": total_kab,
            "n_districts": total_kec,
            "n_villages": total_desa,
        }

        conn.close()
        return {"success": True, "data": result}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e), "data": {}}

# ============================================================
# WILAYAH — DRILL-DOWN KECAMATAN & DESA (dengan PFVI)
# ============================================================
@router.get("/wilayah/regency/{regency_kode}/districts-detail")
def api_wilayah_districts_detail(regency_kode: str):
    """
    List kecamatan dengan PFVI.
    - Kecamatan dengan data aktual → PFVI dari data
    - Kecamatan tanpa data → inherit dari kabupaten
    """
    from server.core.regions import get_districts_from_db, WILAYAH_DB_PATH
    from server.core.index_calc import (
        optimize_pfvi_params, pfvi_score, classify_status
    )
    from server.database import get_all_data
    import sqlite3
    import numpy as np

    districts = get_districts_from_db(regency_kode)
    df_data = get_all_data()

    # ─── PFVI kabupaten (untuk inherit) ────────────
    kab_pfvi = 50.0
    kab_status = "🟡 SIAGA"
    kab_data = pd.DataFrame()

    # Cari nama kabupaten dari DB
    kab_nama = ""
    try:
        conn_tmp = sqlite3.connect(str(WILAYAH_DB_PATH))
        cur_tmp = conn_tmp.cursor()
        cur_tmp.execute("SELECT nama FROM wilayah WHERE kode = ?", (regency_kode,))
        row = cur_tmp.fetchone()
        conn_tmp.close()
        if row:
            kab_nama = row[0]
    except Exception:
        pass

    # Hitung PFVI kabupaten dari data aktual
    if not df_data.empty and "regency" in df_data.columns and kab_nama:
        mask = df_data['regency'].str.strip().str.lower() == kab_nama.lower()
        kab_data = df_data[mask]

        if len(kab_data) >= 1:
            try:
                opt = optimize_pfvi_params(df_data)
                weights = opt['weights']
                normalization = opt['normalization']
                kab_pfvi = pfvi_score(
                    float(kab_data['wt'].astype(float).mean()),
                    float(kab_data['sm'].astype(float).mean()),
                    float(kab_data['rf'].astype(float).mean()),
                    float(kab_data['temp'].astype(float).mean()),
                    weights, normalization,
                )
                kab_pfvi = float(np.clip(kab_pfvi, 0, 100))
                kab_status = classify_status(kab_pfvi)
            except Exception:
                pass

    # ─── Ambil kecamatan + PFVI ────────────────────
    try:
        conn = sqlite3.connect(str(WILAYAH_DB_PATH))
        cur = conn.cursor()
        result = []

        for d in districts:
            d_kode = d["kode"]
            d_name = d["name"]

            # Jumlah desa
            cur.execute(
                "SELECT COUNT(*) FROM wilayah WHERE level = 4 AND parent_kode = ?",
                (d_kode,),
            )
            n_villages = cur.fetchone()[0]

            # PFVI kecamatan
            n_data = 0
            kec_pfvi = kab_pfvi
            kec_status = kab_status
            pfvi_source = "inherit"

            if not df_data.empty and "district" in df_data.columns:
                mask = df_data["district"].str.strip().str.lower() == d_name.strip().lower()
                kec_data = df_data[mask]
                n_data = len(kec_data)

                if n_data >= 1:
                    try:
                        opt = optimize_pfvi_params(df_data)
                        weights = opt['weights']
                        normalization = opt['normalization']
                        kec_pfvi = pfvi_score(
                            float(kec_data['wt'].astype(float).mean()),
                            float(kec_data['sm'].astype(float).mean()),
                            float(kec_data['rf'].astype(float).mean()),
                            float(kec_data['temp'].astype(float).mean()),
                            weights, normalization,
                        )
                        kec_pfvi = float(np.clip(kec_pfvi, 0, 100))
                        kec_status = classify_status(kec_pfvi)
                        pfvi_source = "aktual"
                    except Exception:
                        pass

            result.append({
                "kode": d_kode,
                "name": d_name,
                "n_villages": n_villages,
                "n_data": n_data,
                "pfvi_score": round(kec_pfvi, 1),
                "pfvi_status": kec_status,
                "pfvi_source": pfvi_source,
            })

        conn.close()
        return {
            "success": True,
            "count": len(result),
            "data": result,
            "kabupaten_pfvi": round(kab_pfvi, 1),
            "kabupaten_status": kab_status,
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e), "data": []}


@router.get("/wilayah/district/{district_kode}/villages-detail")
def api_wilayah_villages_detail(district_kode: str):
    """
    List desa/kelurahan dengan PFVI.
    - Desa dengan data aktual → PFVI dari data
    - Desa tanpa data → inherit dari kecamatan
    """
    from server.core.regions import get_villages_from_db, WILAYAH_DB_PATH
    from server.core.index_calc import (
        optimize_pfvi_params, pfvi_score, classify_status
    )
    from server.database import get_all_data
    import sqlite3
    import numpy as np

    villages = get_villages_from_db(district_kode)
    df_data = get_all_data()

    # ─── PFVI kecamatan (untuk inherit) ────────────
    kec_pfvi = 50.0
    kec_status = "🟡 SIAGA"
    kec_nama = ""

    try:
        conn_tmp = sqlite3.connect(str(WILAYAH_DB_PATH))
        cur_tmp = conn_tmp.cursor()
        cur_tmp.execute("SELECT nama FROM wilayah WHERE kode = ?", (district_kode,))
        row = cur_tmp.fetchone()
        conn_tmp.close()
        if row:
            kec_nama = row[0]
    except Exception:
        pass

    if not df_data.empty and "district" in df_data.columns and kec_nama:
        kec_mask = df_data['district'].str.strip().str.lower() == kec_nama.lower()
        kec_data = df_data[kec_mask]

        if len(kec_data) >= 1:
            try:
                opt = optimize_pfvi_params(df_data)
                weights = opt['weights']
                normalization = opt['normalization']
                kec_pfvi = pfvi_score(
                    float(kec_data['wt'].astype(float).mean()),
                    float(kec_data['sm'].astype(float).mean()),
                    float(kec_data['rf'].astype(float).mean()),
                    float(kec_data['temp'].astype(float).mean()),
                    weights, normalization,
                )
                kec_pfvi = float(np.clip(kec_pfvi, 0, 100))
                kec_status = classify_status(kec_pfvi)
            except Exception:
                pass

    # ─── Ambil desa + PFVI ─────────────────────────
    result = []
    for v in villages:
        v_name = v["name"]
        n_data = 0
        desa_pfvi = kec_pfvi
        desa_status = kec_status
        pfvi_source = "inherit"

        if not df_data.empty and "village" in df_data.columns:
            mask = df_data["village"].str.strip().str.lower() == v_name.strip().lower()
            desa_data = df_data[mask]
            n_data = len(desa_data)

            if n_data >= 1:
                try:
                    opt = optimize_pfvi_params(df_data)
                    weights = opt['weights']
                    normalization = opt['normalization']
                    desa_pfvi = pfvi_score(
                        float(desa_data['wt'].astype(float).mean()),
                        float(desa_data['sm'].astype(float).mean()),
                        float(desa_data['rf'].astype(float).mean()),
                        float(desa_data['temp'].astype(float).mean()),
                        weights, normalization,
                    )
                    desa_pfvi = float(np.clip(desa_pfvi, 0, 100))
                    desa_status = classify_status(desa_pfvi)
                    pfvi_source = "aktual"
                except Exception:
                    pass

        result.append({
            "kode": v["kode"],
            "name": v_name,
            "n_data": n_data,
            "pfvi_score": round(desa_pfvi, 1),
            "pfvi_status": desa_status,
            "pfvi_source": pfvi_source,
        })

    return {
        "success": True,
        "count": len(result),
        "data": result,
        "kecamatan_pfvi": round(kec_pfvi, 1),
        "kecamatan_status": kec_status,
    }

# ============================================================
# PETA — Data untuk Choropleth
# ============================================================
@router.get("/map/data")
def api_map_data():
    """
    Data untuk peta choropleth:
    - Semua kabupaten di 3 region gambut
    - PFVI score + status per kabupaten
    """
    from server.core.regions import get_all_regions, WILAYAH_DB_PATH
    from server.core.satellite import get_regional_summary
    from server.core.index_calc import (
        optimize_pfvi_params, pfvi_score, classify_status
    )
    from server.database import get_all_data
    import sqlite3
    import numpy as np

    regions_meta = get_all_regions()
    regional_summary = get_regional_summary()
    df_data = get_all_data()

    # PFVI params cache
    try:
        opt = optimize_pfvi_params(df_data) if len(df_data) >= 3 else None
        weights = opt['weights'] if opt else [0.4, 0.3, 0.2, 0.1]
        normalization = opt['normalization'] if opt else None
    except Exception:
        weights, normalization = [0.4, 0.3, 0.2, 0.1], None

    results = []

    try:
        conn = sqlite3.connect(str(WILAYAH_DB_PATH))
        cur = conn.cursor()

        for region_key, region_info in regions_meta.items():
            region_name = region_info["name"]
            region_pfvi = regional_summary.get(region_key, {}).get("pfvi_score", 0)
            region_status = regional_summary.get(region_key, {}).get("status", "🟢 AMAN")

            for prov_key, prov_info in region_info.get("provinces", {}).items():
                prov_name = prov_info["name"]

                # Cari kode provinsi
                cur.execute(
                    "SELECT kode FROM wilayah WHERE level = 1 AND UPPER(nama) = UPPER(?)",
                    (prov_name,),
                )
                row = cur.fetchone()
                if not row:
                    continue
                prov_kode = row[0]

                # Ambil semua kabupaten
                cur.execute(
                    "SELECT kode, nama FROM wilayah WHERE level = 2 AND parent_kode = ?",
                    (prov_kode,),
                )
                for kab in cur.fetchall():
                    kab_kode, kab_nama = kab[0], kab[1]

                    # Hitung PFVI
                    n_data = 0
                    kab_pfvi = region_pfvi
                    kab_status = region_status

                    if not df_data.empty and 'regency' in df_data.columns:
                        mask = df_data['regency'].str.strip().str.lower() == kab_nama.strip().lower()
                        kab_data = df_data[mask]
                        n_data = len(kab_data)
                        if n_data >= 1:
                            try:
                                score = pfvi_score(
                                    float(kab_data['wt'].astype(float).mean()),
                                    float(kab_data['sm'].astype(float).mean()),
                                    float(kab_data['rf'].astype(float).mean()),
                                    float(kab_data['temp'].astype(float).mean()),
                                    weights, normalization,
                                )
                                kab_pfvi = float(np.clip(score, 0, 100))
                                kab_status = classify_status(kab_pfvi)
                            except Exception:
                                pass

                    # Skip kabupaten tanpa koordinat (kita pakai centroid by slug)
                    results.append({
                        "region": region_key,
                        "province": prov_name,
                        "kode": kab_kode,
                        "name": kab_nama,
                        "pfvi_score": round(kab_pfvi, 1),
                        "status": kab_status,
                        "n_data": n_data,
                        "has_data": n_data > 0,
                    })

        conn.close()
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": str(e), "data": []}

    return {
        "success": True,
        "count": len(results),
        "data": results,
    }


@router.get("/map/geojson")
def api_map_geojson():
    """Serve GeoJSON file."""
    from fastapi.responses import FileResponse
    from pathlib import Path
    geo_path = Path(__file__).resolve().parents[1] / "static" / "geo" / "indonesia-provinces.geojson"
    if geo_path.exists():
        return FileResponse(geo_path, media_type="application/geo+json")
    return {"error": "GeoJSON not available"}

# ============================================================
# EXPORT
# ============================================================
@router.get("/export/excel")
def api_export_excel(region: str = None):
    """Export data ke Excel (public — data bukan rahasia)."""
    """Export data ke Excel."""
    from fastapi.responses import Response
    from server.core.export import export_to_excel

    df = get_all_data()
    if df.empty:
        raise HTTPException(status_code=404, detail="Tidak ada data")

    if region:
        df = df[df['region'].str.lower() == region.lower()]

    # Select kolom penting
    cols = ['tanggal', 'region', 'province', 'regency', 'district', 'village',
            'wt', 'sm', 'rf', 'temp']
    df = df[[c for c in cols if c in df.columns]]

    # Add PFVI score
    try:
        from server.core.index_calc import pfvi_score, classify_status
        from server.core.pfvi_cache import get_cached_params
        params = get_cached_params()
        weights = params['weights']
        normalization = params['normalization']

        scores, statuses = [], []
        for _, row in df.iterrows():
            try:
                s = pfvi_score(row['wt'], row['sm'], row['rf'], row['temp'],
                              weights, normalization)
                scores.append(round(float(s), 1))
                statuses.append(classify_status(s))
            except Exception:
                scores.append(0.0)
                statuses.append("🟢 AMAN")

        df['pfvi_score'] = scores
        df['status'] = statuses
    except Exception:
        pass

    title = f"Laporan Data Gambut"
    if region:
        title += f" - {region.upper()}"

    excel_bytes = export_to_excel(df, title)

    filename = f"gambut_fr_{region or 'all'}_{datetime.now().strftime('%Y%m%d')}.xlsx"

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/html")
def api_export_html(region: str = None):
    """Export data ke HTML/PDF (public)."""
    """Export data ke HTML (print-to-PDF friendly)."""
    from fastapi.responses import HTMLResponse
    from server.core.export import export_to_html

    df = get_all_data()
    if df.empty:
        raise HTTPException(status_code=404, detail="Tidak ada data")

    if region:
        df = df[df['region'].str.lower() == region.lower()]

    cols = ['tanggal', 'region', 'province', 'regency', 'district', 'village',
            'wt', 'sm', 'rf', 'temp']
    df = df[[c for c in cols if c in df.columns]]

    # Add PFVI
    try:
        from server.core.index_calc import pfvi_score, classify_status
        from server.core.pfvi_cache import get_cached_params
        params = get_cached_params()
        weights = params['weights']
        normalization = params['normalization']

        scores, statuses = [], []
        for _, row in df.iterrows():
            try:
                s = pfvi_score(row['wt'], row['sm'], row['rf'], row['temp'],
                              weights, normalization)
                scores.append(round(float(s), 1))
                statuses.append(classify_status(s))
            except Exception:
                scores.append(0.0)
                statuses.append("🟢 AMAN")

        df['pfvi_score'] = scores
        df['status'] = statuses
    except Exception:
        pass

    title = "Laporan Data Gambut"
    if region:
        title += f" - {region.upper()}"

    html = export_to_html(df, title)
    return HTMLResponse(content=html)

# ============================================================
# AUDIT LOG
# ============================================================
@router.get("/audit/recent")
def api_audit_recent(
    limit: int = 100,
    user: str = None,
    action: str = None,
    _admin: dict = Depends(require_role("admin")),
):
    """Ambil audit log terbaru (admin only)."""
    logs = get_recent_logs(limit=limit, user=user, action=action)
    return {"success": True, "count": len(logs), "data": logs}


@router.get("/audit/stats")
def api_audit_stats(_admin: dict = Depends(require_role("admin"))):
    """Statistik audit log."""
    return {"success": True, "data": get_audit_stats()}