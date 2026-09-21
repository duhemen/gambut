"""Parse wilayah.sql → SQLite database."""
import re
import sqlite3
from pathlib import Path

SQL_PATH = Path("scripts/wilayah_raw.sql")
DB_PATH = Path("server/data/wilayah.db")

# Pattern untuk extract ('kode', 'nama')
# Handle 2 format: single insert & batch insert
ROW_PATTERN = re.compile(
    r"\(\s*'([0-9.]+)'\s*,\s*'((?:[^'\\]|\\.)*)'\s*\)"
)


def unescape(s: str) -> str:
    """Unescape SQL string."""
    return s.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")


def detect_level(kode: str) -> int:
    """Detect level dari format kode."""
    parts = kode.split(".")
    return len(parts)  # 1=prov, 2=kab, 3=kec, 4=kel/desa


def get_parent(kode: str) -> str:
    """Parent code = kode tanpa segment terakhir."""
    parts = kode.split(".")
    if len(parts) <= 1:
        return ""
    return ".".join(parts[:-1])


def parse_sql(sql_path: Path) -> list:
    """Parse SQL, return list of (kode, nama, level, parent)."""
    print(f"Parsing {sql_path}...")

    with open(sql_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Cari bagian INSERT INTO `wilayah`
    # Ambil semua setelah "INSERT INTO `wilayah`"
    # Sampai tanda ";" terakhir
    inserts = re.findall(
        r"INSERT\s+INTO\s+`?wilayah`?\s+(?:\([^)]+\)\s+)?VALUES\s+(.+?);",
        content,
        re.DOTALL | re.IGNORECASE,
    )

    if not inserts:
        print("ERROR: Tidak ada INSERT statement ditemukan!")
        return []

    print(f"Found {len(inserts)} INSERT blocks")

    rows = []
    seen = set()

    for block in inserts:
        for match in ROW_PATTERN.finditer(block):
            kode = match.group(1).strip()
            nama = unescape(match.group(2).strip())

            if kode in seen:
                continue
            seen.add(kode)

            level = detect_level(kode)
            parent = get_parent(kode)
            rows.append((kode, nama, level, parent))

    print(f"Parsed {len(rows)} unique rows")
    return rows


def build_sqlite(rows: list, db_path: Path):
    """Build SQLite database."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    # Create schema
    cur.execute("""
        CREATE TABLE wilayah (
            kode TEXT PRIMARY KEY,
            nama TEXT NOT NULL,
            level INTEGER NOT NULL,
            parent_kode TEXT
        )
    """)

    # Indexes
    cur.execute("CREATE INDEX idx_level ON wilayah(level)")
    cur.execute("CREATE INDEX idx_parent ON wilayah(parent_kode)")

    # Batch insert
    cur.executemany(
        "INSERT INTO wilayah (kode, nama, level, parent_kode) VALUES (?, ?, ?, ?)",
        rows,
    )

    conn.commit()

    # Stats
    cur.execute("SELECT level, COUNT(*) FROM wilayah GROUP BY level ORDER BY level")
    stats = cur.fetchall()

    conn.close()

    print(f"\nOK: Database built at {db_path}")
    print(f"   Size: {db_path.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"\n   Statistik:")
    level_names = {1: "Provinsi", 2: "Kabupaten/Kota", 3: "Kecamatan", 4: "Kelurahan/Desa"}
    for lvl, count in stats:
        name = level_names.get(lvl, f"Level {lvl}")
        print(f"     {name}: {count:,}")


def main():
    if not SQL_PATH.exists():
        print(f"ERROR: {SQL_PATH} tidak ada. Jalankan download_wilayah.py dulu.")
        return

    rows = parse_sql(SQL_PATH)
    if not rows:
        return

    build_sqlite(rows, DB_PATH)


if __name__ == "__main__":
    main()
