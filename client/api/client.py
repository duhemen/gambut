# client/api/client.py
"""HTTP client untuk komunikasi dengan FastAPI server."""
import requests
from client.config import SERVER_URL, REQUEST_TIMEOUT


class ApiClient:
    def __init__(self):
        self.base_url = SERVER_URL
        self.token = None
        self.user = None

    def _headers(self, skip_content_type: bool = False):
        """Return headers. Kalau skip_content_type=True, jangan set Content-Type."""
        headers = {}
        if not skip_content_type:
            headers["Content-Type"] = "application/json"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    # ============================================================
    # HEALTH
    # ============================================================
    def health(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/health", timeout=5)
            return r.status_code == 200
        except requests.exceptions.RequestException:
            return False

    # ============================================================
    # AUTH
    # ============================================================
    def login(self, username: str, password: str) -> dict:
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"username": username, "password": password},
                timeout=REQUEST_TIMEOUT,
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user = data.get("user")
                return {
                    "success": True,
                    "message": data.get("message", "Login berhasil"),
                    "user": self.user,
                }
            try:
                detail = response.json().get("detail", "Login gagal")
            except Exception:
                detail = f"HTTP {response.status_code}"
            return {"success": False, "message": detail}
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"Tidak dapat terhubung: {e}"}

    def logout(self):
        self.token = None
        self.user = None

    # ============================================================
    # HTTP METHODS
    # ============================================================
    def get(self, path: str, **kwargs):
        return requests.get(
            f"{self.base_url}{path}",
            headers=self._headers(),
            timeout=REQUEST_TIMEOUT,
            **kwargs,
        )

    def post(self, path: str, json=None, files=None, data=None, **kwargs):
        """
        POST request. Auto-handle multipart.
        Kalau `files` diisi, jangan set Content-Type (biar requests yang atur).
        """
        if files is not None:
            headers = self._headers(skip_content_type=True)
        else:
            headers = self._headers()

        return requests.post(
            f"{self.base_url}{path}",
            headers=headers,
            json=json,
            files=files,
            data=data,
            timeout=REQUEST_TIMEOUT,
            **kwargs,
        )

    def put(self, path: str, json=None, **kwargs):
        return requests.put(
            f"{self.base_url}{path}",
            headers=self._headers(),
            json=json,
            timeout=REQUEST_TIMEOUT,
            **kwargs,
        )

    def delete(self, path: str, **kwargs):
        return requests.delete(
            f"{self.base_url}{path}",
            headers=self._headers(),
            timeout=REQUEST_TIMEOUT,
            **kwargs,
        )


_client = None


def get_client() -> ApiClient:
    global _client
    if _client is None:
        _client = ApiClient()
    return _client