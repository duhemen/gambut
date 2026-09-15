# app/gui/tabs/tab_manual.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QSlider, QComboBox, QPushButton, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt

from app.utils.data_processor import (
    save_manual_input, get_dashboard_data,
    run_forecast, calculate_index
)


class ManualTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        title = QLabel("✍️ FORM INPUT DATA MANUAL HARIAN")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)

        # Group input
        group_input = QGroupBox("Parameter Kondisi Lapangan")
        group_input.setStyleSheet("""
            QGroupBox {
                font-weight: bold; color: #3498db;
                border: 1px solid #2c3034; border-radius: 8px;
                margin-top: 15px; padding-top: 15px;
            }
        """)
        input_layout = QVBoxLayout(group_input)

        self.inputs = {}
        parameters = [
            ("Tinggi Muka Air / Water Table (WT) - cm", -100, 50, 0),
            ("Kelembapan Tanah / Soil Moisture (SM) - %", 0, 100, 40),
            ("Curah Hujan / Rainfall (Rf) - mm", 0, 300, 10),
            ("Suhu Udara / Temperature (Temp) - °C", 15, 45, 30)
        ]

        for name, min_val, max_val, def_val in parameters:
            param_layout = QHBoxLayout()
            lbl = QLabel(name)
            lbl.setStyleSheet("color: #adb5bd; font-size: 13px;")
            lbl.setFixedWidth(280)

            txt_input = QLineEdit(str(def_val))
            txt_input.setFixedWidth(60)
            txt_input.setStyleSheet(
                "background-color: #2c3034; color: white; "
                "border: 1px solid #495057; border-radius: 4px; padding: 4px;"
            )

            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(min_val, max_val)
            slider.setValue(def_val)
            slider.setStyleSheet("""
                QSlider::groove:horizontal { height: 6px; background: #495057; border-radius: 3px; }
                QSlider::handle:horizontal { background: #3498db; width: 16px; margin: -5px 0; border-radius: 8px; }
            """)
            slider.valueChanged.connect(lambda val, txt=txt_input: txt.setText(str(val)))
            txt_input.textChanged.connect(
                lambda _t, s=slider: s.setValue(int(float(_t)) if _t.replace('-','').replace('.','').isdigit() else 0)
            )

            param_layout.addWidget(lbl)
            param_layout.addWidget(slider)
            param_layout.addWidget(txt_input)
            input_layout.addLayout(param_layout)

            self.inputs[name.split(" (")[0]] = txt_input

        layout.addWidget(group_input)

        # Model config
        group_model = QGroupBox("Konfigurasi Algoritma Peatfr")
        group_model.setStyleSheet(
            "QGroupBox { font-weight: bold; color: #2ecc71; "
            "border: 1px solid #2c3034; border-radius: 8px; "
            "margin-top: 10px; padding-top: 15px;}"
        )
        model_layout = QHBoxLayout(group_model)

        model_layout.addWidget(QLabel("Metode Imputasi:"))
        self.combo_impute = QComboBox()
        self.combo_impute.addItems(
            ["KNN Imputation", "Spline Interpolation", "Linear Interpolation"]
        )
        self.combo_impute.setStyleSheet(
            "background-color: #2c3034; color: white; padding: 5px; border-radius: 4px;"
        )
        model_layout.addWidget(self.combo_impute)

        model_layout.addWidget(QLabel("Model Forecasting:"))
        self.combo_forecast = QComboBox()
        self.combo_forecast.addItems(
            ["ARIMA Stochastic", "LSTM Deep Learning", "GRU Deep Learning"]
        )
        self.combo_forecast.setStyleSheet(
            "background-color: #2c3034; color: white; padding: 5px; border-radius: 4px;"
        )
        model_layout.addWidget(self.combo_forecast)

        layout.addWidget(group_model)

        self.btn_analyze = QPushButton("🔥 JALANKAN ANALISIS PREDIKSI RISIKO")
        self.btn_analyze.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; color: white; font-size: 14px;
                font-weight: bold; border-radius: 8px; padding: 12px; margin-top: 10px;
            }
            QPushButton::hover { background-color: #c0392b; }
        """)
        self.btn_analyze.clicked.connect(self.proses_analisis)
        layout.addWidget(self.btn_analyze)

        layout.addStretch()

    def proses_analisis(self):
        wt = self.inputs["Tinggi Muka Air / Water Table"].text()
        sm = self.inputs["Kelembapan Tanah / Soil Moisture"].text()
        rf = self.inputs["Curah Hujan / Rainfall"].text()
        temp = self.inputs["Suhu Udara / Temperature"].text()
        model_pilihan = self.combo_forecast.currentText()

        # 1. Simpan ke server
        sukses, pesan = save_manual_input(wt, sm, rf, temp)
        if not sukses:
            self._show_error(f"Gagal menyimpan: {pesan}")
            return

        # 2. Trigger forecast
        result_forecast = run_forecast(model_pilihan, steps=7)
        if not result_forecast.get("success"):
            self._show_error(f"Gagal forecast: {result_forecast.get('message')}")
            return
        hasil_ramalan = result_forecast.get("data", [])

        # 3. Hitung indeks
        result_idx = calculate_index(float(wt), float(sm), float(rf), float(temp))
        if result_idx.get("success"):
            score = result_idx["data"]["score"]
            status = result_idx["data"]["status"]
        else:
            score, status = 0.0, "🟢 AMAN"

        # 4. Tampilkan hasil
        teks = (
            f"<b>Status Sistem:</b> Data berhasil dihitung di server!<br><br>"
            f"<b>⚖️ KONDISI LAHAN SAAT INI (Optimisasi Nelder-Mead):</b><br>"
            f"Skor Kerawanan: <b>{score} / 100</b> -> "
            f"<span style='font-size: 14px; font-weight: bold;'>{status}</span><br><br>"
            f"<b>🔮 PREDIKSI TINGGI AIR 7 HARI KE DEPAN ({model_pilihan}):</b><br>"
            f"<span style='font-size: 15px; color: #3498db; font-weight: bold;'>"
            f"{hasil_ramalan}</span><br><br>"
            f"<i>{pesan}</i><br>"
            f"<i>Silakan cek 'Dashboard Ringkasan' untuk melihat grafik menyeluruh.</i>"
        )

        msg = QMessageBox(self)
        msg.setWindowTitle("🔮 ANALISIS SELESAI")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(teks)
        msg.setStyleSheet("""
            QMessageBox { background-color: #212529; border: 1px solid #454d55; border-radius: 10px; }
            QLabel { color: #ffffff; font-size: 13px; }
            QPushButton { background-color: #0d6efd; color: white; font-weight: bold;
                padding: 6px 20px; border-radius: 5px; min-width: 70px; }
            QPushButton:hover { background-color: #0b5ed7; }
        """)
        msg.exec()

    def _show_error(self, message: str):
        err = QMessageBox(self)
        err.setWindowTitle("🔴 GAGAL PROSES")
        err.setIcon(QMessageBox.Icon.Critical)
        err.setText(f"Terjadi kesalahan:<br><br>"
                    f"<span style='color: #e74c3c; font-weight: bold;'>{message}</span>")
        err.setStyleSheet("""
            QMessageBox { background-color: #212529; border: 1px solid #454d55; border-radius: 10px; }
            QLabel { color: #ffffff; font-size: 13px; }
            QPushButton { background-color: #e74c3c; color: white; font-weight: bold;
                padding: 6px 20px; border-radius: 5px; }
        """)
        err.exec()