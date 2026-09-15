# app/gui/tabs/tab_upload.py
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt

from app.utils.data_processor import read_and_validate_file


class UploadTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        header_layout = QHBoxLayout()
        title = QLabel("📁 UNGGAH DATA REKAMAN LAPANGAN (EXCEL / CSV)")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        header_layout.addWidget(title)

        self.btn_template = QPushButton("📥 Unduh Template (.xlsx)")
        self.btn_template.setStyleSheet("""
            QPushButton { background-color: #2ecc71; color: white; font-weight: bold;
                padding: 6px 12px; border-radius: 6px; font-size: 12px; }
            QPushButton::hover { background-color: #27ae60; }
        """)
        self.btn_template.clicked.connect(self.unduh_template_excel)
        header_layout.addWidget(self.btn_template, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(header_layout)

        # Drop area
        self.drop_area = QFrame()
        self.drop_area.setObjectName("DropArea")
        self.drop_area.setMinimumHeight(200)
        self.drop_area.setStyleSheet("""
            QFrame#DropArea {
                border: 2px dashed #495057; border-radius: 12px;
                background-color: #2c3034;
            }
        """)
        drop_layout = QVBoxLayout(self.drop_area)
        drop_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_label = QLabel("📥")
        self.icon_label.setStyleSheet("font-size: 54px; margin-bottom: 5px;")
        drop_layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.text_label = QLabel(
            "Seret dan jatuhkan file Excel atau CSV Anda di sini\n- atau -"
        )
        self.text_label.setStyleSheet(
            "color: #adb5bd; font-size: 14px; font-weight: 500; line-height: 150%;"
        )
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(self.text_label)

        self.btn_browse = QPushButton("Pilih Berkas Komputer")
        self.btn_browse.setFixedWidth(180)
        self.btn_browse.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; font-weight: bold;
                padding: 10px 15px; border-radius: 6px; margin-top: 10px; font-size: 13px; }
            QPushButton::hover { background-color: #2980b9; }
        """)
        self.btn_browse.clicked.connect(self.browse_file)
        drop_layout.addWidget(self.btn_browse, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.drop_area)

        # Panduan
        guide_frame = QFrame()
        guide_frame.setStyleSheet(
            "background-color: #1a1c1e; border: 1px solid #2c3034; "
            "border-radius: 8px; padding: 10px;"
        )
        guide_layout = QVBoxLayout(guide_frame)

        guide_title = QLabel(
            "⚠️ Format kolom wajib (harus sama persis): "
            "tanggal, wt, sm, rf, temp"
        )
        guide_title.setStyleSheet(
            "color: #e67e22; font-weight: bold; font-size: 12px; border: none;"
        )
        guide_layout.addWidget(guide_title)

        self.sample_table = QTableWidget(2, 5)
        self.sample_table.horizontalHeader().setVisible(True)
        self.sample_table.setHorizontalHeaderLabels(
            ["tanggal", "wt", "sm", "rf", "temp"]
        )
        sample_rows = [
            ("2026-09-15", "-12", "45", "0", "32.5"),
            ("2026-09-16", "-15", "42", "0.0", "33.1"),
        ]
        for r, row in enumerate(sample_rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.sample_table.setItem(r, c, item)

        self.sample_table.setStyleSheet("""
            QTableWidget { background-color: #2c3034; color: #ffffff;
                border: 1px solid #454d55; gridline-color: #454d55;
                font-size: 13px; border-radius: 6px; }
            QTableWidget::item { color: #ffffff; background-color: #212529; }
            QHeaderView::section { background-color: #34495e;
                color: #ffffff !important; font-weight: bold; font-size: 12px;
                border: 1px solid #454d55; padding: 2px 4px; }
        """)
        self.sample_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.sample_table.verticalHeader().setVisible(False)
        self.sample_table.horizontalHeader().setFixedHeight(45)
        self.sample_table.setRowHeight(0, 35)
        self.sample_table.setRowHeight(1, 35)
        self.sample_table.setFixedHeight(135)
        self.sample_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        guide_layout.addWidget(self.sample_table)

        layout.addWidget(guide_frame)

        # Status box
        self.status_box = QFrame()
        self.status_box.setStyleSheet(
            "background-color: #2c3034; border-radius: 8px; border: 1px solid #495057;"
        )
        status_layout = QHBoxLayout(self.status_box)
        status_layout.setContentsMargins(15, 12, 15, 12)

        self.status_log = QLabel("Status: Menunggu unggahan berkas data lapangan...")
        self.status_log.setStyleSheet(
            "color: #adb5bd; font-size: 13px; font-weight: 500; border: none;"
        )
        status_layout.addWidget(self.status_log)

        layout.addWidget(self.status_box)
        layout.addStretch()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_area.setStyleSheet(
                "QFrame#DropArea { border: 2px dashed #3498db; "
                "background-color: #343a40; }"
            )

    def dragLeaveEvent(self, event):
        self.drop_area.setStyleSheet(
            "QFrame#DropArea { border: 2px dashed #495057; "
            "background-color: #2c3034; }"
        )

    def dropEvent(self, event):
        self.drop_area.setStyleSheet(
            "QFrame#DropArea { border: 2px dashed #495057; "
            "background-color: #2c3034; }"
        )
        urls = event.mimeData().urls()
        if urls:
            self.proses_berkas(urls[0].toLocalFile())

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Berkas Lapangan", "",
            "Data Files (*.csv *.xlsx *.xls)"
        )
        if file_path:
            self.proses_berkas(file_path)

    def proses_berkas(self, file_path):
        self.status_log.setText("⏳ Mengunggah berkas ke server...")
        self.status_box.setStyleSheet(
            "background-color: #2c3034; border: 1px solid #3498db; border-radius: 8px;"
        )
        self.status_log.setStyleSheet(
            "color: #adb5bd; font-size: 13px; font-weight: bold; border: none;"
        )

        sukses, pesan, _ = read_and_validate_file(file_path)

        if sukses:
            self.status_box.setStyleSheet(
                "background-color: #1e4620; border: 1px solid #2ecc71; border-radius: 8px;"
            )
            self.status_log.setStyleSheet(
                "color: #2ecc71; font-size: 14px; font-weight: bold; border: none;"
            )
            self.status_log.setText(f"🟢 BERHASIL: {pesan}")
        else:
            self.status_box.setStyleSheet(
                "background-color: #5c1d1d; border: 1px solid #e74c3c; border-radius: 8px;"
            )
            self.status_log.setStyleSheet(
                "color: #ea868f; font-size: 14px; font-weight: bold; border: none;"
            )
            self.status_log.setText(f"🔴 KESALAHAN: {pesan}")

    def unduh_template_excel(self):
        """Buat template Excel lokal untuk diisi petugas"""
        import pandas as pd

        save_path = os.path.join("data", "template_input.xlsx")
        os.makedirs("data", exist_ok=True)

        try:
            df = pd.DataFrame(columns=['tanggal', 'wt', 'sm', 'rf', 'temp'])
            df.loc[0] = ["2026-09-15", -12.0, 45.0, 0.0, 32.5]
            df.to_excel(save_path, index=False)

            msg = QMessageBox(self)
            msg.setWindowTitle("📥 DOWNLOAD SUKSES")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText(
                f"<b>Berhasil mengunduh berkas template!</b><br><br>"
                f"File disimpan di:<br>"
                f"<span style='color: #2ecc71; font-weight: bold;'>"
                f"{os.path.abspath(save_path)}</span><br><br>"
                f"<i>Silakan isi file tersebut menggunakan Excel, "
                f"lalu seret berkasnya ke kotak Drop Area.</i>"
            )
            msg.setStyleSheet("""
                QMessageBox { background-color: #212529; border: 1px solid #454d55; border-radius: 10px; }
                QLabel { color: #ffffff; font-size: 13px; }
                QPushButton { background-color: #2ecc71; color: white; font-weight: bold;
                    padding: 6px 15px; border-radius: 5px; }
            """)
            msg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Gagal Download",
                                 f"Terjadi kesalahan: {str(e)}")