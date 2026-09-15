# app/api/client.py
"""HTTP Client untuk berkomunikasi dengan PeatFR Server"""
import os
import requests


DEFAULT_SERVER = os.environ.get(
    "PEATFR_SERVER_URL",
    "http://localhost:8000/api/v1"
)


class PeatFireClient:
    """Singleton HTTP client untuk server PeatFR"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or DEFAULT_SERVER
        self.timeout = 30

    # ---------- Low-level helpers ----------
    def _get(self, path: str):
        try:
            r = requests.get(f"{self.base_url}{path}", timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.ConnectionError:
            return {"success": False,
                    "message": "Server tidak dapat dijangkau. Periksa koneksi."}
        except requests.exceptions.Timeout:
            return {"success": False, "message": "Server timeout."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def _post(self, path: str, json=None, files=None):
        try:
            r = requests.post(
                f"{self.base_url}{path}",
                json=json, files=files, timeout=self.timeout
            )
            r.raise_for_status()
            return r.json()
        except requests.exceptions.ConnectionError:
            return {"success": False,
                    "message": "Server tidak dapat dijangkau."}
        except requests.exceptions.Timeout:
            return {"success": False, "message": "Server timeout."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    # ---------- Endpoints ----------
    def health(self) -> bool:
        """Cek apakah server hidup"""
        try:
            root = self.base_url.replace("/api/v1", "")
            r = requests.get(f"{root}/health", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def get_data(self):
        """Ambil semua data dari server"""
        return self._get("/data")

    def save_manual(self, wt, sm, rf, temp):
        """Simpan input manual"""
        return self._post("/data", json={
            "wt": float(wt), "sm": float(sm),
            "rf": float(rf), "temp": float(temp)
        })

    def upload_file(self, file_path: str):
        """Upload file CSV/Excel ke server"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                return self._post("/data/upload", files=files)
        except Exception as e:
            return {"success": False, "message": str(e)}

    def sync_satellite(self, method: str):
        """Trigger sinkronisasi satelit di server"""
        return self._post("/satellite/sync", json={"method": method})

    def forecast(self, model: str, steps: int = 7):
        """Jalankan forecast"""
        return self._post("/forecast", json={"model": model, "steps": steps})

    def calculate_index(self, wt, sm, rf, temp):
        """Hitung indeks kerawanan Nelder-Mead"""
        return self._post("/index", json={
            "wt": float(wt), "sm": float(sm),
            "rf": float(rf), "temp": float(temp)
        })

    def get_config(self):
        return self._get("/config")

    def save_config(self, api_url, api_key):
        return self._post("/config", json={
            "api_url": api_url, "api_key": api_key
        })


# Singleton
_client_instance = None

def get_client() -> PeatFireClient:
    global _client_instance
    if _client_instance is None:
        _client_instance = PeatFireClient()
    return _client_instance


def set_server_url(url: str):
    """Ganti base URL server saat runtime"""
    global _client_instance
    _client_instance = PeatFireClient(base_url=url)