# app/utils/data_processor.py
"""
Refactored: Semua operasi data dialihkan ke server via API.
Kompatibel dengan API lama agar tab tidak perlu diubah banyak.
"""
import pandas as pd
from app.api.client import get_client


def init_database():
    """Tidak lagi dipakai di client — semua inisialisasi di server"""
    pass


def get_dashboard_data() -> pd.DataFrame:
    """Ambil data via API dan return sebagai DataFrame"""
    client = get_client()
    result = client.get_data()
    if not result.get("success"):
        return pd.DataFrame()
    data = result.get("data", [])
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)


def save_manual_input(wt, sm, rf, temp):
    """Kirim input manual ke server"""
    client = get_client()
    result = client.save_manual(wt, sm, rf, temp)
    return result.get("success", False), result.get("message", "")


def read_and_validate_file(file_path: str):
    """Upload file ke server. Return (sukses, pesan, df)"""
    client = get_client()
    result = client.upload_file(file_path)
    df = None
    if result.get("success") and result.get("data"):
        try:
            df = pd.DataFrame(result["data"])
        except Exception:
            df = None
    return result.get("success", False), result.get("message", ""), df


# ==== TAMBAHAN UNTUK FITUR BARU ====
def sync_satellite_data(method: str):
    """Trigger sinkronisasi satelit"""
    client = get_client()
    return client.sync_satellite(method)


def run_forecast(model: str, steps: int = 7):
    """Trigger forecast"""
    client = get_client()
    return client.forecast(model, steps)


def calculate_index(wt, sm, rf, temp):
    """Trigger index calculation"""
    client = get_client()
    return client.calculate_index(wt, sm, rf, temp)


def get_config():
    client = get_client()
    return client.get_config()


def save_config(api_url, api_key):
    client = get_client()
    return client.save_config(api_url, api_key)