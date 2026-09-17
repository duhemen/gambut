# app/gui/login_dialog.py
"""Dialog login PeatFR — versi cantik dengan gradient header, show/hide password, & animasi."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QGraphicsDropShadowEffect,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QBrush

from app.api.client import get_client


APP_VERSION = "v2.0"


class GradientHeader(QFrame):
    """Banner header dengan gradient horizontal biru → hijau."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(110)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, QColor("#0d6efd"))
        grad.setColorAt(1.0, QColor("#2ecc71"))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)

        # Rounded top corners saja
        painter.drawRoundedRect(self.rect(), 12, 12)
        # Tutup lengkungan bawah dengan rectangle
        painter.drawRect(0, self.height() // 2, self.width(), self.height() // 2)


class LoginDialog(QDialog):
    """Dialog login utama."""

    login_success = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login PeatFR")
        self.setFixedSize(440, 560)
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.WindowCloseButtonHint
        )

        self._password_visible = False
        self._build_ui()
        self._apply_styles()

        # Focus pertama
        self.txt_username.setFocus()

    # =========================================================
    # BUILD UI
    # =========================================================
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── 1. HEADER dengan gradient ───────────────────────
        header = GradientHeader()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(28, 22, 28, 16)
        header_layout.setSpacing(4)

        # Judul aplikasi
        self.lbl_title = QLabel("PeatFR")
        self.lbl_title.setStyleSheet(
            "color: white; font-size: 26px; font-weight: 800; "
            "background: transparent; letter-spacing: 1px;"
        )
        header_layout.addWidget(self.lbl_title)

        # Subjudul
        self.lbl_subtitle = QLabel("Peat Fire Risk Monitoring System")
        self.lbl_subtitle.setStyleSheet(
            "color: rgba(255,255,255,0.85); font-size: 12px; "
            "background: transparent;"
        )
        header_layout.addWidget(self.lbl_subtitle)

        root.addWidget(header)

        # ── 2. BODY card ────────────────────────────────────
        body = QFrame()
        body.setObjectName("BodyCard")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(36, 32, 36, 28)
        body_layout.setSpacing(14)

        # Greeting
        greeting = QLabel("Selamat datang kembali 👋")
        greeting.setStyleSheet(
            "color: #e9ecef; font-size: 15px; font-weight: 600;"
        )
        body_layout.addWidget(greeting)

        hint = QLabel("Silakan masuk untuk melanjutkan monitoring.")
        hint.setStyleSheet("color: #6c757d; font-size: 12px;")
        body_layout.addWidget(hint)

        body_layout.addSpacing(10)

        # ── Username ────────────────────────────────────────
        lbl_u = QLabel("USERNAME")
        lbl_u.setStyleSheet(
            "color: #6c757d; font-size: 10px; font-weight: 700; "
            "letter-spacing: 1.2px;"
        )
        body_layout.addWidget(lbl_u)

        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("mis. admin")
        self.txt_username.setMinimumHeight(42)
        self.txt_username.returnPressed.connect(self._focus_password)
        body_layout.addWidget(self.txt_username)

        # ── Password ────────────────────────────────────────
        lbl_p = QLabel("PASSWORD")
        lbl_p.setStyleSheet(
            "color: #6c757d; font-size: 10px; font-weight: 700; "
            "letter-spacing: 1.2px; margin-top: 4px;"
        )
        body_layout.addWidget(lbl_p)

        # Row: input + toggle visibility
        pass_row = QHBoxLayout()
        pass_row.setSpacing(8)

        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("••••••••")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setMinimumHeight(42)
        self.txt_password.returnPressed.connect(self.proses_login)
        pass_row.addWidget(self.txt_password, 1)

        self.btn_toggle = QPushButton("👁")
        self.btn_toggle.setFixedSize(42, 42)
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.setToolTip("Tampilkan / sembunyikan password")
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                background-color: #2c3034; color: #adb5bd;
                border: 1px solid #495057; border-radius: 6px;
                font-size: 15px;
            }
            QPushButton:hover { background-color: #343a40; color: #ffffff; }
        """)
        self.btn_toggle.clicked.connect(self._toggle_password)
        pass_row.addWidget(self.btn_toggle)

        body_layout.addLayout(pass_row)

        body_layout.addSpacing(6)

        # ── Status / error ──────────────────────────────────
        self.lbl_status = QLabel("")
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setMinimumHeight(34)
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet(
            "color: #e74c3c; font-size: 12px; background: transparent;"
        )
        body_layout.addWidget(self.lbl_status)

        # ── Tombol login ────────────────────────────────────
        self.btn_login = QPushButton("🔓  MASUK")
        self.btn_login.setMinimumHeight(46)
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.setDefault(True)
        self.btn_login.clicked.connect(self.proses_login)
        body_layout.addWidget(self.btn_login)

        # ── Footer: versi + bantuan ─────────────────────────
        footer_row = QHBoxLayout()
        footer_row.setContentsMargins(0, 10, 0, 0)

        lbl_ver = QLabel(f"PeatFR {APP_VERSION}")
        lbl_ver.setStyleSheet("color: #495057; font-size: 10px;")
        footer_row.addWidget(lbl_ver)

        footer_row.addStretch()

        lbl_help = QLabel("Butuh bantuan? Hubungi admin.")
        lbl_help.setStyleSheet("color: #495057; font-size: 10px;")
        footer_row.addWidget(lbl_help)

        body_layout.addLayout(footer_row)

        root.addWidget(body, 1)

        # ── Drop shadow di body ────────────────────────────
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 4)
        body.setGraphicsEffect(shadow)

        # Loading dots timer
        self._loading_step = 0
        self._loading_timer = QTimer()
        self._loading_timer.timeout.connect(self._animate_loading)

    # =========================================================
    # STYLES
    # =========================================================
    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #0f1113;
            }
            QFrame#BodyCard {
                background-color: #1a1c1e;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }
            QLabel {
                color: #e9ecef;
                background: transparent;
            }
            QLineEdit {
                background-color: #212529;
                color: #ffffff;
                border: 1px solid #343a40;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                selection-background-color: #0d6efd;
            }
            QLineEdit:hover {
                border: 1px solid #495057;
            }
            QLineEdit:focus {
                border: 1px solid #0d6efd;
                background-color: #262b2f;
            }
            QPushButton#LoginBtn, QPushButton {
                background-color: #0d6efd;
                color: #ffffff;
                font-weight: 700;
                font-size: 14px;
                border: none;
                border-radius: 8px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton:pressed {
                background-color: #0a53be;
            }
            QPushButton:disabled {
                background-color: #343a40;
                color: #6c757d;
            }
        """)

    # =========================================================
    # ACTIONS
    # =========================================================
    def _focus_password(self):
        self.txt_password.setFocus()

    def _toggle_password(self):
        self._password_visible = not self._password_visible
        if self._password_visible:
            self.txt_password.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_toggle.setText("🙈")
        else:
            self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_toggle.setText("👁")

    def _animate_loading(self):
        """Animasi titik loading: Masuk. → Masuk.. → Masuk..."""
        dots = "." * (self._loading_step % 4)
        self.btn_login.setText(f"⏳  Memproses{dots}")
        self._loading_step += 1

    def _set_loading(self, loading: bool):
        if loading:
            self._loading_step = 0
            self._loading_timer.start(300)
            self.btn_login.setEnabled(False)
            self.txt_username.setEnabled(False)
            self.txt_password.setEnabled(False)
            self.btn_toggle.setEnabled(False)
        else:
            self._loading_timer.stop()
            self.btn_login.setEnabled(True)
            self.btn_login.setText("🔓  MASUK")
            self.txt_username.setEnabled(True)
            self.txt_password.setEnabled(True)
            self.btn_toggle.setEnabled(True)

    def _show_error(self, message: str):
        self.lbl_status.setText(f"⚠️  {message}")
        self.lbl_status.setStyleSheet(
            "color: #e74c3c; font-size: 12px; background: transparent;"
        )

    def _show_success(self, message: str):
        self.lbl_status.setText(f"✅  {message}")
        self.lbl_status.setStyleSheet(
            "color: #2ecc71; font-size: 12px; background: transparent;"
        )

    # =========================================================
    # LOGIN
    # =========================================================
    def proses_login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text()

        if not username and not password:
            self._show_error("Username dan password wajib diisi.")
            self.txt_username.setFocus()
            return
        if not username:
            self._show_error("Username wajib diisi.")
            self.txt_username.setFocus()
            return
        if not password:
            self._show_error("Password wajib diisi.")
            self.txt_password.setFocus()
            return

        self.lbl_status.setText("")
        self._set_loading(True)

        client = get_client()
        result = client.login(username, password)

        if result.get("success"):
            user = result.get("user", {})
            self._show_success(f"Selamat datang, {user.get('full_name') or username}!")
            # Delay kecil biar user lihat pesan sukses
            QTimer.singleShot(500, self.accept)
            self.login_success.emit(user)
        else:
            self._set_loading(False)
            msg = result.get("message", "Login gagal.")
            self._show_error(msg)
            self.txt_password.clear()
            self.txt_password.setFocus()