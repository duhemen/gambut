# app/gui/tabs/tab_setting.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt

from app.api.client import get_client
from app.utils.data_processor import get_config, save_config


class SettingTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        title = QLabel("⚙️ PENGATURAN KONEKSI SERVER & API SATELIT")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)

        layout.addStretch()

        # === SERVER URL ===
        group_server = QGroupBox("Koneksi ke Server PeatFR")
        group_server.setStyleSheet("""
            QGroupBox {
                font-weight: bold; color: #e67e22;
                border: 1px solid #2c3034; border-radius: 8px;
                margin-top: 15px; padding-top: 15px;
            }
        """)
        srv_layout = QVBoxLayout(group_server)

        srv_row = QHBoxLayout()
        srv_lbl = QLabel("Base URL Server:")
        srv_lbl.setStyleSheet("color: #adb5bd; font-size: 13px;")
        srv_lbl.setFixedWidth(150)
        self.txt_server = QLineEdit()
        self.txt_server.setText(get_client().base_url)
        self.txt_server.setStyleSheet(
            "background-color: #2c3034; color: white; "
            "border: 1px solid #495057; border-radius: 4px; padding: 6px;"
        )
        srv_row.addWidget(srv_lbl)
        srv_row.addWidget(self.txt_server)
        srv_layout.addLayout(srv_row)

        self.btn_apply_server = QPushButton("🔌 Terapkan URL Server")
        self.btn_apply_server.setStyleSheet("""
            QPushButton { background-color: #e67e22; color: white; font-weight: bold;
                padding: 8px; border-radius: 6px; }
            QPushButton:hover { background-color: #d35400; }
        """)
        self.btn_apply_server.clicked.connect(self.terapkan_server_url)
        srv_layout.addWidget(self.btn_apply_server)

        layout.addWidget(group_server)

        # === API CONFIG (disimpan di server) ===
        group_api = QGroupBox("Koneksi Server Data Satelit (disimpan di server)")
        group_api.setStyleSheet("""
            QGroupBox {
                font-weight: bold; color: #3498db;
                border: 1px solid #2c3034; border-radius: 8px;
                margin-top: 15px; padding-top: 15px;
            }
        """)
        api_layout = QVBoxLayout(group_api)

        url_layout = QHBoxLayout()
        lbl_url = QLabel("API EndPoint URL:")
        lbl_url.setStyleSheet("color: #adb5bd; font-size: 13px;")
        lbl_url.setFixedWidth(150)
        self.txt_url = QLineEdit()
        self.txt_url.setStyleSheet(
            "background-color: #2c3034; color: white; "
            "border: 1px solid #495057; border-radius: 4px; padding: 6px;"
        )
        url_layout.addWidget(lbl_url)
        url_layout.addWidget(self.txt_url)
        api_layout.addLayout(url_layout)

        key_layout = QHBoxLayout()
        lbl_key = QLabel("Satellite API Key:")
        lbl_key.setStyleSheet("color: #adb5bd; font-size: 13px;")
        lbl_key.setFixedWidth(150)
        self.txt_key = QLineEdit()
        self.txt_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_key.setStyleSheet(
            "background-color: #2c3034; color: white; "
            "border: 1px solid #495057; border-radius: 4px; padding: 6px;"
        )
        key_layout.addWidget(lbl_key)
        key_layout.addWidget(self.txt_key)
        api_layout.addLayout(key_layout)

        layout.addWidget(group_api)

        self.btn_save = QPushButton("💾 SIMPAN KONFIGURASI KE SERVER")
        self.btn_save.setStyleSheet("""
            QPushButton { background-color: #2ecc71; color: white; font-size: 13px;
                font-weight: bold; border-radius: 6px; padding: 10px; margin-top: 10px; }
            QPushButton::hover { background-color: #27ae60; }
        """)
        self.btn_save.clicked.connect(self.simpan_konfigurasi)
        layout.addWidget(self.btn_save)

        layout.addStretch()

        self.muat_konfigurasi()

    def terapkan_server_url(self):
        new_url = self.txt_server.text().strip()
        if not new_url:
            return
        from app.api.client import set_server_url
        set_server_url(new_url)
        QMessageBox.information(
            self, "URL Server",
            f"URL server diubah ke:<br><b>{new_url}</b><br><br>"
            "Perubahan berlaku untuk session ini."
        )

    def muat_konfigurasi(self):
        result = get_config()
        if result.get("success"):
            cfg = result.get("data", {})
            self.txt_url.setText(cfg.get("api_url", ""))
            self.txt_key.setText(cfg.get("api_key", ""))
        else:
            # Kalau 403 (bukan admin), disable input
            msg = result.get("message", "")
            if "403" in msg or "Forbidden" in msg or "role" in msg.lower():
                self.txt_url.setText("— tidak berwenang —")
                self.txt_key.setText("")
                self.txt_url.setEnabled(False)
                self.txt_key.setEnabled(False)
                self.btn_save.setEnabled(False)
            else:
                self.txt_url.setText("")
                self.txt_key.setText("")

    def simpan_konfigurasi(self):
        url = self.txt_url.text().strip()
        key = self.txt_key.text().strip()
        result = save_config(url, key)

        if result.get("success"):
            msg = QMessageBox(self)
            msg.setWindowTitle("Sukses")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText("<b>Konfigurasi berhasil disimpan di server!</b>")
            msg.setStyleSheet("""
                QMessageBox { background-color: #212529; border: 1px solid #454d55; border-radius: 10px; }
                QLabel { color: #ffffff; }
                QPushButton { background-color: #2ecc71; color: white; font-weight: bold;
                    padding: 6px 15px; border-radius: 5px; }
            """)
            msg.exec()
        else:
            QMessageBox.critical(self, "Gagal",
                                 f"Gagal menyimpan konfigurasi: {result.get('message')}")