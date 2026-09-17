# server/core/forecasting.py
"""Model peramalan ARIMA / LSTM / GRU"""
import os
import numpy as np
import pandas as pd

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

try:
    from pmdarima import auto_arima
    from statsmodels.tsa.arima.model import ARIMA
    ARIMA_AVAILABLE = True
except ImportError:
    ARIMA_AVAILABLE = False


def run_arima_forecast(history_series: pd.Series, steps: int = 7) -> np.ndarray:
    """Auto-ARIMA forecast"""
    try:
        series = history_series.astype(float).dropna()
        if len(series) < 5 or not ARIMA_AVAILABLE:
            last_val = series.iloc[-1] if len(series) > 0 else 0.0
            return np.array([last_val] * steps)

        auto_model = auto_arima(series, seasonal=False,
                                error_action='ignore', suppress_warnings=True)
        order = auto_model.order
        model = ARIMA(series, order=order)
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=steps)
        return np.array(forecast)
    except Exception as e:
        print(f"[ERROR ARIMA]: {e}")
        last_val = history_series.dropna().iloc[-1] if len(history_series.dropna()) > 0 else 0.0
        return np.array([last_val] * steps)


def run_lstm_forecast(history_series: pd.Series, steps: int = 7) -> np.ndarray:
    """Simulasi LSTM (stochastic)"""
    try:
        series = history_series.astype(float).dropna().values
        if len(series) == 0:
            return np.array([0.0] * steps)
        last_val = series[-1]
        trend = 0
        if len(series) > 3:
            trend = series[-1] - series[-3]
        forecast = []
        current_val = last_val
        rng = np.random.default_rng(seed=42)
        for _ in range(steps):
            noise = rng.normal(0, 0.2)
            current_val = current_val + (trend * 0.1) + noise
            forecast.append(current_val)
        return np.array(forecast)
    except Exception:
        return np.array([history_series.iloc[-1]] * steps)