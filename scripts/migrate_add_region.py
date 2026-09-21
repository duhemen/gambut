"""Migrate database_gambut.csv untuk tambah kolom region."""
import pandas as pd
from pathlib import Path

DB_PATH = Path("server/data/database_gambut.csv")


def migrate():
    if not DB_PATH.exists():
        print("❌ Database tidak ditemukan:", DB_PATH)
        return

    df = pd.read_csv(DB_PATH)

    if 'region' in df.columns:
        print("✅ Kolom 'region' sudah ada. Skip migrate.")
        return

    # Backup dulu
    backup_path = DB_PATH.with_suffix('.csv.bak')
    df.to_csv(backup_path, index=False)
    print(f"💾 Backup: {backup_path}")

    # Tambahkan kolom region di posisi ke-2 (setelah tanggal)
    df.insert(1, 'region', 'indonesia')  # default untuk data lama

    df.to_csv(DB_PATH, index=False)
    print(f"✅ Migrasi selesai. {len(df)} baris ditambah kolom 'region'.")
    print(f"   Kolom baru: {list(df.columns)}")


if __name__ == "__main__":
    migrate()
