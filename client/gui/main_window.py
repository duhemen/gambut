# client/gui/main_window.py
"""
PeatFR Main Window.

Layout:
┌──────────────┬──────────────────────────────────────┐
│              │  HEADER (judul + user badge)         │
│   SIDEBAR    ├──────────────────────────────────────┤
│   (logo +    │                                      │
│    menu +    │  CONTENT (QStackedWidget)            │
│    user)     │                                      │
│              │                                      │
└──────────────┴──────────────────────────────────────┘
"""
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QStackedWidget, QFrame, QMessageBox, QSizePolicy
)

from client.api.client import get_client
from client.gui.theme import AuroraBackground, get_palette
from client.gui.tabs import (
    DashboardTab,
    ManualInputTab,
    UploadTab,
    SettingTab,
    AnomalyTab,
    SchedulerTab,
    PlaceholderTab,
)


# ============================================================
# SIDEBAR BUTTON
# ============================================================
class SidebarButton(QPushButton):
    """Tombol menu di sidebar."""

    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setText(f"  {icon}   {text}")
        self.setMinimumHeight(44)
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #cbd5e1;
                border: none;
                border-radius: 8px;
                text-align: left;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(51, 65, 85, 0.5);
                color: #f8fafc;
            }
            QPushButton:checked {
                background: rgba(16, 185, 129, 0.15);
                color: #10b981;
                font-weight: 700;
                border-left: 3px solid #10b981;
            }
        """)


# ============================================================
# MAIN WINDOW
# ============================================================
class PeatFireApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔥 PeatFR — Peat Fire Risk Monitoring")
        self.setMinimumSize(1200, 720)
        self.resize(1280, 760)

        self.client = get_client()
        self._build_ui()
        self._load_user_info()

    # ============================================================
    # UI
    # ============================================================
    def _build_ui(self):
        # ─── Central widget dengan Aurora background ──────────
        central = AuroraBackground()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ─── SIDEBAR ──────────────────────────────────────────
        sidebar = self._build_sidebar()
        main_layout.addWidget(sidebar)

        # ─── RIGHT PANE (header + content) ────────────────────
        right_pane = QWidget()
        right_pane.setStyleSheet("background: transparent;")
        right_layout = QVBoxLayout(right_pane)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Header
        header = self._build_header()
        right_layout.addWidget(header)

        # Content stack
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")
        right_layout.addWidget(self.stack)

        # Buat tab-tab
        self.tabs = {}
        self._register_tabs()

        main_layout.addWidget(right_pane, stretch=1)

        # Pilih menu default
        self._select_menu("dashboard")

    # ─── Sidebar ──────────────────────────────────────────────
    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("""
            QFrame {
                background: rgba(17, 24, 39, 0.85);
                border-right: 1px solid #1e293b;
            }
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(6)

        # Logo + title
        logo_row = QHBoxLayout()
        logo_row.setSpacing(10)

        logo = QLabel("🔥")
        logo.setStyleSheet("font-size: 28px; background: transparent;")
        logo_row.addWidget(logo)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        t1 = QLabel("PeatFR")
        t1.setStyleSheet(
            "color: #f8fafc; font-size: 16px; font-weight: 700; "
            "background: transparent;"
        )
        t2 = QLabel("Fire Risk Monitor")
        t2.setStyleSheet(
            "color: #64748b; font-size: 10px; letter-spacing: 0.5px; "
            "background: transparent;"
        )
        title_col.addWidget(t1)
        title_col.addWidget(t2)
        logo_row.addLayout(title_col)
        logo_row.addStretch()

        layout.addLayout(logo_row)
        layout.addSpacing(20)

        # Section label
        sec = QLabel("MENU UTAMA")
        sec.setStyleSheet(
            "color: #475569; font-size: 10px; font-weight: 700; "
            "letter-spacing: 1.5px; background: transparent; "
            "padding: 4px 8px;"
        )
        layout.addWidget(sec)

        # Menu buttons
        self.menu_buttons = {}
        menu_items = [
            ("dashboard", "📊", "Dashboard"),
            ("manual",    "✍️", "Input Manual"),
            ("upload",    "📁", "Upload Data"),
            ("anomaly",   "🔍", "Anomali"),
            ("scheduler", "⏰", "Scheduler"),
            ("setting",   "⚙️", "Pengaturan"),
        ]
        for key, icon, label in menu_items:
            btn = SidebarButton(icon, label)
            btn.clicked.connect(lambda _, k=key: self._select_menu(k))
            layout.addWidget(btn)
            self.menu_buttons[key] = btn

        layout.addStretch()

        # Info koneksi server (bawah)
        self.lbl_server = QLabel("🟢 Server: Connected")
        self.lbl_server.setStyleSheet(
            "color: #10b981; font-size: 11px; padding: 8px; "
            "background: rgba(16, 185, 129, 0.1); "
            "border-radius: 6px;"
        )
        self.lbl_server.setWordWrap(True)
        layout.addWidget(self.lbl_server)

        return sidebar

    # ─── Header ───────────────────────────────────────────────
    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("""
            QFrame {
                background: rgba(17, 24, 39, 0.6);
                border-bottom: 1px solid #1e293b;
            }
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(28, 12, 28, 12)
        layout.setSpacing(12)

        # Judul halaman (dinamis)
        self.lbl_page_title = QLabel("Dashboard")
        self.lbl_page_title.setStyleSheet(
            "color: #f8fafc; font-size: 18px; font-weight: 700; "
            "background: transparent;"
        )
        layout.addWidget(self.lbl_page_title)

        layout.addStretch()

        # User badge
        self.lbl_user = QLabel("👤  —")
        self.lbl_user.setStyleSheet(
            "color: #cbd5e1; font-size: 12px; padding: 8px 14px; "
            "background: rgba(30, 41, 59, 0.8); "
            "border: 1px solid #334155; border-radius: 6px;"
        )
        layout.addWidget(self.lbl_user)

        # Tombol logout
        btn_logout = QPushButton("Logout")
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #ef4444;
                border: 1px solid #ef4444;
                border-radius: 6px;
                padding: 7px 16px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.15);
            }
        """)
        btn_logout.clicked.connect(self._handle_logout)
        layout.addWidget(btn_logout)

        return header

    # ─── Tab Registration ─────────────────────────────────────
    def _register_tabs(self):
        """Daftarkan semua tab ke QStackedWidget."""
        from client.gui.tabs import (
            DashboardTab, ManualInputTab, UploadTab, SettingTab
        )

        # Dashboard
        self.tabs["dashboard"] = DashboardTab()
        self.stack.addWidget(self.tabs["dashboard"])

        # Input Manual
        self.tabs["manual"] = ManualInputTab()
        self.tabs["manual"].data_saved.connect(self._refresh_dashboard)
        self.stack.addWidget(self.tabs["manual"])

        # Upload
        self.tabs["upload"] = UploadTab()
        self.tabs["upload"].data_uploaded.connect(self._refresh_dashboard)
        self.stack.addWidget(self.tabs["upload"])

        # Anomali
        self.tabs["anomaly"] = AnomalyTab()
        self.stack.addWidget(self.tabs["anomaly"])

        # Scheduler
        from client.gui.tabs import SchedulerTab
        self.tabs["scheduler"] = SchedulerTab()
        self.stack.addWidget(self.tabs["scheduler"])

        # Pengaturan
        self.tabs["setting"] = SettingTab()
        self.stack.addWidget(self.tabs["setting"])


    def _refresh_dashboard(self):
        """Refresh dashboard setelah data baru masuk."""
        if "dashboard" in self.tabs:
            self.tabs["dashboard"].refresh()

    # ============================================================
    # ACTIONS
    # ============================================================
    def _select_menu(self, key: str):
        """Ganti tab aktif."""
        if key not in self.tabs:
            return

        self.stack.setCurrentWidget(self.tabs[key])

        # Update state tombol
        for k, btn in self.menu_buttons.items():
            btn.setChecked(k == key)

        # Update judul header
        titles = {
            "dashboard": "Dashboard",
            "manual":    "Input Manual",
            "upload":    "Upload Data",
            "setting":   "Pengaturan",
        }
        self.lbl_page_title.setText(titles.get(key, "PeatFR"))

    def _load_user_info(self):
        """Tampilkan info user yang sedang login."""
        user = self.client.user
        if user:
            name = user.get("full_name") or user.get("username", "User")
            role = user.get("role", "").upper()
            self.lbl_user.setText(f"👤  {name}  ·  {role}")
        else:
            self.lbl_user.setText("👤  Guest")

    def _handle_logout(self):
        reply = QMessageBox.question(
            self,
            "Konfirmasi Logout",
            "Yakin ingin keluar dari aplikasi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.client.logout()
            self.close()