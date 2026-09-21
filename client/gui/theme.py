# client/gui/theme.py
"""
Tema terpusat untuk aplikasi PeatFR.

Single source of truth untuk:
- Palet warna (dark & light mode)
- QSS untuk semua widget
- Helper untuk status badge (AMAN/SIAGA/BAHAYA)
- Aurora background widget

Usage:
    from client.gui.theme import apply_theme, ThemeMode
    apply_theme(app, ThemeMode.DARK)
"""
from enum import Enum
from typing import Optional

from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QPainter, QRadialGradient
from PyQt6.QtWidgets import QApplication, QWidget

from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QComboBox, QApplication

# ============================================================
# THEME MODE
# ============================================================
class ThemeMode(str, Enum):
    DARK = "dark"
    LIGHT = "light"


# ============================================================
# HELPERS
# ============================================================
def hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert '#RRGGBB' + alpha (0.0-1.0) → 'rgba(r, g, b, a)'."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


# ============================================================
# COLOR PALETTES
# ============================================================
# Warna yang sama di kedua mode
_BASE = {
    "accent_primary":         "#0d6efd",
    "accent_primary_hover":   "#0b5ed7",
    "accent_primary_pressed": "#0a53be",
    "accent_neon":            "#10b981",
    "accent_neon_hover":      "#059669",
    "accent_warning":         "#f59e0b",
    "accent_warning_hover":   "#d97706",
    "accent_danger":          "#ef4444",
    "accent_danger_hover":    "#dc2626",
}

PALETTE_DARK = {
    **_BASE,
    # Backgrounds
    "bg_primary":     "#0b0f19",
    "bg_secondary":   "#111827",
    "bg_card":        "#1e293b",
    "bg_input":       "#1f2937",
    "bg_hover":       "#334155",
    "bg_overlay":     "rgba(11, 15, 25, 0.85)",
    # Borders
    "border":         "#334155",
    "border_focus":   "#10b981",
    # Text
    "text_primary":   "#f8fafc",
    "text_secondary": "#cbd5e1",
    "text_muted":     "#94a3b8",
    # Status
    "status_aman":    "#10b981",
    "status_siaga":   "#f59e0b",
    "status_bahaya":  "#ef4444",
    # Aurora overlay (dipakai di AuroraBackground)
    "aurora_1":       "rgba(16, 185, 129, 55)",   # emerald
    "aurora_2":       "rgba(13, 110, 253, 45)",   # blue
    "aurora_3":       "rgba(139, 92, 246, 35)",   # violet
}

PALETTE_LIGHT = {
    **_BASE,
    # Backgrounds
    "bg_primary":     "#f8fafc",
    "bg_secondary":   "#ffffff",
    "bg_card":        "#ffffff",
    "bg_input":       "#f1f5f9",
    "bg_hover":       "#e2e8f0",
    "bg_overlay":     "rgba(248, 250, 252, 0.85)",
    # Borders
    "border":         "#cbd5e1",
    "border_focus":   "#0d6efd",
    # Text
    "text_primary":   "#0f172a",
    "text_secondary": "#334155",
    "text_muted":     "#64748b",
    # Status
    "status_aman":    "#059669",
    "status_siaga":   "#d97706",
    "status_bahaya":  "#dc2626",
    # Aurora overlay
    "aurora_1":       "rgba(16, 185, 129, 30)",
    "aurora_2":       "rgba(13, 110, 253, 25)",
    "aurora_3":       "rgba(139, 92, 246, 20)",
}


# ============================================================
# QSS TEMPLATE
# ============================================================
# Menggunakan sintaks @nama_var supaya aman dari konflik
# dengan kurung kurawal {} yang banyak di QSS.
_QSS_TEMPLATE = """
/* ============================================================
   GLOBAL
   ============================================================ */
QWidget {
    background-color: @bg_primary;
    color: @text_primary;
    font-family: 'Segoe UI', 'Inter', 'Roboto', sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: @bg_primary;
}

/* ============================================================
   TYPOGRAPHY
   ============================================================ */
QLabel {
    background: transparent;
    color: @text_primary;
}

QLabel#TitleLabel {
    font-size: 22px;
    font-weight: 700;
    color: @text_primary;
    background: transparent;
}

QLabel#SubtitleLabel {
    font-size: 12px;
    color: @text_muted;
    background: transparent;
}

QLabel#SectionLabel {
    font-size: 11px;
    font-weight: 700;
    color: @text_muted;
    letter-spacing: 1px;
    background: transparent;
}

QLabel#MutedLabel {
    color: @text_muted;
    font-size: 12px;
    background: transparent;
}

QLabel#KpiValue {
    font-size: 28px;
    font-weight: 700;
    color: @accent_neon;
    background: transparent;
}

QLabel#KpiLabel {
    font-size: 11px;
    font-weight: 600;
    color: @text_muted;
    letter-spacing: 0.8px;
    background: transparent;
}

/* ============================================================
   BUTTONS
   ============================================================ */
QPushButton {
    background-color: @accent_primary;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 10px 18px;
    font-size: 13px;
    font-weight: 600;
    min-height: 20px;
}
QPushButton:hover {
    background-color: @accent_primary_hover;
}
QPushButton:pressed {
    background-color: @accent_primary_pressed;
}
QPushButton:disabled {
    background-color: @bg_hover;
    color: @text_muted;
}

QPushButton[variant="secondary"] {
    background-color: @bg_card;
    color: @text_primary;
    border: 1px solid @border;
}
QPushButton[variant="secondary"]:hover {
    background-color: @bg_hover;
    border-color: @accent_primary;
}

QPushButton[variant="danger"] {
    background-color: @accent_danger;
}
QPushButton[variant="danger"]:hover {
    background-color: @accent_danger_hover;
}

QPushButton[variant="success"] {
    background-color: @accent_neon;
}
QPushButton[variant="success"]:hover {
    background-color: @accent_neon_hover;
}

QPushButton[variant="ghost"] {
    background: transparent;
    color: @text_secondary;
    border: 1px solid transparent;
    padding: 8px 14px;
}
QPushButton[variant="ghost"]:hover {
    background-color: @bg_hover;
    color: @text_primary;
}

/* ============================================================
   INPUTS
   ============================================================ */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: @bg_input;
    color: @text_primary;
    border: 1px solid @border;
    border-radius: 6px;
    padding: 9px 12px;
    selection-background-color: @accent_primary;
    selection-color: #ffffff;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid @accent_neon;
}
QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
    background-color: @bg_secondary;
    color: @text_muted;
}

/* ============================================================
   COMBOBOX — VISIBILITY FIXED
   ============================================================ */
QComboBox {
    background-color: #1f2937;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 12px;
    padding-right: 32px;
    min-height: 22px;
    min-width: 150px;
    font-size: 13px;
}
QComboBox:hover {
    border: 1px solid #0d6efd;
    background-color: #2c3034;
}
QComboBox:focus {
    border: 1px solid #10b981;
    background-color: #2c3034;
}
QComboBox:on {
    border: 1px solid #10b981;
}
QComboBox:disabled {
    background-color: #111827;
    color: #64748b;
    border: 1px solid #334155;
}

/* Tombol dropdown (panah) */
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: center right;
    border: none;
    width: 28px;
    background: transparent;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #94a3b8;
    width: 0;
    height: 0;
    margin-right: 10px;
}
QComboBox::down-arrow:hover {
    border-top-color: #10b981;
}

/* ⚠️ POPUP LIST — pakai hardcoded color biar PASTI kelihatan */
QComboBox QAbstractItemView {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 4px;
    outline: 0;
    selection-background-color: #0d6efd;
    selection-color: #ffffff;
    font-size: 13px;
}

QComboBox QAbstractItemView::item {
    min-height: 28px;
    padding: 6px 12px;
    color: #f8fafc;
    background-color: transparent;
    border-radius: 4px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #334155;
    color: #ffffff;
}

QComboBox QAbstractItemView::item:selected {
    background-color: #0d6efd;
    color: #ffffff;
    font-weight: 600;
}

QComboBox QAbstractItemView::item:disabled {
    color: #64748b;
}

QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit {
    background-color: @bg_input;
    color: @text_primary;
    border: 1px solid @border;
    border-radius: 6px;
    padding: 8px 10px;
}
QSpinBox:focus, QDoubleSpinBox:focus,
QDateEdit:focus, QTimeEdit:focus {
    border: 1px solid @accent_neon;
}

QCheckBox, QRadioButton {
    color: @text_primary;
    spacing: 8px;
    background: transparent;
}
QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid @border;
    background: @bg_input;
}
QCheckBox::indicator { border-radius: 4px; }
QRadioButton::indicator { border-radius: 8px; }
QCheckBox::indicator:checked,
QRadioButton::indicator:checked {
    background-color: @accent_neon;
    border-color: @accent_neon;
}
QCheckBox::indicator:hover,
QRadioButton::indicator:hover {
    border-color: @accent_neon;
}

/* ============================================================
   TABS
   ============================================================ */
QTabWidget::pane {
    background: @bg_secondary;
    border: 1px solid @border;
    border-radius: 8px;
    top: -1px;
}
QTabBar::tab {
    background: transparent;
    color: @text_muted;
    padding: 10px 20px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 500;
}
QTabBar::tab:hover {
    color: @text_primary;
    background: @bg_hover;
}
QTabBar::tab:selected {
    background: @accent_neon;
    color: #ffffff;
    font-weight: 700;
}

/* ============================================================
   TABLES
   ============================================================ */
QTableWidget, QTableView {
    background-color: @bg_secondary;
    alternate-background-color: @bg_card;
    color: @text_primary;
    border: 1px solid @border;
    border-radius: 8px;
    gridline-color: @border;
    selection-background-color: @accent_primary;
    selection-color: #ffffff;
    outline: 0;
}
QTableWidget::item, QTableView::item {
    padding: 8px;
    border: none;
}
QTableWidget::item:hover, QTableView::item:hover {
    background-color: @bg_hover;
}
QHeaderView::section {
    background-color: @bg_card;
    color: @text_secondary;
    padding: 10px 12px;
    border: none;
    border-right: 1px solid @border;
    border-bottom: 1px solid @border;
    font-weight: 700;
    font-size: 12px;
}
QTableCornerButton::section {
    background-color: @bg_card;
    border: none;
}

/* ============================================================
   GROUP BOX
   ============================================================ */
QGroupBox {
    background-color: @bg_card;
    border: 1px solid @border;
    border-radius: 10px;
    margin-top: 18px;
    padding: 18px 12px 12px 12px;
    font-weight: 600;
    color: @text_primary;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 10px;
    color: @accent_neon;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

/* ============================================================
   CARDS (via QFrame property)
   ============================================================ */
QFrame[card="true"] {
    background-color: @bg_card;
    border: 1px solid @border;
    border-radius: 12px;
}
QFrame[card="kpi"] {
    background-color: @bg_card;
    border: 1px solid @border;
    border-radius: 12px;
}
QFrame[card="aurora"] {
    background-color: @bg_card;
    border: 1px solid @accent_neon;
    border-radius: 12px;
}

/* ============================================================
   SCROLL BARS
   ============================================================ */
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: @border;
    border-radius: 5px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover {
    background: @text_muted;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}
QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: @border;
    border-radius: 5px;
    min-width: 24px;
}
QScrollBar::handle:horizontal:hover {
    background: @text_muted;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: transparent;
}

/* ============================================================
   PROGRESS BAR
   ============================================================ */
QProgressBar {
    background-color: @bg_input;
    border: 1px solid @border;
    border-radius: 6px;
    text-align: center;
    color: @text_primary;
    height: 20px;
}
QProgressBar::chunk {
    background-color: @accent_neon;
    border-radius: 5px;
}

/* ============================================================
   MENU
   ============================================================ */
QMenuBar {
    background-color: @bg_secondary;
    color: @text_primary;
}
QMenuBar::item {
    background: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}
QMenuBar::item:selected {
    background-color: @bg_hover;
}
QMenu {
    background-color: @bg_card;
    color: @text_primary;
    border: 1px solid @border;
    border-radius: 8px;
    padding: 6px;
}
QMenu::item {
    padding: 8px 20px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: @accent_primary;
    color: #ffffff;
}
QMenu::separator {
    height: 1px;
    background: @border;
    margin: 4px 8px;
}

/* ============================================================
   TOOLTIP
   ============================================================ */
QToolTip {
    background-color: @bg_card;
    color: @text_primary;
    border: 1px solid @border;
    border-radius: 6px;
    padding: 6px 10px;
}

/* ============================================================
   STATUS BADGES
   ============================================================ */
QLabel[status="aman"] {
    background-color: @status_aman_bg;
    color: @status_aman;
    border: 1px solid @status_aman;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 700;
    font-size: 13px;
}
QLabel[status="siaga"] {
    background-color: @status_siaga_bg;
    color: @status_siaga;
    border: 1px solid @status_siaga;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 700;
    font-size: 13px;
}
QLabel[status="bahaya"] {
    background-color: @status_bahaya_bg;
    color: @status_bahaya;
    border: 1px solid @status_bahaya;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 700;
    font-size: 13px;
}

/* ============================================================
   SPLITTER
   ============================================================ */
QSplitter::handle {
    background-color: @border;
}
QSplitter::handle:hover {
    background-color: @accent_neon;
}
"""


# ============================================================
# INTERNAL STATE
# ============================================================
_current_mode: ThemeMode = ThemeMode.DARK


# ============================================================
# PUBLIC API
# ============================================================
def get_palette(mode: Optional[ThemeMode | str] = None) -> dict:
    """Return dict warna sesuai mode. Kalau None, pakai mode saat ini."""
    if mode is None:
        mode = _current_mode
    if isinstance(mode, str):
        mode = ThemeMode(mode.lower())
    palette = dict(PALETTE_DARK if mode == ThemeMode.DARK else PALETTE_LIGHT)
    # Turunkan status_bg dari warna status (alpha 0.15)
    palette["status_aman_bg"] = hex_to_rgba(palette["status_aman"], 0.15)
    palette["status_siaga_bg"] = hex_to_rgba(palette["status_siaga"], 0.15)
    palette["status_bahaya_bg"] = hex_to_rgba(palette["status_bahaya"], 0.15)
    return palette


def get_stylesheet(mode: Optional[ThemeMode | str] = None) -> str:
    """Return QSS lengkap dengan warna sudah di-inject."""
    palette = get_palette(mode)
    qss = _QSS_TEMPLATE

    # ⚠️ PENTING: sort by length DESC
    # Supaya 'accent_primary_hover' di-replace SEBELUM 'accent_primary'
    # (kalau tidak, 'accent_primary' dulu akan jadi '#0d6efd_hover')
    for key in sorted(palette.keys(), key=len, reverse=True):
        qss = qss.replace(f"@{key}", palette[key])

    # Sanity check — kalau masih ada @xxx yang belum ke-replace
    import re
    leftover = re.findall(r"@[a-z_]+", qss)
    if leftover:
        print(f"⚠️ [THEME] Placeholder belum di-replace: {set(leftover)}")

    return qss


def apply_theme(app: QApplication, mode: ThemeMode | str = ThemeMode.DARK) -> None:
    """
    Terapkan tema ke QApplication.
    Juga set palette global supaya popup widgets ikut dark.
    """
    global _current_mode
    if isinstance(mode, str):
        mode = ThemeMode(mode.lower())
    _current_mode = mode

    # Set stylesheet
    app.setStyleSheet(get_stylesheet(mode))

    # ⚠️ Set GLOBAL PALETTE — ini yang bikin popup widget ikut dark
    if mode == ThemeMode.DARK:
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#0b0f19"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#f8fafc"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#1e293b"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#0f172a"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#f8fafc"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#1f2937"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#f8fafc"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#0d6efd"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#1e293b"))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#f8fafc"))
        app.setPalette(palette)

def get_current_mode() -> ThemeMode:
    """Return mode tema saat ini."""
    return _current_mode


# ============================================================
# HELPERS UNTUK STATUS
# ============================================================
def status_color(status: str, mode: Optional[ThemeMode] = None) -> str:
    """
    Return hex color berdasarkan string status.
    Mendukung emoji: 🟢 🟡 🔴
    """
    palette = get_palette(mode)
    s = (status or "").upper()
    if "BAHAYA" in s or "DANGER" in s or "🔴" in (status or ""):
        return palette["status_bahaya"]
    if "SIAGA" in s or "WARNING" in s or "🟡" in (status or ""):
        return palette["status_siaga"]
    return palette["status_aman"]


def status_badge_style(status: str, mode: Optional[ThemeMode] = None) -> str:
    """
    Return QSS inline untuk QLabel status badge.
    Cocok dipasang via widget.setStyleSheet(...).
    """
    palette = get_palette(mode)
    color = status_color(status, mode)
    bg = hex_to_rgba(color, 0.15)
    return f"""
        background-color: {bg};
        color: {color};
        border: 1px solid {color};
        border-radius: 6px;
        padding: 6px 14px;
        font-weight: 700;
        font-size: 13px;
    """


def kpi_card_qss(accent: Optional[str] = None, mode: Optional[ThemeMode] = None) -> str:
    """
    Return QSS untuk KPI card (QFrame).
    accent = warna border (opsional). Kalau None, pakai border default.
    """
    palette = get_palette(mode)
    border = accent or palette["border"]
    return f"""
        QFrame {{
            background-color: {palette['bg_card']};
            border: 1px solid {border};
            border-radius: 12px;
        }}
    """

# ============================================================
# COMBOBOX DARK THEME ENFORCER
# ============================================================
def style_combo(combo: QComboBox) -> None:
    """
    Force dark theme untuk QComboBox termasuk popup view-nya.
    
    Wajib dipanggil untuk setiap QComboBox di aplikasi
    karena popup di-render di window terpisah yang
    kadang mengabaikan QSS global di Windows.
    """
    # ─── 1. Palette untuk MAIN widget ────────────────
    p = combo.palette()
    p.setColor(QPalette.ColorRole.Base, QColor("#1f2937"))
    p.setColor(QPalette.ColorRole.Text, QColor("#f8fafc"))
    p.setColor(QPalette.ColorRole.Button, QColor("#1f2937"))
    p.setColor(QPalette.ColorRole.ButtonText, QColor("#f8fafc"))
    p.setColor(QPalette.ColorRole.Window, QColor("#1f2937"))
    p.setColor(QPalette.ColorRole.WindowText, QColor("#f8fafc"))
    p.setColor(QPalette.ColorRole.Highlight, QColor("#0d6efd"))
    p.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    combo.setPalette(p)

    # ─── 2. Palette untuk POPUP VIEW ─────────────────
    view = combo.view()
    pv = view.palette()
    pv.setColor(QPalette.ColorRole.Base, QColor("#1e293b"))
    pv.setColor(QPalette.ColorRole.AlternateBase, QColor("#0f172a"))
    pv.setColor(QPalette.ColorRole.Text, QColor("#f8fafc"))
    pv.setColor(QPalette.ColorRole.WindowText, QColor("#f8fafc"))
    pv.setColor(QPalette.ColorRole.Window, QColor("#1e293b"))
    pv.setColor(QPalette.ColorRole.Highlight, QColor("#0d6efd"))
    pv.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    view.setPalette(pv)

    # ─── 3. QSS untuk MAIN widget ────────────────────
    combo.setStyleSheet("""
        QComboBox {
            background-color: #1f2937;
            color: #f8fafc;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 8px 12px;
            padding-right: 32px;
            min-height: 22px;
            min-width: 150px;
            font-size: 13px;
        }
        QComboBox:hover { border: 1px solid #0d6efd; background-color: #2c3034; }
        QComboBox:focus { border: 1px solid #10b981; }
        QComboBox:disabled { background-color: #111827; color: #64748b; }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: center right;
            border: none;
            width: 28px;
            background: transparent;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid #94a3b8;
            width: 0;
            height: 0;
            margin-right: 10px;
        }
    """)

    # ─── 4. QSS KHUSUS untuk VIEW (popup) ────────────
    # Ini KUNCI UTAMA — style view secara langsung
    view.setStyleSheet("""
        QListView {
            background-color: #1e293b;
            color: #f8fafc;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 4px;
            outline: 0;
            font-size: 13px;
        }
        QListView::item {
            min-height: 28px;
            padding: 6px 12px;
            color: #f8fafc;
            background-color: transparent;
            border-radius: 4px;
        }
        QListView::item:hover {
            background-color: #334155;
            color: #ffffff;
        }
        QListView::item:selected {
            background-color: #0d6efd;
            color: #ffffff;
            font-weight: 600;
        }
    """)


def style_all_combos(root_widget) -> None:
    """Cari semua QComboBox dalam widget tree dan style semuanya."""
    for combo in root_widget.findChildren(QComboBox):
        style_combo(combo)


# ============================================================
# AURORA BACKGROUND WIDGET
# ============================================================
class AuroraBackground(QWidget):
    """
    Widget yang menampilkan efek radial gradient 'aurora'.

    Cara pakai:
        aurora = AuroraBackground(parent)
        aurora.setGeometry(parent.rect())
        aurora.lower()  # taruh di belakang

    Atau jadikan base class layout:
        class MyWindow(AuroraBackground):
            def __init__(self):
                super().__init__()
                layout = QVBoxLayout(self)
                ...
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        palette = get_palette()
        w, h = self.width(), self.height()

        # Aurora 1 — Emerald (kiri atas)
        grad1 = QRadialGradient(QPointF(w * 0.15, h * 0.20), w * 0.55)
        grad1.setColorAt(0.0, QColor(palette["aurora_1"]))
        grad1.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), grad1)

        # Aurora 2 — Blue (kanan bawah)
        grad2 = QRadialGradient(QPointF(w * 0.85, h * 0.80), w * 0.55)
        grad2.setColorAt(0.0, QColor(palette["aurora_2"]))
        grad2.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), grad2)

        # Aurora 3 — Violet (tengah kanan atas)
        grad3 = QRadialGradient(QPointF(w * 0.75, h * 0.25), w * 0.40)
        grad3.setColorAt(0.0, QColor(palette["aurora_3"]))
        grad3.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.fillRect(self.rect(), grad3)

        # Background base (paling bawah)
        painter.fillRect(self.rect(), QColor(palette["bg_primary"]))

        # Ulang aurora supaya tampil di atas base
        painter.fillRect(self.rect(), grad1)
        painter.fillRect(self.rect(), grad2)
        painter.fillRect(self.rect(), grad3)