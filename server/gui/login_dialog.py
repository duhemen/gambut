# app/gui/login_dialog.py
"""Dialog login sebelum masuk ke aplikasi utama."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt

from app.api.client import get_client


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔐 Login PeatFR")
        self.setFixedSize(420, 380)
        self.setStyleSheet("""
            QDialog { background-color: #1a1c1e; }
            QLabel { color: #ffffff; }
            QLineEdit {
                background-color: #2c3034; color: #ffffff;
                border: 1px solid #495057; border-radius: 6px;
                padding: 10px; font-size: 13px;
            }
            QLineEdit:focus { border: 1px solid #0d6efd; }
            QPushButton {
                background-color: #0d6efd; color: white;
                font-weight: bold; padding: 12px;
                border-radius: 6px; font-size: 14px;
            }
            QPushButton:hover { background-color: #0b5ed7; }
            QPushButton:disabled { background-color: #495057; color: #adb5bd; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Header
        logo = QLabel("🔥")
        logo.setStyleSheet("font-size: 48px;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        title = QLabel("PEAT FIRE RISK")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #0d6efd;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Masuk untuk melanjutkan monitoring lahan gambut")
        subtitle.setStyleSheet("color: #adb5bd; font-size: 12px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # Username
        lbl_user = QLabel("Username")
        lbl_user.setStyleSheet("color: #adb5bd; font-size: 12px;")
        layout.addWidget(lbl_user)
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Masukkan username")
        self.txt_username.returnPressed.connect(self._focus_password)
        layout.addWidget(self.txt_username)

        # Password
        lbl_pass = QLabel("Password")
        lbl_pass.setStyleSheet("color: #adb5bd; font-size: 12px;")
        layout.addWidget(lbl_pass)
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("Masukkan password")
        self.txt_password.returnPressed.connect(self.proses_login)
        layout.addWidget(self.txt_password)

        # Status label
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet(
            "color: #e74c3c; font-size: 12px; padding: 5px;"
        )
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_status)

        layout.addStretch()

        # Button
        self.btn_login = QPushButton("🔓  MASUK")
        self.btn_login.clicked.connect(self.proses_login)
        layout.addWidget(self.btn_login)

        self.txt_username.setFocus()

    def _focus_password(self):
        self.txt_password.setFocus()

    def proses_login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text()

        if not username or not password:
            self.lbl_status.setText("⚠️ Username dan password wajib diisi.")
            return

        self.btn_login.setEnabled(False)
        self.btn_login.setText("⏳ Memproses...")
        self.lbl_status.setText("")

        client = get_client()
        result = client.login(username, password)

        if result.get("success"):
            self.accept()
        else:
            self.btn_login.setEnabled(True)
            self.btn_login.setText("🔓  MASUK")
            self.lbl_status.setText(f"❌ {result.get('message', 'Login gagal.')}")
            self.txt_password.clear()
            self.txt_password.setFocus()