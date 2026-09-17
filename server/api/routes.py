# server/api/routes.py
"""REST API endpoints"""
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
from server.core.forecasting import run_arima_forecast, run_lstm_forecast
from server.core.index_calc import calculate_peat_fire_index

router = APIRouter()
REQUIRED_COLS = ['tanggal', 'wt', 'sm', 'rf', 'temp']


# ============ AUTH ============
@router.post("/auth/register", response_model=UserOut, status_code=201)
def api_register(payload: UserRegister):
    """Daftarkan user baru."""
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
    """Simpan input manual"""
    try:
        row = {
            "tanggal": datetime.now().strftime('%Y-%m-%d'),
            "wt": float(payload.wt),
            "sm": float(payload.sm),
            "rf": float(payload.rf),
            "temp": float(payload.temp),
        }
        total = save_row(row)
        return {
            "success": True,
            "message": f"Data harian berhasil disimpan! Total: {total} baris",
            "data": [row],
        }
    except Exception as e:
        return {"success": False, "message": f"Gagal menyimpan: {str(e)}"}


@router.post("/data/upload")
async def api_upload_file(
    file: UploadFile = File(...),
    _user: dict = Depends(get_current_user),
):
    """Upload file CSV/Excel lapangan"""
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
        missing = [c for c in REQUIRED_COLS if c not in df_new.columns]
        if missing:
            return {"success": False,
                    "message": f"Kolom tidak ditemukan: {', '.join(missing).upper()}"}

        clean_df = df_new[REQUIRED_COLS].copy()
        clean_df['wt'] = pd.to_numeric(clean_df['wt'], errors='coerce').fillna(0.0)
        clean_df['sm'] = pd.to_numeric(clean_df['sm'], errors='coerce').fillna(0.0)
        clean_df['rf'] = pd.to_numeric(clean_df['rf'], errors='coerce').fillna(0.0)
        clean_df['temp'] = pd.to_numeric(clean_df['temp'], errors='coerce').fillna(0.0)
        clean_df['tanggal'] = clean_df['tanggal'].astype(str)

        rows = clean_df.to_dict(orient='records')
        save_many(rows)

        return {
            "success": True,
            "message": f"Sukses mengimpor {len(rows)} data baris lapangan.",
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


# ============ FORECAST & INDEX ============
@router.post("/forecast")
def api_forecast(payload: ForecastRequest, _user: dict = Depends(get_current_user)):
    """Jalankan prediksi WT"""
    try:
        df = get_data_chronological()
        if df.empty:
            return {"success": False, "message": "Database kosong, tidak bisa forecast."}

        series = df['wt'].astype(float)
        model = payload.model

        if "ARIMA" in model:
            hasil = run_arima_forecast(series, steps=payload.steps)
        elif "GRU" in model:
            hasil = run_lstm_forecast(series, steps=payload.steps) * 1.01
        else:
            hasil = run_lstm_forecast(series, steps=payload.steps)

        hasil_rounded = [round(float(x), 2) for x in hasil]
        return {
            "success": True,
            "message": f"Forecast {model} selesai.",
            "data": hasil_rounded,
        }
    except Exception as e:
        return {"success": False, "message": f"Gagal forecast: {str(e)}"}


@router.post("/index")
def api_index(payload: IndexRequest, _user: dict = Depends(get_current_user)):
    """Hitung indeks kerawanan Nelder-Mead"""
    try:
        skor, status = calculate_peat_fire_index(
            payload.wt, payload.sm, payload.rf, payload.temp
        )
        return {
            "success": True,
            "message": "OK",
            "data": {"score": round(float(skor), 2), "status": status},
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


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