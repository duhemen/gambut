# server/models.py
"""Pydantic models untuk validasi request/response"""
from pydantic import BaseModel, Field
from typing import Optional


class PeatRow(BaseModel):
    tanggal: str
    wt: float
    sm: float
    rf: float
    temp: float


class ManualInput(BaseModel):
    wt: float
    sm: float
    rf: float
    temp: float


class SatelliteRow(BaseModel):
    tanggal: str
    wt: Optional[float] = None
    sm: Optional[float] = None
    rf: Optional[float] = None
    temp: Optional[float] = None


class SyncRequest(BaseModel):
    method: str = Field(default="KNN Imputer",
                        description="KNN Imputer | Spline Curve | Linear Method")


class ForecastRequest(BaseModel):
    model: str = Field(default="ARIMA Stochastic",
                       description="ARIMA Stochastic | LSTM Deep Learning | GRU Deep Learning")
    steps: int = 7


class IndexRequest(BaseModel):
    wt: float
    sm: float
    rf: float
    temp: float


class ConfigData(BaseModel):
    api_url: str = ""
    api_key: str = ""


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[list] = None


# ============ AUTH SCHEMAS ============
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = ""
    role: str = Field(default="petugas")  # "admin" | "petugas"


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = ""
    role: str
    created_at: str


class TokenResponse(BaseModel):
    success: bool = True
    message: str = "Login berhasil"
    access_token: str
    token_type: str = "bearer"
    user: UserOut