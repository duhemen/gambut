# main.py
import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox

from app.gui.main_window import PeatFireApp
from app.api.client import get_client


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Cek koneksi server
    client = get_client()
    if not client.health():
        reply = QMessageBox.question(
            None,
            "⚠️ Server Tidak Terhubung",
            f"Tidak dapat terhubung ke server:\n<b>{client.base_url}</b>\n\n"
            "Pastikan server sudah berjalan dengan:<br>"
            "<code>python -m uvicorn server.main:app --host 0.0.0.0 --port 8000</code><br><br>"
            "Lanjutkan dalam mode offline? (fitur terbatas)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        if reply == QMessageBox.StandardButton.No:
            sys.exit(1)

    window = PeatFireApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()