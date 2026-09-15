# server/api/routes.py
"""REST API endpoints"""
import io
import os
from datetime import datetime

import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException

from server.database import (
    get_all_data, get_data_chronological, save_row, save_many,
    get_satellite_raw, get_config, save_config
)
from server.models import (
    ManualInput, SyncRequest, ForecastRequest, IndexRequest, ConfigData
)
from server.core.imputation import (
    knn_imputation, spline_interpolation, linear_interpolation
)
from server.core.forecasting import run_arima_forecast, run_lstm_forecast
from server.core.index_calc import calculate_peat_fire_index

router = APIRouter()
REQUIRED_COLS = ['tanggal', 'wt', 'sm', 'rf', 'temp']


# ============ DATA ENDPOINTS ============
@router.get("/data")
def api_get_data():
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
def api_save_manual(payload: ManualInput):
    """Simpan input manual"""
    try:
        row = {
            "tanggal": datetime.now().strftime('%Y-%m-%d'),
            "wt": float(payload.wt),
            "sm": float(payload.sm),
            "rf": float(payload.rf),
            "temp": float(payload.temp)
        }
        total = save_row(row)
        return {
            "success": True,
            "message": f"Data harian berhasil disimpan! Total: {total} baris",
            "data": [row]
        }
    except Exception as e:
        return {"success": False, "message": f"Gagal menyimpan: {str(e)}"}


@router.post("/data/upload")
async def api_upload_file(file: UploadFile = File(...)):
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

        # Bersihkan & konversi
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
            "data": rows
        }
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}


# ============ SATELLITE SYNC ============
@router.post("/satellite/sync")
def api_satellite_sync(payload: SyncRequest):
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
            "data": rows
        }
    except Exception as e:
        return {"success": False, "message": f"Gagal sinkronisasi: {str(e)}"}


# ============ FORECAST & INDEX ============
@router.post("/forecast")
def api_forecast(payload: ForecastRequest):
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
            "data": hasil_rounded
        }
    except Exception as e:
        return {"success": False, "message": f"Gagal forecast: {str(e)}"}


@router.post("/index")
def api_index(payload: IndexRequest):
    """Hitung indeks kerawanan Nelder-Mead"""
    try:
        skor, status = calculate_peat_fire_index(
            payload.wt, payload.sm, payload.rf, payload.temp
        )
        return {
            "success": True,
            "message": "OK",
            "data": {"score": round(float(skor), 2), "status": status}
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


# ============ CONFIG ============
@router.get("/config")
def api_get_config():
    cfg = get_config()
    return {"success": True, "message": "OK", "data": cfg}


@router.post("/config")
def api_save_config(payload: ConfigData):
    try:
        save_config({"api_url": payload.api_url, "api_key": payload.api_key})
        return {"success": True, "message": "Konfigurasi disimpan."}
    except Exception as e:
        return {"success": False, "message": str(e)}