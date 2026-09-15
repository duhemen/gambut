# app/gui/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QListWidget,
    QStackedWidget, QFrame, QStatusBar, QLabel
)
from PyQt6.QtCore import Qt, QTimer

from app.gui.tabs.tab_dashboard import DashboardTab
from app.gui.tabs.tab_default import DefaultTab
from app.gui.tabs.tab_manual import ManualTab
from app.gui.tabs.tab_upload import UploadTab
from app.gui.tabs.tab_setting import SettingTab
from app.api.client import get_client


class PeatFireApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔥 PEAT FIRE RISK APP (peatfr-pyqt) - Client/Server")
        self.resize(1200, 780)

        self.setStyleSheet("""
            QMainWindow { background-color: #1a1c1e; }
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # === SIDEBAR ===
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(260)
        self.sidebar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.sidebar.addItems([
            " 📊   Dashboard Ringkasan",
            " 📡   Data Bawaan Satelit",
            " ✍️   Form Input Manual",
            " 📁   Unggah Berkas Excel/CSV",
            " ⚙️   Pengaturan Aplikasi"
        ])
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #212529;
                border: 1px solid #2c3034;
                border-radius: 12px;
                padding-top: 15px;
            }
            QListWidget::item {
                color: #adb5bd;
                font-size: 14px;
                font-weight: 500;
                padding: 14px 18px;
                margin: 4px 10px;
                border-radius: 8px;
            }
            QListWidget::item:hover {
                background-color: #2c3034;
                color: #ffffff;
            }
            QListWidget::item:selected {
                background-color: #0d6efd;
                color: #ffffff;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(self.sidebar)

        # === CONTENT CONTAINER ===
        self.content_container = QFrame()
        self.content_container.setStyleSheet("""
            QFrame {
                background-color: #212529;
                border: 1px solid #2c3034;
                border-radius: 12px;
            }
        """)
        container_layout = QHBoxLayout(self.content_container)
        container_layout.setContentsMargins(20, 20, 20, 20)

        self.pages = QStackedWidget()
        container_layout.addWidget(self.pages)
        main_layout.addWidget(self.content_container)

        self.init_tabs()

        self.sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.sidebar.setCurrentRow(0)

        # === STATUS BAR KONEKSI ===
        self.status = QStatusBar()
        self.status.setStyleSheet("color: #adb5bd; background-color: #212529;")
        self.setStatusBar(self.status)

        self.lbl_status = QLabel("🔌 Memeriksa koneksi server...")
        self.status.addPermanentWidget(self.lbl_status)

        # Timer cek koneksi server
        self.timer = QTimer()
        self.timer.timeout.connect(self._check_server_status)
        self.timer.start(10000)  # tiap 10 detik
        self._check_server_status()

    def _check_server_status(self):
        client = get_client()
        if client.health():
            self.lbl_status.setText(f"🟢 Terhubung: {client.base_url}")
            self.lbl_status.setStyleSheet("color: #2ecc71;")
        else:
            self.lbl_status.setText(f"🔴 OFFLINE: {client.base_url}")
            self.lbl_status.setStyleSheet("color: #e74c3c;")

    def init_tabs(self):
        self.tab_dashboard = DashboardTab()
        self.tab_default = DefaultTab()
        self.tab_manual = ManualTab()
        self.tab_upload = UploadTab()
        self.tab_setting = SettingTab()

        self.pages.addWidget(self.tab_dashboard)
        self.pages.addWidget(self.tab_default)
        self.pages.addWidget(self.tab_manual)
        self.pages.addWidget(self.tab_upload)
        self.pages.addWidget(self.tab_setting)

        # Hubungkan sinyal
        self.tab_manual.btn_analyze.clicked.connect(self.refresh_all_dashboards)
        self.tab_default.btn_sync.clicked.connect(self.refresh_all_dashboards)
        self.sidebar.currentRowChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        if index == 0:
            self.refresh_all_dashboards()
        elif index == 1:
            self.tab_default.refresh_table_display()
        elif index == 4:
            self.tab_setting.muat_konfigurasi()

    def refresh_all_dashboards(self):
        self.tab_dashboard.load_and_refresh_data()