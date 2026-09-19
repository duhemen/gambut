# client/gui/tabs/tab_dashboard.py
"""Tab Dashboard — KPI + tren data + pie + tabel."""
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
    QFrame, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QMessageBox
)

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from client.gui.widgets import KpiCard, StatusBadge, SectionTitle, Card
from client.api.client import get_client
from client.gui.theme import get_palette


# ============================================================
# CHART WIDGETS
# ============================================================
class TrendChart(FigureCanvas):
    """Line chart untuk tren WT."""

    def __init__(self, parent=None, width=7, height=3, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor="#1e293b")
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = self.fig.add_subplot(111)
        self._style_axes()

    def _style_axes(self):
        palette = get_palette()
        self.ax.set_facecolor("#1e293b")
        for spine in self.ax.spines.values():
            spine.set_color("#334155")
        self.ax.tick_params(colors="#94a3b8", labelsize=9)
        self.ax.grid(True, color="#334155", linestyle="--", alpha=0.5)

    def plot(self, dates, values):
        self.ax.clear()
        self._style_axes()

        if not dates or not values:
            self.ax.text(0.5, 0.5, "Belum ada data",
                         ha="center", va="center",
                         color="#64748b", fontsize=12,
                         transform=self.ax.transAxes)
            self.draw()
            return

        self.ax.plot(
            dates, values,
            color="#10b981", linewidth=2.5,
            marker="o", markersize=5,
            markerfacecolor="#10b981",
            markeredgecolor="#0b0f19", markeredgewidth=1.5,
            label="WT (cm)",
        )
        self.ax.fill_between(
            range(len(dates)), values,
            alpha=0.15, color="#10b981"
        )
        self.ax.set_xticks(range(len(dates)))
        self.ax.set_xticklabels(dates, rotation=45, ha="right")
        self.ax.set_ylabel("Muka Air (cm)", color="#94a3b8", fontsize=10)
        self.ax.legend(facecolor="#1e293b", edgecolor="#334155",
                       labelcolor="#f8fafc", fontsize=9)
        self.fig.tight_layout()
        self.draw()


class StatusPie(FigureCanvas):
    """Pie chart untuk distribusi status."""

    def __init__(self, parent=None, width=4, height=3, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor="#1e293b")
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = self.fig.add_subplot(111)

    def plot(self, aman: int, siaga: int, bahaya: int):
        self.ax.clear()

        labels, sizes, colors = [], [], []
        if aman > 0:
            labels.append(f"Aman ({aman})"); sizes.append(aman); colors.append("#10b981")
        if siaga > 0:
            labels.append(f"Siaga ({siaga})"); sizes.append(siaga); colors.append("#f59e0b")
        if bahaya > 0:
            labels.append(f"Bahaya ({bahaya})"); sizes.append(bahaya); colors.append("#ef4444")

        if not sizes:
            self.ax.text(0.5, 0.5, "Belum ada data",
                         ha="center", va="center",
                         color="#64748b", fontsize=11,
                         transform=self.ax.transAxes)
            self.draw()
            return

        wedges, texts, autotexts = self.ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct="%1.0f%%",
            startangle=90,
            textprops={"color": "#f8fafc", "fontsize": 10},
            wedgeprops={"edgecolor": "#0b0f19", "linewidth": 2},
        )
        for at in autotexts:
            at.set_color("#ffffff")
            at.set_fontweight("bold")
        self.ax.axis("equal")
        self.fig.tight_layout()
        self.draw()


# ============================================================
# DASHBOARD TAB
# ============================================================
class DashboardTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        # ─── Header ──────────────────────────────────────────
        header = QHBoxLayout()

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title = QLabel("Dashboard Monitoring")
        title.setObjectName("TitleLabel")
        title_col.addWidget(title)

        subtitle = QLabel("Ringkasan risiko kebakaran lahan gambut tropis")
        subtitle.setObjectName("SubtitleLabel")
        title_col.addWidget(subtitle)

        header.addLayout(title_col)
        header.addStretch()

        self.btn_sync = QPushButton("Sync Satelit")
        self.btn_sync.setProperty("variant", "secondary")
        self.btn_sync.clicked.connect(self._sync_satellite)
        header.addWidget(self.btn_sync)

        self.btn_broadcast = QPushButton("Broadcast Alert")
        self.btn_broadcast.setProperty("variant", "danger")
        self.btn_broadcast.clicked.connect(self._broadcast_alert)
        header.addWidget(self.btn_broadcast)

        self.status_badge = StatusBadge("🟢 AMAN")
        header.addWidget(self.status_badge, alignment=Qt.AlignmentFlag.AlignVCenter)

        root.addLayout(header)

        # ─── KPI Grid ────────────────────────────────────────
        root.addWidget(SectionTitle("Ringkasan Hari Ini"))

        kpi_grid = QHBoxLayout()
        kpi_grid.setSpacing(16)

        self.kpi_total = KpiCard("Total Observasi", "—", "baris data", "#0d6efd")
        self.kpi_wt = KpiCard("Muka Air (WT)", "—", "cm (terbaru)", "#10b981")
        self.kpi_temp = KpiCard("Suhu", "—", "°C (terbaru)", "#f59e0b")
        self.kpi_score = KpiCard("Indeks Kerawanan", "—", "skor 0–100", "#ef4444")

        for card in (self.kpi_total, self.kpi_wt, self.kpi_temp, self.kpi_score):
            kpi_grid.addWidget(card)
        root.addLayout(kpi_grid)

        # ─── Chart Row (Line + Pie) ─────────────────────────
        root.addWidget(SectionTitle("Analisis Tren"))

        chart_row = QHBoxLayout()
        chart_row.setSpacing(16)

        # Line chart card
        line_card = Card()
        line_card.layout().addWidget(QLabel("📈 Tren Muka Air Tanah (7 hari)"))
        self.trend_chart = TrendChart(width=7, height=3, dpi=90)
        self.trend_chart.setMinimumHeight(240)
        line_card.layout().addWidget(self.trend_chart)
        chart_row.addWidget(line_card, stretch=2)

        # Pie chart card
        pie_card = Card()
        pie_card.layout().addWidget(QLabel("🥧 Distribusi Status"))
        self.status_pie = StatusPie(width=4, height=3, dpi=90)
        self.status_pie.setMinimumHeight(240)
        pie_card.layout().addWidget(self.status_pie)
        chart_row.addWidget(pie_card, stretch=1)

        root.addLayout(chart_row)

        # ─── Table ───────────────────────────────────────────
        root.addWidget(SectionTitle("Data Terbaru"))

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Tanggal", "WT (cm)", "SM (%)", "RF (mm)", "Suhu (°C)"]
        )
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setMinimumHeight(200)
        root.addWidget(self.table)

        root.addStretch()

    # ============================================================
    # DATA REFRESH
    # ============================================================
    def refresh(self):
        client = get_client()
        if not client.token:
            return

        try:
            resp = client.get("/api/v1/data")
            if resp.status_code != 200:
                return

            payload = resp.json()
            data = payload.get("data", [])

            # Sort ascending by tanggal untuk chart
            sorted_data = sorted(data, key=lambda x: x.get("tanggal", ""))

            # ─── KPI ─────────────────────────────────────────
            self.kpi_total.set_value(f"{len(data)}")

            if data:
                # Ambil data terbaru (data[0] karena server return desc)
                latest = data[0]
                wt = latest.get("wt")
                temp = latest.get("temp")

                self.kpi_wt.set_value(f"{wt:.1f}" if isinstance(wt, (int, float)) else "—")
                self.kpi_temp.set_value(f"{temp:.1f}" if isinstance(temp, (int, float)) else "—")

                score = self._quick_score(wt, temp)
                self.kpi_score.set_value(f"{score:.0f}")
                self.status_badge.set_status(self._score_to_status(score))

            # ─── Line Chart ──────────────────────────────────
            dates = [d.get("tanggal", "")[-5:] for d in sorted_data[-7:]]
            wts = [d.get("wt", 0) or 0 for d in sorted_data[-7:]]
            self.trend_chart.plot(dates, wts)

            # ─── Pie Chart ───────────────────────────────────
            aman = siaga = bahaya = 0
            for d in data:
                sc = self._quick_score(d.get("wt"), d.get("temp"))
                if sc >= 65: bahaya += 1
                elif sc >= 40: siaga += 1
                else: aman += 1
            self.status_pie.plot(aman, siaga, bahaya)

            # ─── Table ───────────────────────────────────────
            self.table.setRowCount(min(10, len(data)))
            for i, d in enumerate(data[:10]):
                self.table.setItem(i, 0, QTableWidgetItem(str(d.get("tanggal", ""))))
                self.table.setItem(i, 1, QTableWidgetItem(f"{d.get('wt', 0):.2f}"))
                self.table.setItem(i, 2, QTableWidgetItem(f"{d.get('sm', 0):.2f}"))
                self.table.setItem(i, 3, QTableWidgetItem(f"{d.get('rf', 0):.2f}"))
                self.table.setItem(i, 4, QTableWidgetItem(f"{d.get('temp', 0):.2f}"))

        except Exception as e:
            print(f"⚠️ [DASHBOARD] Error: {e}")

    def _sync_satellite(self):
        """Trigger fetch satelit untuk semua region."""
        client = get_client()
        if not client.token:
            return

        self.btn_sync.setEnabled(False)
        self.btn_sync.setText("Sync...")

        try:
            total_fetched = 0
            for region in ["kalimantan", "sumatera", "papua"]:
                r = client.post(
                    "/api/v1/satellite/fetch",
                    json={"region": region, "days_back": 1},
                )
                if r.status_code == 200:
                    data = r.json()
                    total_fetched += data.get("fetched", 0)

            QMessageBox.information(
                self, "Sinkronisasi",
                f"Berhasil fetch {total_fetched} hotspot dari 3 region."
            )
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            self.btn_sync.setEnabled(True)
            self.btn_sync.setText("Sync Satelit")

    def _broadcast_alert(self):
        """Kirim alert ke semua region."""
        client = get_client()
        if not client.token:
            return

        reply = QMessageBox.question(
            self, "Konfirmasi",
            "Kirim alert Telegram untuk semua region BAHAYA/SIAGA?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            r = client.post("/api/v1/alert/broadcast-regions",
                            json={"force": False})
            data = r.json()
            if data.get("success"):
                QMessageBox.information(
                    self, "Broadcast",
                    data.get("message", "OK")
                )
            else:
                QMessageBox.warning(self, "Gagal",
                                    data.get("message", "Error"))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    @staticmethod
    def _quick_score(wt, temp) -> float:
        if not isinstance(wt, (int, float)) or not isinstance(temp, (int, float)):
            return 0.0
        return max(0.0, min(100.0, (-wt * 3.0) + ((temp - 25) * 2.0)))

    @staticmethod
    def _score_to_status(score: float) -> str:
        if score >= 65: return "🔴 BAHAYA"
        if score >= 40: return "🟡 SIAGA"
        return "🟢 AMAN"