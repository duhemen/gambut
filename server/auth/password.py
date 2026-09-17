"""Hash & verify password pakai bcrypt via passlib."""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Ubah password plaintext → hash bcrypt."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Cek apakah password cocok dengan hash."""
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False