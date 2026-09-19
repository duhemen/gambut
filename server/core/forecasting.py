# server/core/forecasting.py
"""
Forecasting dispatcher — sekarang support LSTM/GRU asli + ensemble.
"""
import os
import warnings
import numpy as np
import pandas as pd

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

from server.core.deep_learning import run_lstm_real, run_gru_real, get_backend_info

try:
    from pmdarima import auto_arima
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller
    from scipy.stats import boxcox
    from scipy.special import inv_boxcox
    ARIMA_AVAILABLE = True
except ImportError as e:
    print(f"[FORECAST] ARIMA deps missing: {e}")
    ARIMA_AVAILABLE = False


# ============================================================
# BOX-COX HELPER
# ============================================================
def _prepare_boxcox(series: np.ndarray):
    min_val = float(np.min(series))
    shift = abs(min_val) + 1.0 if min_val <= 0 else 0.0
    return series + shift, shift


# ============================================================
# ARIMA + BOX-COX
# ============================================================
def run_arima_forecast(history_series: pd.Series, steps: int = 7) -> np.ndarray:
    try:
        series = history_series.astype(float).dropna().values

        if len(series) < 30:
            print(f"⚠️ [ARIMA] Hanya {len(series)} poin. Butuh ≥30 untuk optimal.")

        if len(series) < 5 or not ARIMA_AVAILABLE:
            last_val = series[-1] if len(series) > 0 else 0.0
            return np.array([last_val] * steps)

        shifted, shift = _prepare_boxcox(series)

        try:
            transformed, lam = boxcox(shifted)
            print(f"[ARIMA] Box-Cox λ={lam:.4f}, shift={shift:.2f}")
        except Exception:
            transformed, lam = shifted, None

        try:
            auto_model = auto_arima(
                transformed, seasonal=False,
                error_action='ignore', suppress_warnings=True,
                stepwise=True, max_p=3, max_q=3, max_d=2,
            )
            order = auto_model.order
            print(f"[ARIMA] Order: {order}")
        except Exception:
            order = (1, 1, 1)

        model = ARIMA(transformed, order=order)
        fit = model.fit()
        fc_trans = fit.forecast(steps=steps)

        if lam is not None:
            forecast = inv_boxcox(fc_trans, lam) - shift
        else:
            forecast = fc_trans - shift

        return np.array(forecast)

    except Exception as e:
        print(f"[ERROR ARIMA]: {e}")
        cleaned = history_series.dropna()
        last_val = cleaned.iloc[-1] if len(cleaned) > 0 else 0.0
        return np.array([last_val] * steps)


# ============================================================
# DISPATCHER
# ============================================================
def run_forecast(history_series: pd.Series, model: str = "ARIMA",
                 steps: int = 7) -> np.ndarray:
    """Dispatcher forecasting."""
    m = (model or "").upper()

    if "ENSEMBLE" in m:
        from server.core.ensemble import ensemble_forecast
        result = ensemble_forecast(history_series, steps=steps)
        return result["forecast"]
    elif "ARIMA" in m:
        return run_arima_forecast(history_series, steps)
    elif "GRU" in m:
        return run_gru_real(history_series, steps=steps)
    elif "LSTM" in m:
        return run_lstm_real(history_series, steps=steps)
    else:
        return run_arima_forecast(history_series, steps)


# ============================================================
# EVALUATION
# ============================================================
def evaluate_forecast(history_series: pd.Series,
                      model: str = "ARIMA",
                      test_ratio: float = 0.2) -> dict:
    """Evaluasi akurasi model."""
    series = history_series.astype(float).dropna()
    n = len(series)

    if n < 5:
        return {"error": "Data < 5 baris"}

    split = max(1, int(n * (1 - test_ratio)))
    train = series.iloc[:split]
    test = series.iloc[split:]

    if len(test) == 0:
        return {"error": "Test set kosong"}

    try:
        forecast = run_forecast(train, model=model, steps=len(test))
        actual = test.values
        mse = float(np.mean((actual - forecast[:len(actual)]) ** 2))
        rmse = float(np.sqrt(mse))
        mae = float(np.mean(np.abs(actual - forecast[:len(actual)])))

        return {
            "model": model,
            "n_train": len(train),
            "n_test": len(test),
            "MSE": round(mse, 4),
            "RMSE": round(rmse, 4),
            "MAE": round(mae, 4),
        }
    except Exception as e:
        return {"error": str(e)}