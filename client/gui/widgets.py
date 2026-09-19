# client/gui/widgets.py
"""Komponen UI reusable untuk PeatFR."""
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QSizePolicy
)

from client.gui.theme import get_palette, status_badge_style, kpi_card_qss


# ============================================================
# KPI CARD
# ============================================================
class KpiCard(QFrame):
    """
    Kartu KPI dengan label + value besar + optional subtitle.

    Usage:
        card = KpiCard("Total Data", "1,240", "baris", accent="#10b981")
    """

    def __init__(
        self,
        label: str,
        value: str,
        subtitle: str = "",
        accent: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.setObjectName("KpiCard")
        self.setProperty("card", "kpi")
        self.setStyleSheet(kpi_card_qss(accent=accent))
        self.setMinimumHeight(110)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        # Label atas
        lbl = QLabel(label.upper())
        lbl.setObjectName("KpiLabel")
        layout.addWidget(lbl)

        # Value
        self.lbl_value = QLabel(value)
        self.lbl_value.setObjectName("KpiValue")
        if accent:
            self.lbl_value.setStyleSheet(
                f"color: {accent}; font-size: 28px; font-weight: 700; "
                "background: transparent;"
            )
        layout.addWidget(self.lbl_value)

        # Subtitle
        if subtitle:
            sub = QLabel(subtitle)
            sub.setObjectName("MutedLabel")
            sub.setStyleSheet(
                "color: #64748b; font-size: 11px; background: transparent;"
            )
            layout.addWidget(sub)

        layout.addStretch()

    def set_value(self, value: str):
        """Update nilai KPI secara dinamis."""
        self.lbl_value.setText(value)

    def set_accent(self, color: str):
        """Update warna accent value."""
        self.lbl_value.setStyleSheet(
            f"color: {color}; font-size: 28px; font-weight: 700; "
            "background: transparent;"
        )


# ============================================================
# STATUS BADGE
# ============================================================
class StatusBadge(QLabel):
    """
    Badge status AMAN / SIAGA / BAHAYA dengan warna neon.

    Usage:
        badge = StatusBadge("🟢 AMAN")
        badge.set_status("🔴 BAHAYA")
    """

    def __init__(self, status: str = "🟢 AMAN", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.set_status(status)

    def set_status(self, status: str):
        self.setText(status)
        self.setStyleSheet(status_badge_style(status))


# ============================================================
# SECTION TITLE
# ============================================================
class SectionTitle(QLabel):
    """Judul section dengan style konsisten."""

    def __init__(self, text: str, parent: Optional[QWidget] = None):
        super().__init__(text.upper(), parent)
        self.setObjectName("SectionLabel")
        self.setStyleSheet(
            "color: #94a3b8; font-size: 11px; font-weight: 700; "
            "letter-spacing: 1.2px; background: transparent; "
            "padding: 4px 0;"
        )


# ============================================================
# CARD (container)
# ============================================================
class Card(QFrame):
    """
    Container card dengan background gelap + border.

    Usage:
        card = Card()
        card.layout().addWidget(...)  # atau akses .body_layout
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setProperty("card", "true")
        self.body_layout = QVBoxLayout(self)
        self.body_layout.setContentsMargins(20, 18, 20, 18)
        self.body_layout.setSpacing(12)

    def layout(self):
        """Override untuk expose body_layout."""
        return self.body_layout


# ============================================================
# PLACEHOLDER
# ============================================================
class Placeholder(QWidget):
    """Widget placeholder untuk fitur yang belum diimplementasi."""

    def __init__(
        self,
        title: str = "Coming Soon",
        subtitle: str = "Fitur ini sedang dalam pengembangan.",
        icon: str = "🚧",
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        ico = QLabel(icon)
        ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ico.setStyleSheet("font-size: 64px; background: transparent;")
        layout.addWidget(ico)

        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setStyleSheet(
            "color: #f8fafc; font-size: 22px; font-weight: 700; "
            "background: transparent;"
        )
        layout.addWidget(lbl_title)

        lbl_sub = QLabel(subtitle)
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub.setStyleSheet(
            "color: #94a3b8; font-size: 13px; background: transparent;"
        )
        layout.addWidget(lbl_sub)