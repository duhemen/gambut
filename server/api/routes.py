# server/api/routes.py
"""REST API endpoints — Hybrid Decentralized"""
import io
import os
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from server import database
from server.database import (
    get_all_data, get_data_chronological, save_row, save_many,
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

router = APIRouter()
REQUIRED_COLS = ['tanggal', 'wt', 'sm', 'rf', 'temp']


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
    """Daftarkan user baru. Hanya admin yang boleh."""
    try:
        user = database.create_user(
            username=payload.username,
            password=payload.password,
            full_name=payload.full_name or "",
            role=payload.role,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {k: v for k, v in user.items() if k != "password_hash"}


@router.post("/auth/login", response_model=TokenResponse)
def api_login(payload: UserLogin):
    """Login → dapat JWT token."""
    user = database.authenticate_user(payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Username atau password salah.",
        )
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
    """Simpan input manual dengan region + trigger alert."""
    try:
        from server.core.index_calc import (
            calculate_peat_fire_index, optimize_pfvi_params
        )
        from server.core.alert import send_alert

        row = {
            "tanggal": datetime.now().strftime('%Y-%m-%d'),
            "region": (payload.region or "indonesia").lower().strip(),
            "wt": float(payload.wt),
            "sm": float(payload.sm),
            "rf": float(payload.rf),
            "temp": float(payload.temp),
        }
        total = save_row(row)

        try:
            from server.core.pfvi_cache import refresh_params
            df_all = get_all_data()
            if len(df_all) >= 3:
                refresh_params(df_all)
        except Exception as e:
            print(f"⚠️ [PFVI-CACHE] Gagal refresh: {e}")

        # ── Hitung PFVI & trigger alert ──
        try:
            df_all = get_all_data()
            if len(df_all) >= 3:
                opt = optimize_pfvi_params(df_all)
                weights = opt['weights']
                normalization = opt['normalization']
            else:
                weights, normalization = None, None

            score, status = calculate_peat_fire_index(
                payload.wt, payload.sm, payload.rf, payload.temp,
                weights=weights, normalization=normalization,
            )

            # Ambil kata status aja (BAHAYA/SIAGA/AMAN)
            status_clean = status.split()[-1] if status else "AMAN"

            alert_result = send_alert(
                score=score,
                status=status_clean,
                data=row,
                region=row["region"],
            )
        except Exception as e:
            print(f"⚠️ [ALERT] Gagal kirim: {e}")
            alert_result = {"error": str(e)}

        return {
            "success": True,
            "message": f"Data {row['region']} tersimpan. Total: {total} baris",
            "data": [row],
            "alert": alert_result,
        }
    except Exception as e:
        return {"success": False, "message": f"Gagal menyimpan: {str(e)}"}

@router.post("/data/upload")
async def api_upload_file(
    file: UploadFile = File(...),
    region: str = "indonesia",
    _user: dict = Depends(get_current_user),
):
    """Upload file CSV/Excel lapangan dengan region."""
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

        # Cek kolom wajib (region optional kalau di-set dari parameter)
        required = ['tanggal', 'wt', 'sm', 'rf', 'temp']
        missing = [c for c in required if c not in df_new.columns]
        if missing:
            return {"success": False,
                    "message": f"Kolom tidak ditemukan: {', '.join(missing).upper()}"}

        clean_df = df_new[required].copy()

        # Tambahkan region dari parameter (atau dari kolom kalau ada)
        if 'region' in df_new.columns:
            clean_df['region'] = df_new['region'].fillna(region).astype(str)
        else:
            clean_df['region'] = region.lower().strip()

        # Reorder biar region di kolom ke-2
        clean_df = clean_df[['tanggal', 'region', 'wt', 'sm', 'rf', 'temp']]

        # Konversi numerik
        for c in ['wt', 'sm', 'rf', 'temp']:
            clean_df[c] = pd.to_numeric(clean_df[c], errors='coerce').fillna(0.0)
        clean_df['tanggal'] = clean_df['tanggal'].astype(str)

        rows = clean_df.to_dict(orient='records')
        save_many(rows)

        return {
            "success": True,
            "message": f"Sukses mengimpor {len(rows)} baris untuk region {region}.",
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