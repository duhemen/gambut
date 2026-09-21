# client/gui/tabs/tab_manual.py
"""Tab Input Manual — form input data harian dengan cascading region."""
from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QFrame, QDoubleSpinBox,
    QDateEdit, QSizePolicy,
)

from client.gui.widgets import SectionTitle, Card, StatusBadge
from client.gui.widgets.region_selector import RegionSelector
from client.api.client import get_client


class ManualInputTab(QWidget):
    """Form input data harian gambut dengan cascading region."""

    data_saved = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    # ============================================================
    # UI
    # ============================================================
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(20)

        # ─── Header ──────────────────────────────────────────
        header = QVBoxLayout()
        header.setSpacing(2)

        title = QLabel("Input Manual Data Harian")
        title.setObjectName("TitleLabel")
        header.addWidget(title)

        subtitle = QLabel(
            "Masukkan data pengukuran lapangan untuk hari ini. "
            "Pilih lokasi lengkap (Region → Provinsi → Kabupaten → Kecamatan → Kelurahan) "
            "agar data tercatat dengan presisi."
        )
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setWordWrap(True)
        header.addWidget(subtitle)

        root.addLayout(header)

        # ─── Form Card ────────────────────────────────────────
        root.addWidget(SectionTitle("Lokasi & Waktu Pengukuran"))

        form_card = Card()

        # ─── Region Selector (5-level) ─────────────────────
        self.region_selector = RegionSelector()
        form_card.layout().addWidget(self.region_selector)

        # ─── Tanggal Pengukuran ────────────────────────────
        date_row = QHBoxLayout()
        lbl_date = QLabel("Tanggal Pengukuran")
        lbl_date.setObjectName("MutedLabel")
        lbl_date.setFixedWidth(140)
        date_row.addWidget(lbl_date)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("dd MMMM yyyy")
        date_row.addWidget(self.date_input, stretch=1)
        form_card.layout().addLayout(date_row)

        root.addWidget(form_card)

        # ─── Data Pengukuran Card ─────────────────────────
        root.addWidget(SectionTitle("Data Pengukuran"))

        data_card = Card()

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(14)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        # WT
        lbl_wt = QLabel("Muka Air Tanah / WT (cm)")
        lbl_wt.setObjectName("MutedLabel")
        grid.addWidget(lbl_wt, 0, 0)
        self.spin_wt = QDoubleSpinBox()
        self.spin_wt.setRange(-100.0, 10.0)
        self.spin_wt.setDecimals(2)
        self.spin_wt.setSuffix(" cm")
        self.spin_wt.setValue(-10.0)
        grid.addWidget(self.spin_wt, 1, 0)

        # Suhu
        lbl_temp = QLabel("Suhu Udara (°C)")
        lbl_temp.setObjectName("MutedLabel")
        grid.addWidget(lbl_temp, 0, 1)
        self.spin_temp = QDoubleSpinBox()
        self.spin_temp.setRange(-10.0, 60.0)
        self.spin_temp.setDecimals(2)
        self.spin_temp.setSuffix(" °C")
        self.spin_temp.setValue(30.0)
        grid.addWidget(self.spin_temp, 1, 1)

        # Soil Moisture
        lbl_sm = QLabel("Kelembapan Tanah / SM (%)")
        lbl_sm.setObjectName("MutedLabel")
        grid.addWidget(lbl_sm, 2, 0)
        self.spin_sm = QDoubleSpinBox()
        self.spin_sm.setRange(0.0, 100.0)
        self.spin_sm.setDecimals(2)
        self.spin_sm.setSuffix(" %")
        self.spin_sm.setValue(50.0)
        grid.addWidget(self.spin_sm, 3, 0)

        # Rainfall
        lbl_rf = QLabel("Curah Hujan / RF (mm)")
        lbl_rf.setObjectName("MutedLabel")
        grid.addWidget(lbl_rf, 2, 1)
        self.spin_rf = QDoubleSpinBox()
        self.spin_rf.setRange(0.0, 500.0)
        self.spin_rf.setDecimals(2)
        self.spin_rf.setSuffix(" mm")
        self.spin_rf.setValue(0.0)
        grid.addWidget(self.spin_rf, 3, 1)

        data_card.layout().addLayout(grid)
        root.addWidget(data_card)

        # ─── Preview + Aksi ───────────────────────────────────
        action_row = QHBoxLayout()
        action_row.setSpacing(12)

        self.lbl_preview = QLabel("Isi form untuk melihat preview status...")
        self.lbl_preview.setStyleSheet(
            "color: #94a3b8; font-size: 12px; "
            "background: transparent; padding: 8px;"
        )
        action_row.addWidget(self.lbl_preview)
        action_row.addStretch()

        self.status_badge = StatusBadge("—")
        self.status_badge.setVisible(False)
        action_row.addWidget(self.status_badge)

        self.btn_reset = QPushButton("🔄  Reset")
        self.btn_reset.setProperty("variant", "secondary")
        self.btn_reset.clicked.connect(self._reset_form)
        action_row.addWidget(self.btn_reset)

        self.btn_save = QPushButton("💾  Simpan Data")
        self.btn_save.clicked.connect(self._save_data)
        action_row.addWidget(self.btn_save)

        root.addLayout(action_row)
        root.addStretch()

        # Auto-update preview
        self.spin_wt.valueChanged.connect(self._update_preview)
        self.spin_temp.valueChanged.connect(self._update_preview)
        self.spin_sm.valueChanged.connect(self._update_preview)
        self.spin_rf.valueChanged.connect(self._update_preview)

        self._update_preview()

    # ============================================================
    # LOGIC
    # ============================================================
    def _update_preview(self):
        """Preview status PFVI dari nilai form."""
        wt = self.spin_wt.value()
        temp = self.spin_temp.value()

        score = max(0.0, min(100.0, (-wt * 3.0) + ((temp - 25) * 2.0)))

        if score >= 65:
            status = "🔴 BAHAYA"
            color = "#ef4444"
        elif score >= 40:
            status = "🟡 SIAGA"
            color = "#f59e0b"
        else:
            status = "🟢 AMAN"
            color = "#10b981"

        self.lbl_preview.setText(
            f"<span style='color:{color};font-weight:700;'>"
            f"Skor: {score:.0f}/100 — {status}"
            f"</span>"
        )
        self.status_badge.set_status(status)
        self.status_badge.setVisible(True)

    def _reset_form(self):
        """Reset form ke default."""
        self.date_input.setDate(QDate.currentDate())
        if hasattr(self, "region_selector"):
            try:
                self.region_selector.combo_region.setCurrentIndex(0)
            except Exception:
                pass
        self.spin_wt.setValue(-10.0)
        self.spin_sm.setValue(50.0)
        self.spin_rf.setValue(0.0)
        self.spin_temp.setValue(30.0)
        self._update_preview()

    def _save_data(self):
        """Kirim data ke server."""
        client = get_client()
        if not client.token:
            QMessageBox.warning(self, "Belum Login", "Login dulu.")
            return

        # ─── Ambil selection cascading ───────────────────
        sel = self.region_selector.get_selection()

        if not sel.get("region"):
            QMessageBox.warning(
                self, "⚠️ Pilih Region",
                "Silakan pilih region terlebih dahulu."
            )
            return

        if not sel.get("regency"):
            QMessageBox.warning(
                self, "⚠️ Pilih Kabupaten",
                "Silakan pilih kabupaten/kota terlebih dahulu."
            )
            return

        payload = {
            "region": sel.get("region", ""),
            "province": sel.get("province", ""),
            "regency": sel.get("regency", ""),
            "district": sel.get("district", ""),
            "village": sel.get("village", ""),
            "wt": self.spin_wt.value(),
            "sm": self.spin_sm.value(),
            "rf": self.spin_rf.value(),
            "temp": self.spin_temp.value(),
        }

        self.btn_save.setEnabled(False)
        self.btn_save.setText("⏳ Mengirim...")

        try:
            resp = client.post("/api/v1/data", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    QMessageBox.information(
                        self, "✅ Berhasil",
                        data.get("message", "Data berhasil disimpan.")
                    )
                    self.data_saved.emit()
                    self._reset_form()
                else:
                    QMessageBox.warning(
                        self, "⚠️ Gagal",
                        data.get("message", "Gagal menyimpan data.")
                    )
            else:
                QMessageBox.critical(
                    self, "❌ Error",
                    f"HTTP {resp.status_code}: {resp.text[:200]}"
                )
        except Exception as e:
            QMessageBox.critical(
                self, "❌ Error",
                f"Tidak dapat menghubungi server:\n{e}"
            )
        finally:
            self.btn_save.setEnabled(True)
            self.btn_save.setText("💾  Simpan Data")