# install_backend.py
"""
Auto-detect & install Deep Learning backend.

Script ini mendeteksi apakah PyTorch/TensorFlow sudah terinstall,
dan menawarkan install PyTorch CPU-only kalau belum.

Usage:
    python install_backend.py           # interactive
    python install_backend.py --auto    # non-interactive (pilih PyTorch)
    python install_backend.py --check   # cek saja, tidak install
"""
import argparse
import importlib.util
import subprocess
import sys


PYTORCH_CMD = [
    sys.executable, "-m", "pip", "install",
    "torch", "--index-url", "https://download.pytorch.org/whl/cpu",
]

TF_CMD = [
    sys.executable, "-m", "pip", "install",
    "tensorflow-cpu",
]


def is_installed(module_name: str) -> bool:
    """Cek apakah package terinstall tanpa meng-import-nya."""
    return importlib.util.find_spec(module_name) is not None


def get_version(module_name: str) -> str:
    """Ambil versi package."""
    try:
        mod = importlib.import_module(module_name)
        return getattr(mod, "__version__", "unknown")
    except Exception:
        return "unknown"


def check_backends() -> dict:
    """Cek backend yang tersedia."""
    has_torch = is_installed("torch")
    has_tf = is_installed("tensorflow")

    return {
        "pytorch": {
            "installed": has_torch,
            "version": get_version("torch") if has_torch else None,
        },
        "tensorflow": {
            "installed": has_tf,
            "version": get_version("tensorflow") if has_tf else None,
        },
    }


def install_pytorch():
    """Install PyTorch CPU-only."""
    print("\n📦 Menginstall PyTorch CPU-only (~200 MB)...")
    print(f"   Command: {' '.join(PYTORCH_CMD)}\n")
    try:
        subprocess.check_call(PYTORCH_CMD)
        print("\n✅ PyTorch berhasil diinstall!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Gagal install PyTorch: {e}")
        return False


def install_tensorflow():
    """Install TensorFlow CPU."""
    print("\n📦 Menginstall TensorFlow CPU (~600 MB)...")
    print(f"   Command: {' '.join(TF_CMD)}\n")
    try:
        subprocess.check_call(TF_CMD)
        print("\n✅ TensorFlow berhasil diinstall!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Gagal install TensorFlow: {e}")
        return False


def print_status(info: dict):
    """Print status backend."""
    print("\n" + "=" * 60)
    print("  STATUS DEEP LEARNING BACKEND")
    print("=" * 60)

    pt = info["pytorch"]
    tf = info["tensorflow"]

    if pt["installed"]:
        print(f"  ✅ PyTorch    : {pt['version']}  (RECOMMENDED)")
    else:
        print(f"  ❌ PyTorch    : tidak terinstall")

    if tf["installed"]:
        print(f"  ✅ TensorFlow : {tf['version']}")
    else:
        print(f"  ❌ TensorFlow : tidak terinstall")

    if pt["installed"] or tf["installed"]:
        print(f"\n  🎉 Minimal satu backend tersedia — siap pakai!")
    else:
        print(f"\n  ⚠️  Tidak ada backend DL. Fitur LSTM/GRU akan pakai simulasi.")
    print("=" * 60 + "\n")


def interactive_mode():
    """Mode interaktif."""
    info = check_backends()
    print_status(info)

    if info["pytorch"]["installed"]:
        print("✨ PyTorch sudah terinstall. Tidak perlu install lagi.")
        print("   Kalau mau reinstall, jalankan: pip install --upgrade torch")
        return

    if info["tensorflow"]["installed"]:
        print("ℹ️  TensorFlow terdeteksi. PyTorch tidak wajib diinstall.")
        resp = input("   Install PyTorch juga? (y/N): ").strip().lower()
        if resp != "y":
            return

    print("\n🎯 Rekomendasi: PyTorch CPU-only")
    print("   - Ukuran: ~200 MB (vs TensorFlow ~600 MB)")
    print("   - Startup aplikasi: cepat")
    print("   - Stabil, minim konflik\n")

    resp = input("Install PyTorch sekarang? (Y/n): ").strip().lower()
    if resp in ("", "y", "yes"):
        install_pytorch()
        print_status(check_backends())
    else:
        print("⏭️  Skip install.")


def auto_mode():
    """Mode auto — langsung install PyTorch."""
    info = check_backends()
    print_status(info)

    if info["pytorch"]["installed"]:
        print("✅ PyTorch sudah terinstall.")
        return

    install_pytorch()
    print_status(check_backends())


def check_mode():
    """Mode check — hanya cek, tidak install."""
    info = check_backends()
    print_status(info)


def main():
    parser = argparse.ArgumentParser(description="Install DL backend untuk PeatFR")
    parser.add_argument("--auto", action="store_true",
                        help="Auto-install PyTorch tanpa tanya")
    parser.add_argument("--check", action="store_true",
                        help="Cek backend saja, tidak install")
    parser.add_argument("--tf", action="store_true",
                        help="Install TensorFlow (bukan PyTorch)")
    args = parser.parse_args()

    if args.check:
        check_mode()
    elif args.auto:
        auto_mode()
    elif args.tf:
        print_status(check_backends())
        install_tensorflow()
        print_status(check_backends())
    else:
        interactive_mode()


if __name__ == "__main__":
    main()