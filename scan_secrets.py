"""
scan_secrets.py - Cari hardcoded API keys & secrets di seluruh direktori.

Scan pattern:
- Telegram bot token
- NASA FIRMS API key
- PEATFR_SECRET_KEY
- Generic API keys (api_key, secret, token, password)
- JWT tokens
- Cloudflare tokens
"""
import os
import re
from pathlib import Path

# ─── Pattern yang dicari ──────────────────────────────
PATTERNS = {
    "Telegram Bot Token": re.compile(r"\b\d{9,10}:[A-Za-z0-9_-]{30,40}\b"),
    "NASA FIRMS Key": re.compile(r"\b[a-f0-9]{32}\b"),  # 32 char hex
    "AWS Key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Generic API Key": re.compile(r"""(?i)(api[_-]?key|apikey)\s*[:=]\s*["']([^"']{15,})["']"""),
    "Generic Secret": re.compile(r"""(?i)(secret|password|passwd|pwd)\s*[:=]\s*["']([^"']{8,})["']"""),
    "Bearer Token": re.compile(r"""Bearer\s+[A-Za-z0-9_\-\.]{20,}"""),
    "JWT Token": re.compile(r"\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\b"),
    "Cloudflare Token": re.compile(r"\b[A-Za-z0-9_-]{40}\b"),
    "Basic Auth": re.compile(r"(?i)basic\s+[A-Za-z0-9+/=]{20,}"),
}

# ─── File yang di-skip ─────────────────────────────────
SKIP_DIRS = {
    "__pycache__", ".git", ".venv", "venv", "env", ".env",
    "node_modules", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "build", "dist", ".idea", ".vscode",
}

SKIP_FILES = {
    ".env",  # Skip karena memang berisi secrets (akan di-handle terpisah)
    "scan_secrets.py",  # Skip self
}

# ─── Extensions yang discan ────────────────────────────
SCAN_EXTENSIONS = {
    ".py", ".html", ".js", ".json", ".yml", ".yaml", ".env",
    ".md", ".txt", ".ini", ".cfg", ".toml", ".sh", ".bat", ".ps1",
    ".csv",  # Cek juga CSV untuk metadata
    ".sql",
    ".example",  # File example (tapi cek kontennya)
}


def should_skip_dir(dirname):
    return dirname in SKIP_DIRS


def should_scan_file(filepath):
    name = filepath.name
    if name in SKIP_FILES:
        return False
    ext = filepath.suffix.lower()
    # File tanpa extension (config etc)
    if not ext and name not in {"Makefile", "Dockerfile", ".gitignore"}:
        return False
    return ext in SCAN_EXTENSIONS or name == ".gitignore"


def scan_file(filepath):
    """Scan single file. Return list of (line_num, match_type, matched_text)."""
    findings = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            lines = content.split("\n")
    except Exception:
        return findings

    for line_num, line in enumerate(lines, start=1):
        # Skip comment lines
        stripped = line.strip()
        if stripped.startswith("#") and "token" not in stripped.lower() and "key" not in stripped.lower():
            continue

        for pattern_name, regex in PATTERNS.items():
            for match in regex.finditer(line):
                matched_text = match.group(0)

                # Filter false positive
                if should_ignore_match(matched_text, str(filepath)):
                    continue

                findings.append({
                    "line": line_num,
                    "type": pattern_name,
                    "match": matched_text[:80],  # Truncate untuk display
                    "context": line.strip()[:100],
                })

    return findings


def should_ignore_match(text, filepath):
    """Filter false positive."""
    # Placeholder patterns
    placeholders = [
        "PASTE_YOUR", "REPLACE_WITH", "YOUR_", "EXAMPLE",
        "xxxxx", "XXXXX", "your_", "TODO", "FIXME",
        "abcdef1234567890", "dev-only",
        "admin123",  # Default password (OK untuk demo)
        "test_", "_test",
    ]
    for ph in placeholders:
        if ph.lower() in text.lower():
            return True

    # Skip UUIDs (kemungkinan bukan secret)
    uuid_pattern = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
    if uuid_pattern.match(text):
        return True

    # Skip if only md5/sha hashes
    if len(text) in (32, 40, 64) and re.match(r"^[a-f0-9]+$", text):
        # Hex string bisa jadi hash atau API key
        # Kalau di file .py dan tidak ada kata "key"/"token"/"secret" di context → skip
        return False  # Tapi tetap laporkan (false positive OK)

    # Skip common words
    if text.lower() in {"none", "null", "false", "true", "test"}:
        return True

    return False


def main():
    root = Path(".")
    total_files_scanned = 0
    total_findings = 0
    results = {}

    print("=" * 80)
    print("SCAN FOR HARDCODED SECRETS")
    print("=" * 80)
    print(f"Root: {root.resolve()}")
    print()

    for dirpath, dirnames, filenames in os.walk(root):
        # Skip dirs
        dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]

        for filename in filenames:
            filepath = Path(dirpath) / filename

            if not should_scan_file(filepath):
                continue

            total_files_scanned += 1
            findings = scan_file(filepath)

            if findings:
                rel_path = filepath.relative_to(root)
                results[str(rel_path)] = findings
                total_findings += len(findings)

    # ─── Print Results ─────────────────────────────────
    print(f"Total files scanned: {total_files_scanned}")
    print(f"Total findings: {total_findings}")
    print()

    if not results:
        print("[OK] TIDAK ADA hardcoded secrets ditemukan!")
        print("     Repo Anda AMAN untuk di-upload.")
        return

    print("=" * 80)
    print("DETAIL FINDINGS")
    print("=" * 80)

    for filepath, findings in sorted(results.items()):
        print(f"\n[FILE] {filepath}")
        print("-" * 60)
        for f in findings:
            print(f"  Line {f['line']:4d} | {f['type']:20s}")
            print(f"           Match   : {f['match']}")
            print(f"           Context : {f['context']}")
            print()

    print("=" * 80)
    print("REKOMENDASI")
    print("=" * 80)
    print("""
1. Cek setiap finding di atas secara manual
2. Kalau memang secret asli:
   - Hapus dari kode, ganti dengan os.getenv("NAMA_VAR")
   - Pindahkan nilai ke file .env
   - Pastikan .env sudah di .gitignore
   - REVOKE token lama (jika sudah pernah ter-expose)
3. Kalau false positive:
   - Tambahkan ke filter di scan_secrets.py
4. Jalankan scan ulang: python scan_secrets.py
""")


if __name__ == "__main__":
    main()
