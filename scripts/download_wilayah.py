"""Download wilayah.sql dari cahyadsn/wilayah repo."""
import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/cahyadsn/wilayah/master/db/wilayah.sql"
OUT = Path("scripts/wilayah_raw.sql")

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading dari {URL}...")
    try:
        urllib.request.urlretrieve(URL, OUT)
        size_mb = OUT.stat().st_size / 1024 / 1024
        print(f"OK: {OUT} ({size_mb:.2f} MB)")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
