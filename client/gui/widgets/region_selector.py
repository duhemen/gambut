# client/gui/widgets/region_selector.py
"""Widget cascading 5-level: Region → Provinsi → Kabupaten → Kecamatan → Kelurahan."""
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel
)
from client.api.client import get_client
from client.gui.theme import style_combo


class RegionSelector(QWidget):
    """
    Cascading 5-level dropdown.

    Signals:
        selection_changed(dict):
            {
                "region": "kalimantan",
                "province": "kalimantan_tengah",
                "regency": "Kota Palangka Raya",
                "district": "Pahandut",
                "village": "Panarung",
                "region_name": "Kalimantan",
                "province_name": "Kalimantan Tengah",
                "region_kode": "62",           # BPS code provinsi
                "regency_kode": "62.71",       # BPS code kabupaten
                "district_kode": "62.71.01",   # BPS code kecamatan
                "village_kode": "62.71.01.1002",  # BPS code kelurahan
                "full_path": "Kalimantan > Kalimantan Tengah > Kota Palangka Raya > Pahandut > Panarung",
            }
    """

    selection_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tree = {}  # regions.json tree
        self._build_ui()
        self._load_tree()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Helper buat row
        def make_row(label_text):
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setObjectName("MutedLabel")
            lbl.setFixedWidth(140)
            row.addWidget(lbl)
            combo = QComboBox()
            row.addWidget(combo, stretch=1)
            return row, combo

        # Level 1
        self.row_region, self.combo_region = make_row("Region / Pulau")
        self.combo_region.currentIndexChanged.connect(self._on_region_changed)
        layout.addLayout(self.row_region)

        # Level 2
        self.row_province, self.combo_province = make_row("Provinsi")
        self.combo_province.currentIndexChanged.connect(self._on_province_changed)
        layout.addLayout(self.row_province)

        # Level 3
        self.row_regency, self.combo_regency = make_row("Kabupaten / Kota")
        self.combo_regency.currentIndexChanged.connect(self._on_regency_changed)
        layout.addLayout(self.row_regency)

        # Level 4
        self.row_district, self.combo_district = make_row("Kecamatan")
        self.combo_district.currentIndexChanged.connect(self._on_district_changed)
        layout.addLayout(self.row_district)

        # Level 5
        self.row_village, self.combo_village = make_row("Kelurahan / Desa")
        self.combo_village.currentIndexChanged.connect(self._on_village_changed)
        layout.addLayout(self.row_village)

    def _load_tree(self):
        """Load regions.json tree (level 1-3)."""
        client = get_client()
        try:
            r = client.get("/api/v1/regions/tree")
            if r.status_code == 200:
                self._tree = r.json().get("data", {})
                self._populate_regions()
                self._style_all()
        except Exception as e:
            print(f"⚠️ [REGION-SELECTOR] {e}")

    def _style_all(self):
        for c in [self.combo_region, self.combo_province,
                  self.combo_regency, self.combo_district, self.combo_village]:
            style_combo(c)

    def _populate_regions(self):
        self.combo_region.blockSignals(True)
        self.combo_region.clear()
        for key, info in self._tree.items():
            icon = info.get("icon", "📍")
            name = info.get("name", key)
            priority = " ⭐" if info.get("priority") else ""
            self.combo_region.addItem(f"{icon} {name}{priority}", userData=key)
        self.combo_region.blockSignals(False)
        self._on_region_changed()

    # ============================================================
    # HANDLERS
    # ============================================================
    def _on_region_changed(self):
        region_key = self.combo_region.currentData()
        if not region_key or region_key not in self._tree:
            self.combo_province.clear()
            return

        provinces = self._tree[region_key].get("provinces", {})
        self.combo_province.blockSignals(True)
        self.combo_province.clear()
        for pkey, pinfo in provinces.items():
            self.combo_province.addItem(pinfo["name"], userData=pkey)
        self.combo_province.blockSignals(False)

        self._on_province_changed()

    def _on_province_changed(self):
        """Fetch kabupaten dari wilayah.db."""
        region_key = self.combo_region.currentData()
        province_key = self.combo_province.currentData()

        self.combo_regency.blockSignals(True)
        self.combo_regency.clear()
        self.combo_district.clear()
        self.combo_village.clear()
        self.combo_regency.blockSignals(False)

        if not region_key or not province_key:
            self._emit_selection()
            return

        # Ambil nama provinsi
        provinces = self._tree.get(region_key, {}).get("provinces", {})
        province_name = provinces.get(province_key, {}).get("name", "")

        # Lookup kode BPS provinsi
        kode = self._find_province_kode(province_name)

        if not kode:
            self.combo_regency.addItem("⚠️ Kode provinsi tidak ditemukan", userData=None)
            self._emit_selection()
            return

        # Fetch kabupaten dari wilayah.db
        regencies = self._fetch_regencies(kode)

        self.combo_regency.blockSignals(True)
        self.combo_regency.addItem("— Pilih Kabupaten/Kota —", userData=None)
        for r in regencies:
            self.combo_regency.addItem(r["name"], userData=r)
        self.combo_regency.blockSignals(False)

        self._emit_selection()

    def _on_regency_changed(self):
        """Fetch kecamatan."""
        region_key = self.combo_region.currentData()
        province_key = self.combo_province.currentData()
        regency_data = self.combo_regency.currentData()

        self.combo_district.blockSignals(True)
        self.combo_district.clear()
        self.combo_village.clear()
        self.combo_district.blockSignals(False)

        if not regency_data or not isinstance(regency_data, dict):
            self._emit_selection()
            return

        regency_kode = regency_data["kode"]

        districts = self._fetch_districts(regency_kode)

        self.combo_district.blockSignals(True)
        self.combo_district.addItem("— Pilih Kecamatan —", userData=None)
        for d in districts:
            self.combo_district.addItem(d["name"], userData=d)
        self.combo_district.blockSignals(False)

        self._emit_selection()

    def _on_district_changed(self):
        """Fetch kelurahan."""
        district_data = self.combo_district.currentData()

        self.combo_village.blockSignals(True)
        self.combo_village.clear()
        self.combo_village.blockSignals(False)

        if not district_data or not isinstance(district_data, dict):
            self._emit_selection()
            return

        district_kode = district_data["kode"]

        villages = self._fetch_villages(district_kode)

        self.combo_village.blockSignals(True)
        self.combo_village.addItem("— Pilih Kelurahan/Desa —", userData=None)
        for v in villages:
            self.combo_village.addItem(v["name"], userData=v)
        self.combo_village.blockSignals(False)

        self._emit_selection()

    def _on_village_changed(self):
        self._emit_selection()

    # ============================================================
    # API HELPERS
    # ============================================================
    def _find_province_kode(self, province_name: str) -> str:
        """Lookup kode BPS provinsi."""
        client = get_client()
        try:
            r = client.get("/api/v1/wilayah/provinces")
            if r.status_code == 200:
                for p in r.json().get("data", []):
                    if p["name"].lower() == province_name.lower():
                        return p["kode"]
        except Exception:
            pass
        return ""

    def _fetch_regencies(self, province_kode: str) -> list:
        client = get_client()
        try:
            r = client.get(f"/api/v1/wilayah/{province_kode}/regencies")
            if r.status_code == 200:
                return r.json().get("data", [])
        except Exception:
            pass
        return []

    def _fetch_districts(self, regency_kode: str) -> list:
        client = get_client()
        try:
            province_kode = regency_kode.split(".")[0]
            r = client.get(f"/api/v1/wilayah/{province_kode}/{regency_kode}/districts")
            if r.status_code == 200:
                return r.json().get("data", [])
        except Exception:
            pass
        return []

    def _fetch_villages(self, district_kode: str) -> list:
        client = get_client()
        try:
            parts = district_kode.split(".")
            province_kode = parts[0]
            regency_kode = ".".join(parts[:2])
            r = client.get(f"/api/v1/wilayah/{province_kode}/{regency_kode}/{district_kode}/villages")
            if r.status_code == 200:
                return r.json().get("data", [])
        except Exception:
            pass
        return []

    # ============================================================
    # EMIT
    # ============================================================
    def _emit_selection(self):
        self.selection_changed.emit(self.get_selection())

    def get_selection(self) -> dict:
        region_key = self.combo_region.currentData() or ""
        province_key = self.combo_province.currentData() or ""

        regency_data = self.combo_regency.currentData()
        regency = regency_data["name"] if isinstance(regency_data, dict) else ""
        regency_kode = regency_data["kode"] if isinstance(regency_data, dict) else ""

        district_data = self.combo_district.currentData()
        district = district_data["name"] if isinstance(district_data, dict) else ""
        district_kode = district_data["kode"] if isinstance(district_data, dict) else ""

        village_data = self.combo_village.currentData()
        village = village_data["name"] if isinstance(village_data, dict) else ""
        village_kode = village_data["kode"] if isinstance(village_data, dict) else ""

        region_name = ""
        province_name = ""
        if region_key and region_key in self._tree:
            region_name = self._tree[region_key].get("name", "")
            if province_key:
                provinces = self._tree[region_key].get("provinces", {})
                if province_key in provinces:
                    province_name = provinces[province_key].get("name", "")

        path_parts = [p for p in [region_name, province_name, regency, district, village] if p]
        full_path = " > ".join(path_parts)

        return {
            "region": region_key,
            "province": province_key,
            "regency": regency,
            "district": district,
            "village": village,
            "region_name": region_name,
            "province_name": province_name,
            "region_kode": "",
            "regency_kode": regency_kode,
            "district_kode": district_kode,
            "village_kode": village_kode,
            "full_path": full_path,
        }