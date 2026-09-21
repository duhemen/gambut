# server/core/regions.py
"""
Helper untuk manajemen data region hierarkis.

Struktur:
    Region → Provinsi → Kabupaten → Kecamatan → Kelurahan/Desa

Level 1-3 : offline (dari regions.json)
Level 4-5 : lazy-load dari emsifa API (cached)
"""
import json
import re
import requests
from pathlib import Path
from typing import Optional

# ══════════════════════════════════════════════════════════════
# PATHS & CONSTANTS
# ══════════════════════════════════════════════════════════════
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

REGIONS_PATH = DATA_DIR / "regions.json"
DISTRICTS_CACHE_PATH = DATA_DIR / "districts_cache.json"
VILLAGES_CACHE_PATH = DATA_DIR / "villages_cache.json"
REGENCIES_INDEX_PATH = DATA_DIR / "regencies_index.json"

REGIONS_PATH = DATA_DIR / "regions.json"
DISTRICTS_CACHE_PATH = DATA_DIR / "districts_cache.json"
VILLAGES_CACHE_PATH = DATA_DIR / "villages_cache.json"
REGENCIES_INDEX_PATH = DATA_DIR / "regencies_index.json"

# ⬇️ TAMBAHKAN INI
WILAYAH_DB_PATH = DATA_DIR / "wilayah.db"

EMSIFA_BASE = "https://www.emsifa.com/api-wilayah-indonesia/api"

EMSIFA_BASE = "https://www.emsifa.com/api-wilayah-indonesia/api"

_cache = None  # cache untuk regions.json


# ══════════════════════════════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════════════════════════════
def slugify(text: str) -> str:
    """Slugify string untuk key matching."""
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r"[()]", "", text)
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def _load_json_cache(path: Path) -> dict:
    """Load JSON file, return {} kalau error."""
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_json_cache(path: Path, data: dict):
    """Save JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ══════════════════════════════════════════════════════════════
# LEVEL 1-3: OFFLINE (dari regions.json)
# ══════════════════════════════════════════════════════════════
def _load_regions() -> dict:
    """Load regions.json dengan cache."""
    global _cache
    if _cache is None:
        if not REGIONS_PATH.exists():
            _cache = {"regions": {}}
        else:
            try:
                with open(REGIONS_PATH, "r", encoding="utf-8") as f:
                    _cache = json.load(f)
            except Exception as e:
                print(f"⚠️ [REGIONS] Gagal load regions.json: {e}")
                _cache = {"regions": {}}
    return _cache


def reload():
    """Force reload dari disk."""
    global _cache
    _cache = None
    return _load_regions()


def get_all_regions() -> dict:
    """Return full structure."""
    return _load_regions().get("regions", {})


def get_region_list() -> list:
    """List region level 1, dengan priority flag."""
    regions = get_all_regions()
    return [
        {
            "key": k,
            "name": v["name"],
            "icon": v.get("icon", "📍"),
            "priority": v.get("priority", False),
            "n_provinces": len(v.get("provinces", {})),
        }
        for k, v in regions.items()
    ]


def get_provinces(region_key: str) -> list:
    """List provinsi dalam region."""
    regions = get_all_regions()
    if region_key not in regions:
        return []
    provinces = regions[region_key].get("provinces", {})
    return [
        {
            "key": k,
            "name": v["name"],
            "n_regencies": v.get("n_regencies", len(v.get("regencies", []))),
        }
        for k, v in provinces.items()
    ]


def get_regencies(region_key: str, province_key: str) -> list:
    """List kabupaten/kota dalam provinsi."""
    regions = get_all_regions()
    if region_key not in regions:
        return []
    provinces = regions[region_key].get("provinces", {})
    if province_key not in provinces:
        return []
    return provinces[province_key].get("regencies", [])


def get_full_path(region_key: str, province_key: str = None,
                  regency: str = None) -> dict:
    """Return info lengkap path."""
    regions = get_all_regions()
    result = {"region": None, "province": None, "regency": regency}

    if region_key in regions:
        r = regions[region_key]
        result["region"] = {
            "key": region_key,
            "name": r["name"],
            "icon": r.get("icon"),
        }

        if province_key and province_key in r.get("provinces", {}):
            p = r["provinces"][province_key]
            result["province"] = {
                "key": province_key,
                "name": p["name"],
            }
    return result


def validate_selection(region: str, province: str = None,
                       regency: str = None) -> tuple:
    """Validasi pilihan user."""
    regions = get_all_regions()

    if region not in regions:
        return False, f"Region '{region}' tidak valid"

    if province:
        provinces = regions[region].get("provinces", {})
        if province not in provinces:
            return False, f"Provinsi '{province}' tidak ada di {region}"

        if regency:
            regencies = provinces[province].get("regencies", [])
            if regency not in regencies:
                return False, f"Kabupaten '{regency}' tidak ada di {province}"

    return True, "OK"


def get_stats() -> dict:
    """Statistik region."""
    regions = get_all_regions()
    total_prov = sum(len(r.get("provinces", {})) for r in regions.values())
    total_reg = sum(
        len(p.get("regencies", []))
        for r in regions.values()
        for p in r.get("provinces", {}).values()
    )
    return {
        "n_regions": len(regions),
        "n_provinces": total_prov,
        "n_regencies": total_reg,
        "priority_regions": [
            k for k, v in regions.items() if v.get("priority")
        ],
    }


# ══════════════════════════════════════════════════════════════
# LEVEL 4-5: LAZY LOAD (dari emsifa API)
# ══════════════════════════════════════════════════════════════
def _build_regencies_index() -> dict:
    """
    Build index {province_slug::regency_slug: info} untuk lookup ke BPS code.
    Dilakukan sekali, hasil di-cache.
    """
    cached = _load_json_cache(REGENCIES_INDEX_PATH)
    if cached:
        return cached

    print("[REGIONS] Building regencies index dari emsifa...")
    index = {}
    try:
        provinces = requests.get(f"{EMSIFA_BASE}/provinces.json", timeout=15).json()
        for prov in provinces:
            prov_id = prov["id"]
            prov_name = prov["name"]
            try:
                regs = requests.get(
                    f"{EMSIFA_BASE}/regencies/{prov_id}.json", timeout=15
                ).json()
                for reg in regs:
                    key = f"{slugify(prov_name)}::{slugify(reg['name'])}"
                    index[key] = {
                        "id": reg["id"],
                        "name": reg["name"],
                        "province_id": prov_id,
                        "province_name": prov_name,
                    }
            except Exception as e:
                print(f"[REGIONS] Skip provinsi {prov_name}: {e}")
    except Exception as e:
        print(f"[REGIONS] Error building index: {e}")
        return {}

    _save_json_cache(REGENCIES_INDEX_PATH, index)
    print(f"[REGIONS] Index built: {len(index)} kabupaten")
    return index


def get_districts(region_key: str, province_key: str, regency: str) -> list:
    """
    Ambil kecamatan dari emsifa API (cached).

    Args:
        region_key  : 'kalimantan'
        province_key: 'kalimantan_tengah'
        regency     : 'Kota Palangka Raya'
    """
    # Cari BPS code regency dari index
    index = _build_regencies_index()

    # Cari nama provinsi dari regions.json
    regions = get_all_regions()
    province_name = ""
    if region_key in regions:
        provinces = regions[region_key].get("provinces", {})
        if province_key in provinces:
            province_name = provinces[province_key]["name"]

    # Buat key lookup
    lookup_key = f"{slugify(province_name)}::{slugify(regency)}"
    reg_info = index.get(lookup_key)

    if not reg_info:
        print(f"⚠️ [REGIONS] Regency '{regency}' tidak ditemukan di index")
        return []

    reg_code = reg_info["id"]
    cache_key = f"{region_key}/{province_key}/{slugify(regency)}"

    # Cek cache dulu
    cache = _load_json_cache(DISTRICTS_CACHE_PATH)
    if cache_key in cache:
        return cache[cache_key]

    # Fetch dari API
    try:
        print(f"[REGIONS] Fetching districts untuk {regency}...")
        resp = requests.get(
            f"{EMSIFA_BASE}/districts/{reg_code}.json", timeout=15
        )
        if resp.status_code != 200:
            return []

        districts = [
            {"id": d["id"], "name": d["name"]}
            for d in resp.json()
        ]

        cache[cache_key] = districts
        _save_json_cache(DISTRICTS_CACHE_PATH, cache)
        return districts
    except Exception as e:
        print(f"⚠️ [REGIONS] Error fetch districts: {e}")
        return []


def get_villages(region_key: str, province_key: str,
                 regency: str, district_id: str) -> list:
    """
    Ambil kelurahan/desa dari emsifa API (cached).

    Args:
        region_key  : 'kalimantan'
        province_key: 'kalimantan_tengah'
        regency     : 'Kota Palangka Raya'
        district_id : '6271010' (BPS code) atau nama district
    """
    # Cari district ID kalau yang dikirim nama
    if not str(district_id).isdigit():
        cache_key_dist = f"{region_key}/{province_key}/{slugify(regency)}"
        dist_cache = _load_json_cache(DISTRICTS_CACHE_PATH)
        districts = dist_cache.get(cache_key_dist, [])

        found_id = None
        for d in districts:
            if d["name"] == district_id:
                found_id = d["id"]
                break

        if found_id:
            district_id = found_id
        else:
            print(f"⚠️ [REGIONS] District '{district_id}' tidak ditemukan")
            return []

    # Cache key
    village_cache_key = f"dist_{district_id}"

    # Cek cache
    cache = _load_json_cache(VILLAGES_CACHE_PATH)
    if village_cache_key in cache:
        return cache[village_cache_key]

    # Fetch dari API
    try:
        print(f"[REGIONS] Fetching villages untuk district {district_id}...")
        resp = requests.get(
            f"{EMSIFA_BASE}/villages/{district_id}.json", timeout=15
        )
        if resp.status_code != 200:
            return []

        villages = [
            {"id": v["id"], "name": v["name"]}
            for v in resp.json()
        ]

        cache[village_cache_key] = villages
        _save_json_cache(VILLAGES_CACHE_PATH, cache)
        return villages
    except Exception as e:
        print(f"⚠️ [REGIONS] Error fetch villages: {e}")
        return []

# ══════════════════════════════════════════════════════════════
# SQLITE-BASED WILAYAH DATABASE (dari cahyadsn/wilayah)
# Data resmi: Kepmendagri No 300.2.2-2430 Tahun 2025
# Credit: https://github.com/cahyadsn/wilayah
# ══════════════════════════════════════════════════════════════
import sqlite3
from contextlib import contextmanager



_wilayah_cache = {}  # Cache query results


@contextmanager
def _wilayah_conn():
    """SQLite connection (read-only)."""
    if not WILAYAH_DB_PATH.exists():
        raise FileNotFoundError(
            f"Wilayah database belum ada: {WILAYAH_DB_PATH}\n"
            "Jalankan: python scripts/download_wilayah.py && "
            "python scripts/build_wilayah_db.py"
        )
    conn = sqlite3.connect(str(WILAYAH_DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def wilayah_available() -> bool:
    """Cek apakah wilayah.db sudah ada."""
    return WILAYAH_DB_PATH.exists()


def get_provinces_from_db() -> list:
    """Ambil semua provinsi dari SQLite."""
    if "provinces" in _wilayah_cache:
        return _wilayah_cache["provinces"]

    try:
        with _wilayah_conn() as conn:
            cur = conn.execute(
                "SELECT kode, nama FROM wilayah WHERE level = 1 ORDER BY kode"
            )
            data = [
                {"kode": row["kode"], "name": _title_case(row["nama"])}
                for row in cur.fetchall()
            ]
        _wilayah_cache["provinces"] = data
        return data
    except FileNotFoundError:
        return []


def get_regencies_from_db(province_kode: str) -> list:
    """Ambil kabupaten/kota dalam provinsi."""
    cache_key = f"regencies_{province_kode}"
    if cache_key in _wilayah_cache:
        return _wilayah_cache[cache_key]

    try:
        with _wilayah_conn() as conn:
            cur = conn.execute(
                "SELECT kode, nama FROM wilayah "
                "WHERE level = 2 AND parent_kode = ? "
                "ORDER BY kode",
                (province_kode,),
            )
            data = [
                {"kode": row["kode"], "name": _title_case(row["nama"])}
                for row in cur.fetchall()
            ]
        _wilayah_cache[cache_key] = data
        return data
    except FileNotFoundError:
        return []


def get_districts_from_db(regency_kode: str) -> list:
    """Ambil kecamatan dalam kabupaten."""
    cache_key = f"districts_{regency_kode}"
    if cache_key in _wilayah_cache:
        return _wilayah_cache[cache_key]

    try:
        with _wilayah_conn() as conn:
            cur = conn.execute(
                "SELECT kode, nama FROM wilayah "
                "WHERE level = 3 AND parent_kode = ? "
                "ORDER BY kode",
                (regency_kode,),
            )
            data = [
                {"kode": row["kode"], "name": _title_case(row["nama"])}
                for row in cur.fetchall()
            ]
        _wilayah_cache[cache_key] = data
        return data
    except FileNotFoundError:
        return []


def get_villages_from_db(district_kode: str) -> list:
    """Ambil kelurahan/desa dalam kecamatan."""
    cache_key = f"villages_{district_kode}"
    if cache_key in _wilayah_cache:
        return _wilayah_cache[cache_key]

    try:
        with _wilayah_conn() as conn:
            cur = conn.execute(
                "SELECT kode, nama FROM wilayah "
                "WHERE level = 4 AND parent_kode = ? "
                "ORDER BY kode",
                (district_kode,),
            )
            data = [
                {"kode": row["kode"], "name": _title_case(row["nama"])}
                for row in cur.fetchall()
            ]
        _wilayah_cache[cache_key] = data
        return data
    except FileNotFoundError:
        return []


def find_kode_by_name(name: str, level: int = None,
                      parent_kode: str = None) -> Optional[str]:
    """Cari kode dari nama (fuzzy match)."""
    try:
        with _wilayah_conn() as conn:
            query = "SELECT kode, nama FROM wilayah WHERE UPPER(nama) = UPPER(?)"
            params = [name]

            if level:
                query += " AND level = ?"
                params.append(level)
            if parent_kode:
                query += " AND parent_kode = ?"
                params.append(parent_kode)

            cur = conn.execute(query, params)
            row = cur.fetchone()
            return row["kode"] if row else None
    except FileNotFoundError:
        return None


def _title_case(text: str) -> str:
    """Convert 'KABUPATEN ACEH SELATAN' → 'Kabupaten Aceh Selatan'."""
    if not text:
        return ""

    text = text.strip()

    # Handle roman numerals (tetap uppercase)
    def upper_roman(match):
        return match.group(0).upper()

    titled = " ".join(word.capitalize() for word in text.split())
    titled = re.sub(
        r"\b(I{1,3}|IV|V|VI{1,3}|IX|X)\b",
        upper_roman,
        titled,
        flags=re.IGNORECASE,
    )
    return titled

# ============================================================
# NAME → KODE LOOKUP (untuk integrasi client)
# ============================================================
def find_province_kode(name: str) -> Optional[str]:
    """Cari kode provinsi by name dari wilayah.db."""
    try:
        with _wilayah_conn() as conn:
            cur = conn.execute(
                "SELECT kode FROM wilayah WHERE level = 1 AND UPPER(nama) = UPPER(?)",
                (name,),
            )
            row = cur.fetchone()
            return row["kode"] if row else None
    except FileNotFoundError:
        return None


def find_regency_kode(province_kode: str, name: str) -> Optional[str]:
    """Cari kode kabupaten by name dari wilayah.db."""
    try:
        with _wilayah_conn() as conn:
            cur = conn.execute(
                "SELECT kode FROM wilayah WHERE level = 2 AND parent_kode = ? AND UPPER(nama) = UPPER(?)",
                (province_kode, name),
            )
            row = cur.fetchone()
            return row["kode"] if row else None
    except FileNotFoundError:
        return None

def find_district_kode(regency_kode: str, name: str) -> Optional[str]:
    """Cari kode kecamatan by name dari wilayah.db."""
    try:
        with _wilayah_conn() as conn:
            cur = conn.execute(
                "SELECT kode FROM wilayah WHERE level = 3 AND parent_kode = ? AND UPPER(nama) = UPPER(?)",
                (regency_kode, name),
            )
            row = cur.fetchone()
            return row["kode"] if row else None
    except FileNotFoundError:
        return None

def find_village_kode(district_kode: str, name: str) -> Optional[str]:
    """Cari kode kelurahan/desa by name dari wilayah.db."""
    try:
        with _wilayah_conn() as conn:
            cur = conn.execute(
                "SELECT kode FROM wilayah WHERE level = 4 AND parent_kode = ? AND UPPER(nama) = UPPER(?)",
                (district_kode, name),
            )
            row = cur.fetchone()
            return row["kode"] if row else None
    except FileNotFoundError:
        return None