# server/database.py
"""Lapisan database (CSV-based) untuk server — Multi-Level Region Ready"""
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

# ══════════════════════════════════════════════════════════════
# SCHEMA — 5-Level Region Support
# ══════════════════════════════════════════════════════════════
# Kolom lengkap (setelah migrasi):
#   tanggal | region | province | regency | district | village | wt | sm | rf | temp
REQUIRED_COLS = [
    'tanggal',
    'region',
    'province',
    'regency',
    'district',
    'village',
    'wt', 'sm', 'rf', 'temp',
]

# Kolom untuk dedupe (composite key)
DEDUPE_COLS = ['tanggal', 'region', 'province', 'regency', 'district', 'village']

# Kolom yang perlu ditambah kalau database lama
NEW_COLUMNS_V2 = ['province', 'regency', 'district', 'village']

USER_COLS = ["id", "username", "password_hash", "full_name", "role",
             "assigned_region", "assigned_province", "assigned_regency", "assigned_district", "assigned_village",
             "created_at"]


# ══════════════════════════════════════════════════════════════
# INIT & MIGRATION
# ══════════════════════════════════════════════════════════════
def _migrate_schema():
    """
    Auto-migrate database CSV ke schema terbaru (v2 — 5-level region).
    Kalau kolom baru belum ada, tambahkan dengan nilai default.
    """
    if not DB_PATH.exists():
        return

    try:
        df = pd.read_csv(DB_PATH)
    except Exception as e:
        print(f"⚠️ [DB] Gagal baca CSV untuk migrasi: {e}")
        return

    changed = False

    # Cek kolom yang perlu ditambah
    for col in NEW_COLUMNS_V2:
        if col not in df.columns:
            # Posisi: setelah 'region'
            if 'region' in df.columns:
                insert_pos = df.columns.get_loc('region') + 1
                df.insert(insert_pos, col, "")
            else:
                df[col] = ""
            changed = True
            print(f"🔧 [DB] Kolom '{col}' ditambahkan (migrasi v2)")

    # Pastikan semua REQUIRED_COLS ada
    for col in REQUIRED_COLS:
        if col not in df.columns:
            df[col] = "" if col not in ['wt', 'sm', 'rf', 'temp'] else 0.0
            changed = True

    # Reorder kolom sesuai schema
    existing_cols = [c for c in REQUIRED_COLS if c in df.columns]
    extra_cols = [c for c in df.columns if c not in REQUIRED_COLS]
    df = df[existing_cols + extra_cols]

    if changed:
        # Backup dulu
        backup_path = DB_PATH.with_suffix('.csv.bak')
        try:
            df.to_csv(backup_path, index=False)
        except Exception:
            pass

        df.to_csv(DB_PATH, index=False)
        print(f"✅ [DB] Migrasi selesai. Backup: {backup_path.name}")


def init_database():
    """Pastikan file database ada, dan migrasi schema kalau perlu."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not DB_PATH.exists():
        # Fresh install — buat langsung dengan schema lengkap
        pd.DataFrame(columns=REQUIRED_COLS).to_csv(DB_PATH, index=False)
        print("✅ [DB] Database baru dibuat (schema v2)")
    else:
        # Existing — cek migrasi
        _migrate_schema()


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


# ══════════════════════════════════════════════════════════════
# PEAT DATA
# ══════════════════════════════════════════════════════════════
def _normalize_row(row: dict) -> dict:
    """Pastikan row punya semua REQUIRED_COLS. Isi default kalau tidak ada."""
    normalized = {}
    for col in REQUIRED_COLS:
        if col in row:
            normalized[col] = row[col]
        elif col in ['wt', 'sm', 'rf', 'temp']:
            normalized[col] = 0.0
        else:
            normalized[col] = ""
    # Tambah kolom tambahan yang tidak di REQUIRED_COLS (biar fleksibel)
    for k, v in row.items():
        if k not in normalized:
            normalized[k] = v
    return normalized


def get_all_data() -> pd.DataFrame:
    """Ambil semua data, sorted dari terbaru."""
    init_database()
    with _lock:
        try:
            df = pd.read_csv(DB_PATH)
            if df.empty:
                return pd.DataFrame(columns=REQUIRED_COLS)

            # Pastikan semua kolom ada
            for col in REQUIRED_COLS:
                if col not in df.columns:
                    df[col] = "" if col not in ['wt', 'sm', 'rf', 'temp'] else 0.0

            # Isi NaN dengan string kosong
            df = df.fillna("")

            df = df.sort_values(by='tanggal', ascending=False).reset_index(drop=True)
            return df
        except Exception as e:
            print(f"⚠️ [DB] Gagal baca data: {e}")
            return pd.DataFrame(columns=REQUIRED_COLS)


def get_data_chronological() -> pd.DataFrame:
    df = get_all_data()
    if df.empty:
        return df
    return df.sort_values(by='tanggal').reset_index(drop=True)


def save_row(row: dict) -> int:
    """Simpan/upsert satu baris ke database."""
    init_database()
    row = _normalize_row(row)

    with _lock:
        df = pd.read_csv(DB_PATH)

        # Pastikan kolom baru ada
        for col in REQUIRED_COLS:
            if col not in df.columns:
                df[col] = "" if col not in ['wt', 'sm', 'rf', 'temp'] else 0.0

        new_df = pd.DataFrame([row])

        if df.empty:
            df = new_df
        else:
            df = pd.concat([df, new_df], ignore_index=True)

        # ⬇️ Dedupe by (tanggal + lokasi lengkap), bukan tanggal saja
        dedupe_cols = [c for c in DEDUPE_COLS if c in df.columns]
        if dedupe_cols:
            df = df.drop_duplicates(subset=dedupe_cols, keep='last')
        else:
            df = df.drop_duplicates(subset=['tanggal'], keep='last')

        df.to_csv(DB_PATH, index=False)
        return len(df)


def save_many(rows: list) -> int:
    """Bulk insert."""
    init_database()
    if not rows:
        return 0

    rows = [_normalize_row(r) for r in rows]

    with _lock:
        df = pd.read_csv(DB_PATH)

        # Pastikan kolom baru ada
        for col in REQUIRED_COLS:
            if col not in df.columns:
                df[col] = "" if col not in ['wt', 'sm', 'rf', 'temp'] else 0.0

        new_df = pd.DataFrame(rows)

        if df.empty:
            df = new_df
        else:
            df = pd.concat([df, new_df], ignore_index=True)

        # ⬇️ Dedupe by (tanggal + lokasi lengkap)
        dedupe_cols = [c for c in DEDUPE_COLS if c in df.columns]
        if dedupe_cols:
            df = df.drop_duplicates(subset=dedupe_cols, keep='last')
        else:
            df = df.drop_duplicates(subset=['tanggal'], keep='last')

        df.to_csv(DB_PATH, index=False)
        return len(rows)


def get_satellite_raw() -> pd.DataFrame:
    init_satellite_file()
    return pd.read_csv(SATELLITE_PATH)


# ══════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════
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


# ══════════════════════════════════════════════════════════════
# USER MANAGEMENT
# ══════════════════════════════════════════════════════════════
def _read_users() -> pd.DataFrame:
    _init_users()
    try:
        df = pd.read_csv(USERS_PATH)
        # Auto-migrate: tambah kolom baru kalau belum ada
        new_cols = ["assigned_region", "assigned_province", "assigned_regency"]
        for col in new_cols:
            if col not in df.columns:
                df[col] = ""
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
                full_name: str = "", role: str = "petugas",
                assigned_region: str = "",
                assigned_province: str = "",
                assigned_regency: str = "") -> dict:
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
            "assigned_region": assigned_region or "",
            "assigned_province": assigned_province or "",
            "assigned_regency": assigned_regency or "",
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