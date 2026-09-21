# client/gui/login_dialog.py
"""Dialog login sebelum masuk ke aplikasi utama."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt

from client.api.client import get_client


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔐 Login PeatFR")
        self.setFixedSize(420, 400)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)

        # Logo
        logo = QLabel("🔥")
        logo.setStyleSheet("font-size: 48px; background: transparent;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        # Title
        title = QLabel("PEAT FIRE RISK")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Masuk untuk melanjutkan monitoring lahan gambut")
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(10)

        # Username
        lbl_user = QLabel("Username")
        lbl_user.setObjectName("MutedLabel")
        layout.addWidget(lbl_user)
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Masukkan username")
        self.txt_username.returnPressed.connect(self._focus_password)
        layout.addWidget(self.txt_username)

        # Password
        lbl_pass = QLabel("Password")
        lbl_pass.setObjectName("MutedLabel")
        layout.addWidget(lbl_pass)
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("Masukkan password")
        self.txt_password.returnPressed.connect(self.proses_login)
        layout.addWidget(self.txt_password)

        # Status
        self.lbl_status = QLabel("")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet(
            "color: #ef4444; font-size: 12px; padding: 4px; background: transparent;"
        )
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