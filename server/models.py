# server/models.py
"""Pydantic models untuk validasi request/response"""
from pydantic import BaseModel, Field
from typing import Optional, List


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