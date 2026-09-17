# main.py
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox

from app.gui.main_window import PeatFireApp
from app.gui.login_dialog import LoginDialog
from app.api.client import get_client


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    client = get_client()

    # 1. Cek koneksi server
    if not client.health():
        reply = QMessageBox.question(
            None,
            "⚠️ Server Tidak Terhubung",
            f"Tidak dapat terhubung ke server:\n<b>{client.base_url}</b>\n\n"
            "Pastikan server sudah berjalan dengan:<br>"
            "<code>python -m uvicorn server.main:app --host 0.0.0.0 --port 8000</code><br><br>"
            "Lanjutkan dalam mode offline? (fitur terbatas)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply == QMessageBox.StandardButton.No:
            sys.exit(1)
    else:
        # 2. WAJIB login kalau server hidup
        login = LoginDialog()
        if login.exec() != LoginDialog.DialogCode.Accepted:
            sys.exit(0)

    # 3. Buka window utama
    window = PeatFireApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()