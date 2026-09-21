"""FastAPI dependencies: get_current_user & require_role."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from server.auth.jwt_handler import decode_access_token
from server import database

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """Extract & verify user dari header Authorization: Bearer <token>."""
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header Authorization tidak ditemukan.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(creds.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau kadaluarsa.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = database.get_user_by_username(payload.get("sub", ""))
    if not user:
        raise HTTPException(status_code=401, detail="User tidak ditemukan.")
    return user


def require_role(*roles: str):
    """Factory dependency: cek role user."""
    def _checker(user: dict = Depends(get_current_user)) -> dict:
        if user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Butuh role {roles}. Role kamu: {user['role']}",
            )
        return user
    return _checker