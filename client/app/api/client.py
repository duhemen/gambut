# app/api/client.py
"""HTTP Client untuk berkomunikasi dengan PeatFR Server"""
import os
import requests


DEFAULT_SERVER = os.environ.get(
    "PEATFR_SERVER_URL",
    "http://localhost:8000/api/v1"
)


class PeatFireClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or DEFAULT_SERVER
        self.timeout = 30
        self._token: str | None = None
        self._current_user: dict | None = None

    # ---------- Auth helpers ----------
    def _headers(self) -> dict:
        h = {}
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        return h

    @property
    def current_user(self) -> dict | None:
        return self._current_user

    @property
    def is_admin(self) -> bool:
        return bool(self._current_user and self._current_user.get("role") == "admin")

    def is_logged_in(self) -> bool:
        return self._token is not None

    # ---------- Low-level helpers ----------
    def _handle_error_response(self, r):
        """Terjemahkan status code jadi pesan user-friendly."""
        if r.status_code == 401:
            return {"success": False, "message": "Sesi berakhir. Silakan login ulang."}
        if r.status_code == 403:
            return {"success": False, "message": "Akses ditolak (butuh role admin)."}
        try:
            detail = r.json().get("detail", "")
        except Exception:
            detail = r.text[:200]
        return {"success": False, "message": f"HTTP {r.status_code}: {detail or 'Error'}"}

    def _get(self, path: str):
        try:
            r = requests.get(
                f"{self.base_url}{path}",
                headers=self._headers(),
                timeout=self.timeout,
            )
            if not r.ok:
                return self._handle_error_response(r)
            return r.json()
        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "Server tidak dapat dijangkau."}
        except requests.exceptions.Timeout:
            return {"success": False, "message": "Server timeout."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def _post(self, path: str, json_data=None, files=None):
        """Catatan: `json_data` (bukan `json`) supaya tidak shadow module json."""
        try:
            r = requests.post(
                f"{self.base_url}{path}",
                json=json_data, files=files,
                headers=self._headers(),
                timeout=self.timeout,
            )
            if not r.ok:
                return self._handle_error_response(r)
            return r.json()
        except requests.exceptions.ConnectionError:
            return {"success": False, "message": "Server tidak dapat dijangkau."}
        except requests.exceptions.Timeout:
            return {"success": False, "message": "Server timeout."}
        except Exception as e:
            return {"success": False, "message": str(e)}

    # ---------- Auth endpoints ----------
    def login(self, username: str, password: str) -> dict:
        result = self._post("/auth/login", json_data={
            "username": username, "password": password
        })
        if result.get("success") and result.get("access_token"):
            self._token = result["access_token"]
            self._current_user = result.get("user")
        return result

    def logout(self):
        self._token = None
        self._current_user = None

    def me(self):
        return self._get("/auth/me")

    # ---------- Endpoints ----------
    def health(self) -> bool:
        try:
            root = self.base_url.replace("/api/v1", "")
            r = requests.get(f"{root}/health", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def get_data(self):
        return self._get("/data")

    def save_manual(self, wt, sm, rf, temp):
        return self._post("/data", json_data={
            "wt": float(wt), "sm": float(sm),
            "rf": float(rf), "temp": float(temp)
        })

    def upload_file(self, file_path: str):
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                return self._post("/data/upload", files=files)
        except Exception as e:
            return {"success": False, "message": str(e)}

    def sync_satellite(self, method: str):
        return self._post("/satellite/sync", json_data={"method": method})

    def forecast(self, model: str, steps: int = 7):
        return self._post("/forecast", json_data={"model": model, "steps": steps})

    def calculate_index(self, wt, sm, rf, temp):
        return self._post("/index", json_data={
            "wt": float(wt), "sm": float(sm),
            "rf": float(rf), "temp": float(temp)
        })

    def get_config(self):
        return self._get("/config")

    def save_config(self, api_url, api_key):
        return self._post("/config", json_data={
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