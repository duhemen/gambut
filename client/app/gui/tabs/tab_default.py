# app/gui/tabs/tab_default.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt

from app.utils.data_processor import get_dashboard_data, sync_satellite_data


class DefaultTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        title = QLabel("📡 DATA INDEKS BAWAAN SATELIT (TERINTEGRASI)")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        header_layout.addWidget(title)

        header_layout.addWidget(QLabel("Metode Imputasi Satelit:"),
                                alignment=Qt.AlignmentFlag.AlignRight)
        self.combo_impute = QComboBox()
        self.combo_impute.addItems(["KNN Imputer", "Spline Curve", "Linear Method"])
        self.combo_impute.setStyleSheet(
            "background-color: #2c3034; color: white; padding: 5px; "
            "border-radius: 4px; min-width: 130px;"
        )
        header_layout.addWidget(self.combo_impute)

        self.btn_sync = QPushButton("🔄 Sinkronisasi Data Satelit")
        self.btn_sync.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white; font-weight: bold;
                padding: 8px 16px; border-radius: 6px; font-size: 13px;
            }
            QPushButton::hover { background-color: #2980b9; }
            QPushButton:disabled { background-color: #495057; color: #adb5bd; }
        """)
        self.btn_sync.clicked.connect(self.sinkronisasi_satelit_riil)
        header_layout.addWidget(self.btn_sync, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(header_layout)

        self.info_lbl = QLabel("Status: Siap menghubungkan data stasiun satelit cuaca lokal.")
        self.info_lbl.setStyleSheet(
            "color: #adb5bd; font-size: 13px; font-style: italic; "
            "background-color: #1a1c1e; padding: 8px; border-radius: 6px;"
        )
        layout.addWidget(self.info_lbl)

        self.sat_table = QTableWidget(0, 5)
        self.setup_table_style()
        layout.addWidget(self.sat_table)

        self.refresh_table_display()

    def setup_table_style(self):
        self.sat_table.horizontalHeader().setVisible(True)
        self.sat_table.setHorizontalHeaderLabels([
            "Tanggal", "Water Table / WT (cm)", "Soil Moisture / SM (%)",
            "Rainfall / Rf (mm)", "Temperature / Temp (°C)"
        ])
        self.sat_table.setStyleSheet("""
            QTableWidget { background-color: #2c3034; color: #ffffff;
                border: 1px solid #454d55; gridline-color: #454d55;
                font-size: 13px; border-radius: 8px; }
            QTableWidget::item { color: #ffffff; background-color: #212529; padding: 8px; }
            QHeaderView::section { background-color: #34495e; color: #ffffff !important;
                font-weight: bold; font-size: 13px; border: 1px solid #454d55; padding: 8px; }
        """)
        self.sat_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sat_table.verticalHeader().setVisible(False)
        self.sat_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def refresh_table_display(self):
        df = get_dashboard_data()
        if df.empty:
            return
        self.sat_table.setRowCount(0)
        for row_idx, (_, row) in enumerate(df.iterrows()):
            self.sat_table.insertRow(row_idx)
            vals = [str(row['tanggal']), f"{row['wt']} cm", f"{row['sm']} %",
                    f"{row['rf']} mm", f"{row['temp']} °C"]
            for col_idx, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.sat_table.setItem(row_idx, col_idx, item)

    def sinkronisasi_satelit_riil(self):
        self.btn_sync.setEnabled(False)
        self.btn_sync.setText("⏳ Memproses & Menambal Data...")
        self.info_lbl.setText("Menghubungi server untuk imputasi satelit...")
        self.info_lbl.setStyleSheet("color: #adb5bd; font-size: 13px;")

        method = self.combo_impute.currentText()
        result = sync_satellite_data(method)

        if result.get("success"):
            self.refresh_table_display()
            self.info_lbl.setText(
                f"🟢 SINKRONISASI BERHASIL: {result.get('message')}"
            )
            self.info_lbl.setStyleSheet(
                "color: #2ecc71; font-weight: bold; font-size: 13px;"
            )
        else:
            self.info_lbl.setText(
                f"🔴 GAGAL SINKRONISASI: {result.get('message')}"
            )
            self.info_lbl.setStyleSheet(
                "color: #e74c3c; font-weight: bold; font-size: 13px;"
            )

        self.btn_sync.setEnabled(True)
        self.btn_sync.setText("🔄 Sinkronisasi Data Satelit")