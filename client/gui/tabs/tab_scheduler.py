# client/gui/tabs/tab_scheduler.py
"""Tab Scheduler — kontrol auto-fetch satelit."""
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QMessageBox, QComboBox, QSpinBox
)

from client.gui.widgets import KpiCard, SectionTitle, Card
from client.api.client import get_client


class SchedulerTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh()

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(30_000)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        # Header
        header = QVBoxLayout()
        header.setSpacing(2)

        title = QLabel("Scheduler Otomatis")
        title.setObjectName("TitleLabel")
        header.addWidget(title)

        subtitle = QLabel(
            "Fetch data satelit NASA FIRMS otomatis setiap X jam. "
            "Data langsung tersimpan & alert dikirim kalau BAHAYA."
        )
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setWordWrap(True)
        header.addWidget(subtitle)

        root.addLayout(header)

        # KPI
        root.addWidget(SectionTitle("Status Scheduler"))

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(16)

        self.kpi_status = KpiCard("Status", "—", "running/stopped", "#10b981")
        self.kpi_interval = KpiCard("Interval", "—", "jam", "#0d6efd")
        self.kpi_runs = KpiCard("Total Runs", "—", "kali", "#f59e0b")
        self.kpi_errors = KpiCard("Errors", "—", "kali", "#ef4444")

        for c in (self.kpi_status, self.kpi_interval, self.kpi_runs, self.kpi_errors):
            kpi_row.addWidget(c)
        root.addLayout(kpi_row)

        # Info
        root.addWidget(SectionTitle("Informasi"))

        info_card = Card()
        info_grid = QGridLayout()
        info_grid.setHorizontalSpacing(16)
        info_grid.setVerticalSpacing(10)

        lbl_last = QLabel("Terakhir Jalan")
        lbl_last.setObjectName("MutedLabel")
        info_grid.addWidget(lbl_last, 0, 0)
        self.lbl_last_run = QLabel("—")
        self.lbl_last_run.setStyleSheet(
            "color: #10b981; font-size: 13px; font-weight: 600; background: transparent;"
        )
        info_grid.addWidget(self.lbl_last_run, 0, 1)

        lbl_next = QLabel("Jadwal Berikutnya")
        lbl_next.setObjectName("MutedLabel")
        info_grid.addWidget(lbl_next, 1, 0)
        self.lbl_next_run = QLabel("—")
        self.lbl_next_run.setStyleSheet(
            "color: #0d6efd; font-size: 13px; font-weight: 600; background: transparent;"
        )
        info_grid.addWidget(self.lbl_next_run, 1, 1)

        lbl_regions = QLabel("Region Aktif")
        lbl_regions.setObjectName("MutedLabel")
        info_grid.addWidget(lbl_regions, 2, 0)
        self.lbl_regions = QLabel("—")
        self.lbl_regions.setStyleSheet(
            "color: #cbd5e1; font-size: 13px; background: transparent;"
        )
        info_grid.addWidget(self.lbl_regions, 2, 1)

        lbl_result = QLabel("Hasil Terakhir")
        lbl_result.setObjectName("MutedLabel")
        info_grid.addWidget(lbl_result, 3, 0)
        self.lbl_result = QLabel("—")
        self.lbl_result.setStyleSheet(
            "color: #94a3b8; font-size: 12px; background: transparent;"
        )
        self.lbl_result.setWordWrap(True)
        info_grid.addWidget(self.lbl_result, 3, 1)

        info_card.layout().addLayout(info_grid)
        root.addWidget(info_card)

        # Kontrol
        root.addWidget(SectionTitle("Kontrol"))

        control_card = Card()

        interval_row = QHBoxLayout()
        interval_row.setSpacing(12)

        lbl_interval = QLabel("Interval (jam):")
        lbl_interval.setObjectName("MutedLabel")
        interval_row.addWidget(lbl_interval)

        self.spin_interval = QSpinBox()
        self.spin_interval.setRange(1, 72)
        self.spin_interval.setValue(6)
        self.spin_interval.setSuffix(" jam")
        interval_row.addWidget(self.spin_interval)

        interval_row.addStretch()
        control_card.layout().addLayout(interval_row)

        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self.btn_start = QPushButton("▶️  Start Scheduler")
        self.btn_start.setProperty("variant", "success")
        self.btn_start.clicked.connect(self._start_scheduler)
        action_row.addWidget(self.btn_start)

        self.btn_stop = QPushButton("⏸️  Stop Scheduler")
        self.btn_stop.setProperty("variant", "danger")
        self.btn_stop.clicked.connect(self._stop_scheduler)
        action_row.addWidget(self.btn_stop)

        self.btn_trigger = QPushButton("⚡ Trigger Sekarang")
        self.btn_trigger.clicked.connect(self._trigger_now)
        action_row.addWidget(self.btn_trigger)

        action_row.addStretch()
        control_card.layout().addLayout(action_row)

        root.addWidget(control_card)
        root.addStretch()

    def refresh(self):
        client = get_client()
        if not client.token:
            return

        try:
            r = client.get("/api/v1/scheduler/status")
            if r.status_code != 200:
                return

            data = r.json().get("data", {})

            running = data.get("running", False)
            self.kpi_status.set_value("RUNNING" if running else "STOPPED")
            self.kpi_status.set_accent("#10b981" if running else "#ef4444")

            self.kpi_interval.set_value(str(data.get("interval_hours", "—")))
            self.kpi_runs.set_value(str(data.get("total_runs", 0)))
            self.kpi_errors.set_value(str(data.get("total_errors", 0)))

            self.lbl_last_run.setText(str(data.get("last_run", "Belum pernah"))[:19])
            nxt = data.get("next_run")
            self.lbl_next_run.setText(str(nxt)[:19] if nxt else "—")

            regions = data.get("regions", [])
            self.lbl_regions.setText(", ".join(regions) if regions else "—")

            last_result = data.get("last_result", {})
            if last_result:
                parts = []
                for region, info in last_result.items():
                    if "error" in info:
                        parts.append(f"{region}: error")
                    else:
                        parts.append(f"{region}: {info.get('fetched', 0)} hotspot")
                self.lbl_result.setText(" | ".join(parts))
            else:
                self.lbl_result.setText("Belum ada eksekusi.")

            self.btn_start.setEnabled(not running)
            self.btn_stop.setEnabled(running)

        except Exception as e:
            print(f"WARN [SCHEDULER-TAB] {e}")

    def _start_scheduler(self):
        client = get_client()
        if not client.token:
            return
        interval = self.spin_interval.value()
        try:
            r = client.post("/api/v1/scheduler/start",
                            json={"interval_hours": interval})
            if r.status_code == 200:
                QMessageBox.information(self, "Scheduler Aktif",
                    f"Auto-fetch dijalankan setiap {interval} jam.")
                self.refresh()
            else:
                QMessageBox.warning(self, "Gagal", f"HTTP {r.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _stop_scheduler(self):
        client = get_client()
        if not client.token:
            return
        try:
            r = client.post("/api/v1/scheduler/stop")
            if r.status_code == 200:
                QMessageBox.information(self, "Scheduler Stop", "Scheduler dihentikan.")
                self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _trigger_now(self):
        client = get_client()
        if not client.token:
            return
        self.btn_trigger.setEnabled(False)
        self.btn_trigger.setText("Menjalankan...")
        try:
            r = client.post("/api/v1/scheduler/trigger")
            data = r.json()
            if r.status_code == 200:
                QMessageBox.information(self, "Trigger Sukses",
                    f"Auto-fetch selesai.\n\n{data.get('message', 'OK')}")
                self.refresh()
            else:
                QMessageBox.warning(self, "Gagal", f"HTTP {r.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            self.btn_trigger.setEnabled(True)
            self.btn_trigger.setText("Trigger Sekarang")
