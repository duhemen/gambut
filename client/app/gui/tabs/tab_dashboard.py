# app/gui/tabs/tab_dashboard.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from app.utils.data_processor import get_dashboard_data


class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        title = QLabel("📊 PUSAT KOMANDO & RINGKASAN DATA LAHAN GAMBUT")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        main_layout.addWidget(title)

        # KPI Cards
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)
        self.card_wt = self.create_kpi_card("Tinggi Muka Air (Terkini)", "0.0 cm", "#3498db")
        self.card_temp = self.create_kpi_card("Suhu Lahan (Terkini)", "0.0 °C", "#e67e22")
        self.card_status = self.create_kpi_card("Status Risiko Lahan Gambut", "🟢 AMAN", "#2ecc71")
        kpi_layout.addWidget(self.card_wt)
        kpi_layout.addWidget(self.card_temp)
        kpi_layout.addWidget(self.card_status)
        main_layout.addLayout(kpi_layout)

        # Chart
        chart_frame = QFrame()
        chart_frame.setStyleSheet(
            "background-color: #1a1c1e; border: 1px solid #2c3034; border-radius: 12px;"
        )
        chart_layout = QGridLayout(chart_frame)
        chart_layout.setContentsMargins(15, 15, 15, 15)
        self.fig = Figure(figsize=(10, 3.5), facecolor='#1a1c1e')
        self.canvas = FigureCanvas(self.fig)
        chart_layout.addWidget(self.canvas, 0, 0)
        main_layout.addWidget(chart_frame)

        # Table
        table_title = QLabel("📋 Catatan Rekaman Data Historis Terbaru")
        table_title.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #ffffff; margin-top: 5px;"
        )
        main_layout.addWidget(table_title)

        self.data_table = QTableWidget(0, 5)
        self.setup_table_style()
        main_layout.addWidget(self.data_table)

        self.load_and_refresh_data()

    def create_kpi_card(self, title, value, accent_color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #2c3034;
                border: 1px solid #454d55;
                border-left: 5px solid {accent_color};
                border-radius: 8px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 12, 15, 12)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(
            "color: #adb5bd; font-size: 12px; font-weight: bold; "
            "border: none; background: transparent;"
        )
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(
            f"color: {accent_color}; font-size: 22px; font-weight: bold; "
            "border: none; background: transparent; margin-top: 5px;"
        )
        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_value)
        card.value_label = lbl_value
        return card

    def setup_table_style(self):
        self.data_table.horizontalHeader().setVisible(True)
        self.data_table.setHorizontalHeaderLabels(
            ["Tanggal", "WT (cm)", "SM (%)", "Rf (mm)", "Temp (°C)"]
        )
        self.data_table.setStyleSheet("""
            QTableWidget {
                background-color: #2c3034; color: #ffffff;
                border: 1px solid #454d55; gridline-color: #454d55;
                font-size: 13px; border-radius: 6px;
            }
            QTableWidget::item { color: #ffffff; background-color: #212529; }
            QHeaderView::section {
                background-color: #34495e; color: #ffffff !important;
                font-weight: bold; font-size: 13px;
                border: 1px solid #454d55; padding: 6px;
            }
        """)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.data_table.verticalHeader().setVisible(False)
        self.data_table.horizontalHeader().setFixedHeight(38)
        self.data_table.setFixedHeight(160)
        self.data_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def load_and_refresh_data(self):
        df = get_dashboard_data()
        if df.empty:
            return

        latest = df.iloc[0]
        self.card_wt.value_label.setText(f"{latest['wt']} cm")
        self.card_temp.value_label.setText(f"{latest['temp']} °C")

        try:
            wt_val = float(latest['wt'])
            temp_val = float(latest['temp'])
        except Exception:
            wt_val, temp_val = 0.0, 30.0

        if wt_val < -15.0 or temp_val > 34.0:
            self.card_status.value_label.setText("🔴 BAHAYA")
            self.card_status.value_label.setStyleSheet(
                "color: #e74c3c; font-size: 22px; font-weight: bold;"
            )
            self.card_status.setStyleSheet(
                "QFrame { background-color: #2c3034; border: 1px solid #454d55; "
                "border-left: 5px solid #e74c3c; border-radius: 8px; }"
            )
        elif wt_val < -10.0:
            self.card_status.value_label.setText("🟡 SIAGA")
            self.card_status.value_label.setStyleSheet(
                "color: #f1c40f; font-size: 22px; font-weight: bold;"
            )
            self.card_status.setStyleSheet(
                "QFrame { background-color: #2c3034; border: 1px solid #454d55; "
                "border-left: 5px solid #f1c40f; border-radius: 8px; }"
            )
        else:
            self.card_status.value_label.setText("🟢 AMAN")
            self.card_status.value_label.setStyleSheet(
                "color: #2ecc71; font-size: 22px; font-weight: bold;"
            )
            self.card_status.setStyleSheet(
                "QFrame { background-color: #2c3034; border: 1px solid #454d55; "
                "border-left: 5px solid #2ecc71; border-radius: 8px; }"
            )

        # Table
        self.data_table.setRowCount(0)
        df_head = df.head(10)
        for row_idx, (_, row) in enumerate(df_head.iterrows()):
            self.data_table.insertRow(row_idx)
            vals = [str(row['tanggal']), str(row['wt']), str(row['sm']),
                    str(row['rf']), str(row['temp'])]
            for col_idx, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.data_table.setItem(row_idx, col_idx, item)

        # Chart
        self.fig.clear()
        df_chrono = df.head(10).sort_values(by='tanggal')

        ax1 = self.fig.add_subplot(121)
        ax1.set_facecolor('#1a1c1e')
        try:
            ax1.plot(df_chrono['tanggal'].astype(str),
                     df_chrono['wt'].astype(float),
                     color='#3498db', marker='o', linewidth=2)
        except Exception:
            pass
        ax1.set_title("Tren Tinggi Muka Air (WT)",
                      color='white', fontsize=11, fontweight='bold')
        ax1.tick_params(colors='white', labelsize=8, rotation=15)
        ax1.grid(True, color='#2c3034', linestyle='--')

        ax2 = self.fig.add_subplot(122)
        ax2.set_facecolor('#1a1c1e')

        try:
            total_days = len(df)
            danger_days = len(df[(df['wt'].astype(float) < -15) |
                                 (df['temp'].astype(float) > 34)])
            warning_days = len(df[(df['wt'].astype(float) >= -15) &
                                  (df['wt'].astype(float) < -10)])
            safe_days = max(0, total_days - danger_days - warning_days)
        except Exception:
            safe_days, warning_days, danger_days = 1, 0, 0

        counts = [safe_days, warning_days, danger_days]
        if sum(counts) == 0:
            counts = [1, 0, 0]

        ax2.pie(counts, labels=['Aman', 'Siaga', 'Bahaya'],
                autopct='%1.1f%%',
                colors=['#2ecc71', '#f1c40f', '#e74c3c'],
                startangle=90, textprops=dict(color="white"))
        ax2.set_title("Proporsi Status Risiko Lahan",
                      color='white', fontsize=11, fontweight='bold')

        self.fig.tight_layout()
        self.canvas.draw()