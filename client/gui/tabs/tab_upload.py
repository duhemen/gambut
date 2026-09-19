# client/gui/tabs/tab_upload.py
"""Tab Upload Data — drag & drop file CSV/Excel."""
import os

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QFrame, QSizePolicy, QComboBox,
)

from client.gui.widgets import SectionTitle, Card
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
    """Tab upload file lapangan."""

    data_uploaded = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_file = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(20)

        # Header
        title = QLabel("Upload Data Lapangan")
        title.setObjectName("TitleLabel")
        root.addWidget(title)

        subtitle = QLabel(
            "Upload file CSV atau Excel berisi kolom: "
            "<b>tanggal, wt, sm, rf, temp</b>"
        )
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        root.addWidget(SectionTitle("Pilih File"))

        # ─── Region selector ──────────────────────────────
        region_row = QHBoxLayout()
        region_row.setSpacing(12)

        lbl_region = QLabel("Region File:")
        lbl_region.setObjectName("MutedLabel")
        region_row.addWidget(lbl_region)

        self.combo_region = QComboBox()
        self.combo_region.addItems([
            "indonesia", "kalimantan", "sumatera", "papua",
            "jawa", "sulawesi", "bali-nusra", "maluku",
        ])
        region_row.addWidget(self.combo_region)
        region_row.addStretch()

        root.addLayout(region_row)

        # Drop zone
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

        # Action row
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
    # LOGIC
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

    def _upload_file(self):
        if not self._selected_file:
            return

        client = get_client()
        if not client.token:
            QMessageBox.warning(self, "Belum Login", "Login dulu.")
            return

        region = self.combo_region.currentText().lower()

        self.btn_upload.setEnabled(False)
        self.btn_upload.setText("⏳ Mengunggah...")

        try:
            with open(self._selected_file, "rb") as f:
                files = {"file": (
                    os.path.basename(self._selected_file),
                    f,
                    "application/octet-stream",
                )}
                # Kirim region sebagai form data
                resp = client.post(
                    f"/api/v1/data/upload?region={region}",
                    files=files,
                )

            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    QMessageBox.information(
                        self, "✅ Berhasil",
                        data.get("message", "File berhasil diupload.")
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
        self._selected_file = None
        self.lbl_file.setText("Belum ada file dipilih.")
        self.btn_upload.setEnabled(False)