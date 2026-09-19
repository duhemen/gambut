# client/main.py
"""
PeatFR Client — Entry Point.

Urutan startup:
1. Set tema (dark/light)
2. Cek koneksi server (health check)
3. Kalau server hidup → WAJIB login
4. Kalau server mati → tawarkan mode offline
5. Buka main window
"""
import sys

from PyQt6.QtWidgets import QApplication, QMessageBox

from client.gui.theme import apply_theme, ThemeMode
from client.gui.login_dialog import LoginDialog
from client.gui.main_window import PeatFireApp
from client.api.client import get_client
from client.config import SERVER_URL


def main():
    # ─── 1. Setup QApplication ───────────────────────────────
    app = QApplication(sys.argv)
    app.setApplicationName("PeatFR")
    app.setOrganizationName("PeatFR")
    app.setStyle("Fusion")  # base style, QSS kita override di atasnya

    # ─── 2. Terapkan tema ────────────────────────────────────
    # Ganti ke ThemeMode.LIGHT kalau mau mode terang
    apply_theme(app, ThemeMode.DARK)

    # ─── 3. Cek koneksi server ───────────────────────────────
    client = get_client()
    server_online = client.health()

    if not server_online:
        reply = QMessageBox.question(
            None,
            "⚠️ Server Tidak Terhubung",
            (
                f"Tidak dapat terhubung ke server:<br>"
                f"<b>{SERVER_URL}</b><br><br>"
                "Pastikan server sudah berjalan dengan:<br>"
                "<code>python run_hybrid_server.py</code><br>"
                "atau:<br>"
                "<code>python -m uvicorn server.main:app --host 0.0.0.0 --port 8000</code><br><br>"
                "Lanjutkan dalam <b>mode offline</b>? (fitur terbatas)"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply == QMessageBox.StandardButton.No:
            sys.exit(1)
        # Kalau user pilih Yes → lanjut dengan mode offline
        print("⚠️  [CLIENT] Berjalan dalam mode offline.")
    else:
        # ─── 4. Server hidup → WAJIB login ───────────────────
        login = LoginDialog()
        if login.exec() != LoginDialog.DialogCode.Accepted:
            sys.exit(0)
        print(f"✅ [CLIENT] Login berhasil sebagai: {client.user.get('username')}")

    # ─── 5. Buka main window ─────────────────────────────────
    window = PeatFireApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()