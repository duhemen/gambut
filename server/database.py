# server/database.py
"""Lapisan database (CSV-based) untuk server"""
import os
import json
import pandas as pd
from threading import Lock

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "database_gambut.csv")
SATELLITE_PATH = os.path.join(DATA_DIR, "sample_satellite.csv")
CONFIG_PATH = os.path.join(DATA_DIR, "config.json")

_lock = Lock()
REQUIRED_COLS = ['tanggal', 'wt', 'sm', 'rf', 'temp']


def init_database():
    """Pastikan file database CSV ada"""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        pd.DataFrame(columns=REQUIRED_COLS).to_csv(DB_PATH, index=False)


def init_satellite_file():
    """Buat file satelit dummy jika belum ada"""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(SATELLITE_PATH):
        dummy = pd.DataFrame([
            {"tanggal": "2026-09-10", "wt": -5.0, "sm": 55.0, "rf": 12.5, "temp": 28.5},
            {"tanggal": "2026-09-11", "wt": None, "sm": 50.0, "rf": 4.2, "temp": 29.8},
            {"tanggal": "2026-09-12", "wt": -11.5, "sm": None, "rf": 0.0, "temp": 31.2},
            {"tanggal": "2026-09-13", "wt": -13.0, "sm": 42.0, "rf": 0.0, "temp": None},
            {"tanggal": "2026-09-14", "wt": None, "sm": 40.0, "rf": 0.0, "temp": 32.2},
            {"tanggal": "2026-09-15", "wt": -15.2, "sm": 38.5, "rf": 0.0, "temp": 33.5},
        ])
        dummy.to_csv(SATELLITE_PATH, index=False)


def get_all_data() -> pd.DataFrame:
    """Ambil semua data terurut dari terbaru"""
    init_database()
    with _lock:
        try:
            df = pd.read_csv(DB_PATH)
            if df.empty:
                return pd.DataFrame(columns=REQUIRED_COLS)
            df = df.sort_values(by='tanggal', ascending=False).reset_index(drop=True)
            return df
        except Exception:
            return pd.DataFrame(columns=REQUIRED_COLS)


def get_data_chronological() -> pd.DataFrame:
    """Ambil data terurut dari terlama (untuk forecasting)"""
    df = get_all_data()
    if df.empty:
        return df
    return df.sort_values(by='tanggal').reset_index(drop=True)


def save_row(row: dict) -> int:
    """Simpan/upsert satu baris ke database"""
    init_database()
    with _lock:
        df = pd.read_csv(DB_PATH)
        new_df = pd.DataFrame([row])
        if df.empty:
            df = new_df
        else:
            df = pd.concat([df, new_df], ignore_index=True)
        df = df.drop_duplicates(subset=['tanggal'], keep='last')
        df.to_csv(DB_PATH, index=False)
        return len(df)


def save_many(rows: list) -> int:
    """Bulk insert"""
    init_database()
    if not rows:
        return 0
    with _lock:
        df = pd.read_csv(DB_PATH)
        new_df = pd.DataFrame(rows)
        if df.empty:
            df = new_df
        else:
            df = pd.concat([df, new_df], ignore_index=True)
        df = df.drop_duplicates(subset=['tanggal'], keep='last')
        df.to_csv(DB_PATH, index=False)
        return len(rows)


def get_satellite_raw() -> pd.DataFrame:
    """Ambil file satelit mentah (yang masih ada missing values)"""
    init_satellite_file()
    return pd.read_csv(SATELLITE_PATH)


def get_config() -> dict:
    """Baca konfigurasi"""
    if not os.path.exists(CONFIG_PATH):
        return {"api_url": "", "api_key": ""}
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return {"api_url": "", "api_key": ""}


def save_config(cfg: dict):
    """Tulis konfigurasi"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(cfg, f, indent=4)