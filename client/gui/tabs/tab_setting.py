# client/gui/tabs/tab_setting.py
"""Tab Pengaturan — konfigurasi API satelit & preferensi."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QComboBox
)

from client.gui.widgets import SectionTitle, Card
from client.gui.theme import get_current_mode, ThemeMode, get_palette
from client.api.client import get_client
from client.config import SERVER_URL


class SettingTab(QWidget):
    """Tab pengaturan aplikasi."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._load_config()

    # ============================================================
    # UI
    # ============================================================
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(20)

        # Header
        title = QLabel("Pengaturan")
        title.setObjectName("TitleLabel")
        root.addWidget(title)

        subtitle = QLabel(
            "Konfigurasi koneksi server, API satelit, dan preferensi tampilan."
        )
        subtitle.setObjectName("SubtitleLabel")
        root.addWidget(subtitle)

        # ─── Info Server ──────────────────────────────────────
        root.addWidget(SectionTitle("Koneksi Server"))

        server_card = Card()
        info_grid = QGridLayout()
        info_grid.setHorizontalSpacing(16)
        info_grid.setVerticalSpacing(10)

        lbl_url = QLabel("URL Server")
        lbl_url.setObjectName("MutedLabel")
        info_grid.addWidget(lbl_url, 0, 0)

        self.lbl_server_url = QLabel(SERVER_URL)
        self.lbl_server_url.setStyleSheet(
            "color: #10b981; font-size: 13px; font-weight: 600; "
            "background: transparent; padding: 4px;"
        )
        self.lbl_server_url.setWordWrap(True)
        info_grid.addWidget(self.lbl_server_url, 0, 1)

        server_card.layout().addLayout(info_grid)
        root.addWidget(server_card)

        # ─── Config Satelit (admin only) ─────────────────────
        root.addWidget(SectionTitle("API Satelit (Admin)"))

        config_card = Card()
        config_grid = QGridLayout()
        config_grid.setHorizontalSpacing(16)
        config_grid.setVerticalSpacing(10)
        config_grid.setColumnStretch(1, 1)

        # API URL
        lbl_api = QLabel("API URL")
        lbl_api.setObjectName("MutedLabel")
        config_grid.addWidget(lbl_api, 0, 0)

        self.txt_api_url = QLineEdit()
        self.txt_api_url.setPlaceholderText("https://example.com/api")
        config_grid.addWidget(self.txt_api_url, 0, 1)

        # API Key
        lbl_key = QLabel("API Key")
        lbl_key.setObjectName("MutedLabel")
        config_grid.addWidget(lbl_key, 1, 0)

        self.txt_api_key = QLineEdit()
        self.txt_api_key.setPlaceholderText("masukkan-api-key")
        self.txt_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        config_grid.addWidget(self.txt_api_key, 1, 1)

        config_card.layout().addLayout(config_grid)
        root.addWidget(config_card)

        # Action row config
        config_actions = QHBoxLayout()
        config_actions.addStretch()

        self.btn_save_config = QPushButton("💾  Simpan Konfigurasi")
        self.btn_save_config.clicked.connect(self._save_config)
        config_actions.addWidget(self.btn_save_config)

        root.addLayout(config_actions)

        # ─── Preferensi Tampilan ─────────────────────────────
        root.addWidget(SectionTitle("Preferensi Tampilan"))

        theme_card = Card()
        theme_grid = QHBoxLayout()
        theme_grid.setSpacing(12)

        lbl_theme = QLabel("Tema Aplikasi")
        lbl_theme.setObjectName("MutedLabel")
        theme_grid.addWidget(lbl_theme)

        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Dark (default)", "Light"])
        current = get_current_mode()
        self.combo_theme.setCurrentIndex(0 if current == ThemeMode.DARK else 1)
        self.combo_theme.currentIndexChanged.connect(self._on_theme_changed)
        theme_grid.addWidget(self.combo_theme)

        theme_grid.addStretch()

        info_theme = QLabel(
            "⚠️ Perubahan tema memerlukan restart aplikasi."
        )
        info_theme.setStyleSheet(
            "color: #f59e0b; font-size: 11px; background: transparent;"
        )
        theme_grid.addWidget(info_theme)

        theme_card.layout().addLayout(theme_grid)
        root.addWidget(theme_card)

        root.addStretch()

    # ============================================================
    # LOGIC
    # ============================================================
    def _load_config(self):
        """Ambil config dari server."""
        client = get_client()
        if not client.token:
            return

        try:
            resp = client.get("/api/v1/config")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    cfg = data.get("data", {})
                    self.txt_api_url.setText(cfg.get("api_url", ""))
                    self.txt_api_key.setText(cfg.get("api_key", ""))
            elif resp.status_code == 403:
                # Bukan admin, disable form
                self.txt_api_url.setEnabled(False)
                self.txt_api_key.setEnabled(False)
                self.btn_save_config.setEnabled(False)
                self.txt_api_url.setPlaceholderText(
                    "Hanya admin yang bisa mengubah konfigurasi"
                )
        except Exception:
            pass

    def _save_config(self):
        """Simpan config ke server."""
        client = get_client()
        if not client.token:
            QMessageBox.warning(
                self, "Belum Login",
                "Anda harus login terlebih dahulu."
            )
            return

        payload = {
            "api_url": self.txt_api_url.text().strip(),
            "api_key": self.txt_api_key.text().strip(),
        }

        try:
            resp = client.post("/api/v1/config", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    QMessageBox.information(
                        self, "✅ Berhasil",
                        data.get("message", "Konfigurasi disimpan.")
                    )
                else:
                    QMessageBox.warning(
                        self, "⚠️ Gagal",
                        data.get("message", "Gagal menyimpan.")
                    )
            elif resp.status_code == 403:
                QMessageBox.warning(
                    self, "Akses Ditolak",
                    "Hanya admin yang bisa mengubah konfigurasi."
                )
            else:
                QMessageBox.critical(
                    self, "❌ Error",
                    f"HTTP {resp.status_code}"
                )
        except Exception as e:
            QMessageBox.critical(
                self, "❌ Error",
                f"Tidak dapat menghubungi server:\n{e}"
            )

    def _on_theme_changed(self, index: int):
        """Trigger saat user ganti tema."""
        from PyQt6.QtWidgets import QApplication, QMessageBox
        from client.gui.theme import apply_theme, ThemeMode

        new_mode = ThemeMode.DARK if index == 0 else ThemeMode.LIGHT
        current = get_current_mode()

        if new_mode == current:
            return

        reply = QMessageBox.question(
            self, "Ganti Tema",
            f"Ganti tema ke <b>{new_mode.value.upper()}</b>?<br>"
            "Aplikasi akan me-restart untuk menerapkan perubahan penuh.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            # Kembalikan pilihan dropdown
            self.combo_theme.setCurrentIndex(0 if current == ThemeMode.DARK else 1)
            return

        # Apply tema ke QApplication saat ini (visual update langsung untuk widget baru)
        app = QApplication.instance()
        apply_theme(app, new_mode)

        # Simpan pilihan ke .env atau config
        print(f"✅ [THEME] Tema diganti ke: {new_mode.value}")
        QMessageBox.information(
            self, "Tema Diganti",
            "Tema telah diganti. Silakan tutup & buka ulang aplikasi untuk hasil optimal."
        )