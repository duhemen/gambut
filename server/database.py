# server/database.py
"""Lapisan database (CSV-based) untuk server — Hybrid Ready"""
import os
import json
from pathlib import Path
from datetime import datetime
from threading import Lock

import pandas as pd

from server.auth.password import hash_password, verify_password

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("GAMBUT_DATA_DIR", BASE_DIR / "data"))
DB_PATH = DATA_DIR / "database_gambut.csv"
SATELLITE_PATH = DATA_DIR / "sample_satellite.csv"
CONFIG_PATH = DATA_DIR / "config.json"
USERS_PATH = DATA_DIR / "users.csv"

_lock = Lock()
_user_lock = Lock()
REQUIRED_COLS = ['tanggal', 'region', 'wt', 'sm', 'rf', 'temp']
USER_COLS = ["id", "username", "password_hash", "full_name", "role", "created_at"]


def init_database():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        pd.DataFrame(columns=REQUIRED_COLS).to_csv(DB_PATH, index=False)


def init_satellite_file():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SATELLITE_PATH.exists():
        dummy = pd.DataFrame([
            {"tanggal": "2026-09-10", "wt": -5.0, "sm": 55.0, "rf": 12.5, "temp": 28.5},
            {"tanggal": "2026-09-11", "wt": None, "sm": 50.0, "rf": 4.2, "temp": 29.8},
            {"tanggal": "2026-09-12", "wt": -11.5, "sm": None, "rf": 0.0, "temp": 31.2},
            {"tanggal": "2026-09-13", "wt": -13.0, "sm": 42.0, "rf": 0.0, "temp": None},
            {"tanggal": "2026-09-14", "wt": None, "sm": 40.0, "rf": 0.0, "temp": 32.2},
            {"tanggal": "2026-09-15", "wt": -15.2, "sm": 38.5, "rf": 0.0, "temp": 33.5},
        ])
        dummy.to_csv(SATELLITE_PATH, index=False)


def _init_users():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not USERS_PATH.exists():
        pd.DataFrame(columns=USER_COLS).to_csv(USERS_PATH, index=False)


# ============ PEAT DATA ============
def get_all_data() -> pd.DataFrame:
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
    df = get_all_data()
    if df.empty:
        return df
    return df.sort_values(by='tanggal').reset_index(drop=True)


def save_row(row: dict) -> int:
    """Simpan/upsert satu baris ke database."""
    init_database()
    with _lock:
        df = pd.read_csv(DB_PATH)
        new_df = pd.DataFrame([row])
        if df.empty:
            df = new_df
        else:
            df = pd.concat([df, new_df], ignore_index=True)

        # ⬇️ Fix: dedupe by (tanggal, region), bukan tanggal saja
        dedupe_cols = ['tanggal', 'region'] if 'region' in df.columns else ['tanggal']
        df = df.drop_duplicates(subset=dedupe_cols, keep='last')

        df.to_csv(DB_PATH, index=False)
        return len(df)

def save_many(rows: list) -> int:
    """Bulk insert."""
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

        # ⬇️ Fix: dedupe by (tanggal, region)
        dedupe_cols = ['tanggal', 'region'] if 'region' in df.columns else ['tanggal']
        df = df.drop_duplicates(subset=dedupe_cols, keep='last')

        df.to_csv(DB_PATH, index=False)
        return len(rows)

def get_satellite_raw() -> pd.DataFrame:
    init_satellite_file()
    return pd.read_csv(SATELLITE_PATH)


# ============ CONFIG ============
def get_config() -> dict:
    if not CONFIG_PATH.exists():
        return {"api_url": "", "api_key": ""}
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"api_url": "", "api_key": ""}


def save_config(cfg: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=4)


# ============ USER MANAGEMENT ============
def _read_users() -> pd.DataFrame:
    _init_users()
    try:
        df = pd.read_csv(USERS_PATH)
        df = df.fillna("")
        return df
    except Exception:
        return pd.DataFrame(columns=USER_COLS)


def _write_users(df: pd.DataFrame):
    df.to_csv(USERS_PATH, index=False)


def get_user_by_username(username: str) -> dict | None:
    df = _read_users()
    if df.empty:
        return None
    match = df[df["username"] == username]
    if match.empty:
        return None
    row = match.iloc[0].to_dict()
    try:
        row["id"] = int(row["id"])
    except (ValueError, TypeError):
        row["id"] = 0
    return row


def create_user(username: str, password: str,
                full_name: str = "", role: str = "petugas") -> dict:
    with _user_lock:
        df = _read_users()
        if not df.empty and (df["username"] == username).any():
            raise ValueError(f"Username '{username}' sudah dipakai.")

        if df.empty:
            new_id = 1
        else:
            try:
                new_id = int(df["id"].astype(int).max()) + 1
            except (ValueError, TypeError):
                new_id = len(df) + 1

        new_user = {
            "id": new_id,
            "username": username,
            "password_hash": hash_password(password),
            "full_name": full_name or "",
            "role": role,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
        _write_users(df)
        return new_user


def authenticate_user(username: str, password: str) -> dict | None:
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user


def list_users() -> list[dict]:
    df = _read_users()
    if df.empty:
        return []
    return [
        {k: v for k, v in row.items() if k != "password_hash"}
        for row in df.to_dict(orient="records")
    ]