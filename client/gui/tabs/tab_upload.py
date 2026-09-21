# client/gui/tabs/tab_upload.py
"""Tab Upload Data — drag & drop file CSV/Excel dengan cascading region."""
import os
from urllib.parse import urlencode

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QFrame, QSizePolicy,
)

from client.gui.widgets import SectionTitle, Card
from client.gui.widgets.region_selector import RegionSelector
from client.api.client import get_client


class DropZone(QFrame):
    """Area drag & drop untuk file."""

    file_dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(220)
        self.setStyleSheet("""
            QFrame {
                background: rgba(30, 41, 59, 0.4);
                border: 2px dashed #334155;
                border-radius: 12px;
            }
            QFrame[dragging="true"] {
                background: rgba(16, 185, 129, 0.08);
                border: 2px dashed #10b981;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        ico = QLabel("📁")
        ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ico.setStyleSheet("font-size: 56px; background: transparent; border: none;")
        layout.addWidget(ico)

        title = QLabel("Drop file CSV / Excel di sini")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "color: #f8fafc; font-size: 16px; font-weight: 700; "
            "background: transparent; border: none;"
        )
        layout.addWidget(title)

        sub = QLabel("atau klik tombol di bawah untuk pilih file")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(
            "color: #64748b; font-size: 12px; "
            "background: transparent; border: none;"
        )
        layout.addWidget(sub)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                ext = os.path.splitext(urls[0].toLocalFile())[1].lower()
                if ext in (".csv", ".xlsx", ".xls"):
                    event.acceptProposedAction()
                    self.setProperty("dragging", "true")
                    self.style().unpolish(self)
                    self.style().polish(self)
                    return
        event.ignore()

    def dragLeaveEvent(self, event):
        self.setProperty("dragging", "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent):
        self.setProperty("dragging", "false")
        self.style().unpolish(self)
        self.style().polish(self)

        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.file_dropped.emit(path)
            event.acceptProposedAction()


class UploadTab(QWidget):
    """Tab upload file lapangan dengan cascading region (5 level)."""

    data_uploaded = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_file = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(20)

        # ─── Header ──────────────────────────────────────
        title = QLabel("Upload Data Lapangan")
        title.setObjectName("TitleLabel")
        root.addWidget(title)

        subtitle = QLabel(
            "Upload file CSV atau Excel berisi kolom: "
            "<b>tanggal, wt, sm, rf, temp</b>. "
            "Pilih lokasi lengkap (Region → Provinsi → Kabupaten → Kecamatan → Kelurahan) "
            "agar data tercatat dengan presisi."
        )
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        # ─── Region Selector (5-level cascading) ─────────
        root.addWidget(SectionTitle("Lokasi Pengukuran"))

        region_card = Card()
        self.region_selector = RegionSelector()
        region_card.layout().addWidget(self.region_selector)
        root.addWidget(region_card)

        # ─── Drop Zone ───────────────────────────────────
        root.addWidget(SectionTitle("Pilih File"))

        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._on_file_selected)
        root.addWidget(self.drop_zone)

        # File info
        self.lbl_file = QLabel("Belum ada file dipilih.")
        self.lbl_file.setStyleSheet(
            "color: #94a3b8; font-size: 12px; padding: 8px; "
            "background: transparent;"
        )
        root.addWidget(self.lbl_file)

        # ─── Action Row ──────────────────────────────────
        action_row = QHBoxLayout()
        action_row.setSpacing(12)

        self.btn_browse = QPushButton("📂  Pilih File")
        self.btn_browse.setProperty("variant", "secondary")
        self.btn_browse.clicked.connect(self._browse_file)
        action_row.addWidget(self.btn_browse)

        action_row.addStretch()

        self.btn_upload = QPushButton("⬆️  Upload ke Server")
        self.btn_upload.setEnabled(False)
        self.btn_upload.clicked.connect(self._upload_file)
        action_row.addWidget(self.btn_upload)

        root.addLayout(action_row)
        root.addStretch()

    # ============================================================
    # FILE SELECTION
    # ============================================================
    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Pilih File Data",
            "",
            "Data Files (*.csv *.xlsx *.xls)",
        )
        if path:
            self._on_file_selected(path)

    def _on_file_selected(self, path: str):
        if not os.path.exists(path):
            QMessageBox.warning(self, "File Tidak Ditemukan", path)
            return

        ext = os.path.splitext(path)[1].lower()
        if ext not in (".csv", ".xlsx", ".xls"):
            QMessageBox.warning(
                self, "Format Tidak Didukung",
                f"Format '{ext}' tidak didukung.\n"
                "Gunakan .csv, .xlsx, atau .xls"
            )
            return

        self._selected_file = path
        size_kb = os.path.getsize(path) / 1024
        self.lbl_file.setText(
            f"✅ <b>{os.path.basename(path)}</b>  "
            f"<span style='color:#64748b;'>({size_kb:.1f} KB)</span>"
        )
        self.btn_upload.setEnabled(True)

    # ============================================================
    # UPLOAD
    # ============================================================
    def _upload_file(self):
        if not self._selected_file:
            return

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

        # ─── Build query params ──────────────────────────
        params = {
            "region": sel.get("region", ""),
            "province": sel.get("province", ""),
            "regency": sel.get("regency", ""),
            "district": sel.get("district", ""),
            "village": sel.get("village", ""),
        }
        query = urlencode({k: v for k, v in params.items() if v})

        # ─── Label lokasi untuk UI ───────────────────────
        lokasi = sel.get("regency", "")
        if sel.get("district"):
            lokasi = f"{lokasi}, {sel['district']}"
        if sel.get("village"):
            lokasi = f"{lokasi}, {sel['village']}"

        self.btn_upload.setEnabled(False)
        self.btn_upload.setText("⏳ Mengunggah...")

        try:
            with open(self._selected_file, "rb") as f:
                files = {
                    "file": (
                        os.path.basename(self._selected_file),
                        f,
                        "application/octet-stream",
                    )
                }
                resp = client.post(
                    f"/api/v1/data/upload?{query}",
                    files=files,
                )

            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    QMessageBox.information(
                        self, "✅ Berhasil",
                        data.get("message",
                                 f"File berhasil diupload untuk {lokasi}.")
                    )
                    self.data_uploaded.emit()
                    self._reset()
                else:
                    QMessageBox.warning(
                        self, "⚠️ Gagal",
                        data.get("message", "Upload gagal.")
                    )
            else:
                QMessageBox.critical(
                    self, "❌ Error",
                    f"HTTP {resp.status_code}: {resp.text[:200]}"
                )
        except Exception as e:
            QMessageBox.critical(
                self, "❌ Error",
                f"Gagal upload:\n{e}"
            )
        finally:
            self.btn_upload.setEnabled(bool(self._selected_file))
            self.btn_upload.setText("⬆️  Upload ke Server")

    def _reset(self):
        """Reset form setelah upload sukses."""
        self._selected_file = None
        self.lbl_file.setText("Belum ada file dipilih.")
        self.btn_upload.setEnabled(False)

        # Reset region selector ke pilihan awal
        if hasattr(self, "region_selector"):
            try:
                self.region_selector.combo_region.setCurrentIndex(0)
            except Exception:
                pass