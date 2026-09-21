"""Migrate database_gambut.csv — tambah kolom province, regency, district, village."""
import pandas as pd
from pathlib import Path

DB_PATH = Path("server/data/database_gambut.csv")

def migrate():
    if not DB_PATH.exists():
        print("DB belum ada, skip.")
        return

    df = pd.read_csv(DB_PATH)
    print(f"Sebelum: {list(df.columns)}")

    # Tambahkan kolom baru kalau belum ada
    for col in ["province", "regency", "district", "village"]:
        if col not in df.columns:
            df.insert(df.columns.get_loc("region") + 1 + ["province", "regency", "district", "village"].index(col), col, "")
            print(f"  + Kolom '{col}' ditambahkan")

    df.to_csv(DB_PATH, index=False)
    print(f"Sesudah: {list(df.columns)}")
    print(f"Total: {len(df)} baris")

if __name__ == "__main__":
    migrate()
