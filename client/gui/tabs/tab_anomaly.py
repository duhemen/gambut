# client/gui/tabs/tab_anomaly.py
"""Tab Anomaly Detection — visual deteksi outlier."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)

from client.gui.widgets import KpiCard, SectionTitle, Card
from client.api.client import get_client


class AnomalyTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        # ─── Header ──────────────────────────────────────
        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title = QLabel("Deteksi Anomali")
        title.setObjectName("TitleLabel")
        title_col.addWidget(title)

        subtitle = QLabel(
            "Deteksi outlier dengan Z-score, IQR, dan Isolation Forest. "
            "Data dianggap anomali jika ≥ 2 metode sepakat."
        )
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setWordWrap(True)
        title_col.addWidget(subtitle)

        header.addLayout(title_col)
        header.addStretch()

        self.btn_detect = QPushButton("🔍  Deteksi Sekarang")
        self.btn_detect.clicked.connect(self.detect_anomalies)
        header.addWidget(self.btn_detect)

        root.addLayout(header)

        # ─── KPI ─────────────────────────────────────────
        root.addWidget(SectionTitle("Ringkasan"))

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(16)

        self.kpi_total = KpiCard("Total Data", "—", "baris", "#0d6efd")
        self.kpi_anomali = KpiCard("Anomali Terdeteksi", "—", "baris", "#ef4444")
        self.kpi_normal = KpiCard("Data Normal", "—", "baris", "#10b981")
        self.kpi_rate = KpiCard("Rasio Anomali", "—", "%", "#f59e0b")

        for c in (self.kpi_total, self.kpi_anomali, self.kpi_normal, self.kpi_rate):
            kpi_row.addWidget(c)
        root.addLayout(kpi_row)

        # ─── Tabel ───────────────────────────────────────
        root.addWidget(SectionTitle("Detail Anomali"))

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Tanggal", "WT", "SM", "RF", "Suhu", "Votes", "Alasan"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setMinimumHeight(320)
        root.addWidget(self.table)

        root.addStretch()

    def detect_anomalies(self):
        client = get_client()
        if not client.token:
            QMessageBox.warning(self, "Belum Login", "Login dulu.")
            return

        self.btn_detect.setEnabled(False)
        self.btn_detect.setText("⏳ Menganalisis...")

        try:
            r = client.post("/api/v1/anomaly/detect")
            if r.status_code != 200:
                QMessageBox.critical(self, "❌ Error", f"HTTP {r.status_code}")
                return

            payload = r.json()
            if not payload.get("success"):
                QMessageBox.warning(self, "⚠️ Gagal", payload.get("message", "Error"))
                return

            data = payload["data"]
            summary = data["summary"]
            rows = data["rows"]

            # Update KPI
            self.kpi_total.set_value(str(summary["total"]))
            self.kpi_anomali.set_value(str(summary["anomalies"]))
            self.kpi_normal.set_value(str(summary["normal"]))
            self.kpi_rate.set_value(f"{summary['anomaly_rate']:.1f}")

            # Render tabel (hanya anomali)
            anomalies = [r for r in rows if r.get("anomaly")]
            self.table.setRowCount(len(anomalies))

            for i, row in enumerate(anomalies):
                self.table.setItem(i, 0, QTableWidgetItem(str(row.get("tanggal", ""))))
                self.table.setItem(i, 1, QTableWidgetItem(f"{row.get('wt', 0):.2f}"))
                self.table.setItem(i, 2, QTableWidgetItem(f"{row.get('sm', 0):.2f}"))
                self.table.setItem(i, 3, QTableWidgetItem(f"{row.get('rf', 0):.2f}"))
                self.table.setItem(i, 4, QTableWidgetItem(f"{row.get('temp', 0):.2f}"))
                self.table.setItem(i, 5, QTableWidgetItem(str(row.get("anomaly_votes", 0))))
                self.table.setItem(i, 6, QTableWidgetItem(str(row.get("anomaly_reason", ""))))

            if not anomalies:
                QMessageBox.information(
                    self, "✅ Bersih",
                    f"Tidak ada anomali terdeteksi dari {summary['total']} baris."
                )

        except Exception as e:
            QMessageBox.critical(self, "❌ Error", str(e))
        finally:
            self.btn_detect.setEnabled(True)
            self.btn_detect.setText("🔍  Deteksi Sekarang")