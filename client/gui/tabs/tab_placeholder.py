# client/gui/tabs/tab_placeholder.py
"""Placeholder tab untuk fitur yang belum diimplementasi."""
from PyQt6.QtWidgets import QWidget

from client.gui.widgets import Placeholder


class PlaceholderTab(QWidget):
    """Tab placeholder generik."""

    def __init__(self, title: str, subtitle: str = "", icon: str = "🚧", parent=None):
        super().__init__(parent)
        from PyQt6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(Placeholder(
            title=title,
            subtitle=subtitle or "Fitur ini sedang dalam pengembangan.",
            icon=icon,
        ))