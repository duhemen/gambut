# server/core/ensemble.py
"""
Ensemble Forecasting + Confidence Interval.

Fitur UNGGULAN yang tidak ada di peatfr:
- Ensemble multi-model (ARIMA + LSTM + GRU)
- Weighted average berdasarkan akurasi validasi
- Bootstrap confidence interval 95%
"""
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

from server.core.forecasting import run_arima_forecast
from server.core.deep_learning import run_lstm_real, run_gru_real


# ============================================================
# MODEL WEIGHTS — berdasarkan performa historis
# ============================================================
def _compute_model_weights(series: pd.Series,
                           models: list,
                           test_ratio: float = 0.2) -> dict:
    """
    Hitung bobot tiap model berdasarkan RMSE di test set.
    Model dengan RMSE lebih kecil dapat bobot lebih besar.
    """
    data = series.astype(float).dropna().values
    n = len(data)

    if n < 8:
        # Data kecil: bobot sama rata
        return {m: 1.0 / len(models) for m in models}

    split = max(1, int(n * (1 - test_ratio)))
    train = pd.Series(data[:split])
    test = data[split:]

    rmse_dict = {}
    for model_name in models:
        try:
            if model_name == "ARIMA":
                forecast = run_arima_forecast(train, steps=len(test))
            elif model_name == "LSTM":
                forecast = run_lstm_real(train, steps=len(test), lookback=min(3, len(train)-2), epochs=50)
            elif model_name == "GRU":
                forecast = run_gru_real(train, steps=len(test), lookback=min(3, len(train)-2), epochs=50)
            else:
                continue

            if len(forecast) >= len(test):
                rmse = float(np.sqrt(np.mean((test - forecast[:len(test)]) ** 2)))
                rmse_dict[model_name] = max(rmse, 1e-6)
        except Exception as e:
            print(f"[ENSEMBLE] {model_name} gagal: {e}")
            rmse_dict[model_name] = 999.0

    if not rmse_dict:
        return {m: 1.0 / len(models) for m in models}

    # Inverse RMSE weighting — model lebih akurat dapat bobot lebih besar
    inv = {m: 1.0 / r for m, r in rmse_dict.items()}
    total = sum(inv.values())
    return {m: v / total for m, v in inv.items()}


# ============================================================
# ENSEMBLE FORECAST
# ============================================================
def ensemble_forecast(series: pd.Series,
                      steps: int = 7,
                      models: list = None) -> dict:
    """
    Ensemble forecast dari multiple models.

    Returns:
        dict: {
            'forecast': np.ndarray,           # ensemble forecast
            'individual': {model: forecast},   # forecast per model
            'weights': {model: weight},        # bobot tiap model
            'ci_lower': np.ndarray,            # 95% CI lower
            'ci_upper': np.ndarray,            # 95% CI upper
        }
    """
    if models is None:
        models = ["ARIMA", "LSTM", "GRU"]

    data = series.astype(float).dropna()

    # ─── 1. Compute model weights ──────────────────────
    weights = _compute_model_weights(data, models)
    print(f"[ENSEMBLE] Model weights: {weights}")

    # ─── 2. Forecast per model ─────────────────────────
    individual = {}
    for model_name in models:
        try:
            if model_name == "ARIMA":
                fc = run_arima_forecast(data, steps=steps)
            elif model_name == "LSTM":
                fc = run_lstm_real(data, steps=steps, epochs=80)
            elif model_name == "GRU":
                fc = run_gru_real(data, steps=steps, epochs=80)
            else:
                continue
            individual[model_name] = fc
        except Exception as e:
            print(f"[ENSEMBLE] {model_name} forecast gagal: {e}")

    if not individual:
        last_val = float(data.iloc[-1]) if len(data) > 0 else 0.0
        return {
            "forecast": np.array([last_val] * steps),
            "individual": {},
            "weights": {},
            "ci_lower": np.array([last_val] * steps),
            "ci_upper": np.array([last_val] * steps),
        }

    # ─── 3. Weighted ensemble ──────────────────────────
    ensemble = np.zeros(steps)
    total_weight = 0.0
    for model_name, fc in individual.items():
        w = weights.get(model_name, 1.0 / len(individual))
        ensemble += w * fc[:steps]
        total_weight += w

    if total_weight > 0:
        ensemble /= total_weight

    # ─── 4. Confidence Interval via bootstrap ──────────
    ci_lower, ci_upper = _bootstrap_ci(individual, weights, steps, n_boot=200)

    return {
        "forecast": ensemble,
        "individual": individual,
        "weights": weights,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
    }


# ============================================================
# BOOTSTRAP CONFIDENCE INTERVAL
# ============================================================
def _bootstrap_ci(individual: dict, weights: dict,
                  steps: int, n_boot: int = 200,
                  alpha: float = 0.05) -> tuple:
    """
    Hitung confidence interval 95% dari ensemble via bootstrap.

    Cara: ambil sample acak dari forecast tiap model, hitung ensemble,
    ulangi n_boot kali, lalu ambil percentile 2.5% dan 97.5%.
    """
    rng = np.random.default_rng(seed=42)
    model_names = list(individual.keys())
    forecasts = np.array([individual[m][:steps] for m in model_names])
    w_arr = np.array([weights.get(m, 1.0 / len(model_names)) for m in model_names])
    w_arr = w_arr / w_arr.sum()

    boot_ensembles = []
    for _ in range(n_boot):
        # Sample weights dari Dirichlet (konsisten dengan w_arr)
        sampled_w = rng.dirichlet(w_arr * 10 + 0.1, size=1)[0]
        ens = np.sum(forecasts * sampled_w[:, None], axis=0)
        boot_ensembles.append(ens)

    boot_arr = np.array(boot_ensembles)  # shape (n_boot, steps)
    ci_lower = np.percentile(boot_arr, alpha / 2 * 100, axis=0)
    ci_upper = np.percentile(boot_arr, (1 - alpha / 2) * 100, axis=0)
    return ci_lower, ci_upper


# ============================================================
# CROSS-VALIDATION (Time Series K-Fold)
# ============================================================
def time_series_cv(series: pd.Series,
                   model: str = "ARIMA",
                   n_splits: int = 3) -> dict:
    """
    Time Series Cross-Validation.

    Beda dengan k-fold biasa:
    - Data TIDAK di-shuffle
    - Setiap fold, training data selalu di awal, test di akhir
    - Expanding window (train makin besar tiap fold)
    """
    data = series.astype(float).dropna()
    n = len(data)

    if n < 10:
        return {"error": f"Data terlalu sedikit ({n} baris, minimal 10)"}

    fold_size = n // (n_splits + 1)
    results = []

    for i in range(1, n_splits + 1):
        train_end = fold_size * i
        test_end = min(fold_size * (i + 1), n)

        if test_end <= train_end:
            continue

        train = data.iloc[:train_end]
        test = data.iloc[train_end:test_end]

        try:
            if model == "ARIMA":
                forecast = run_arima_forecast(train, steps=len(test))
            elif model == "LSTM":
                forecast = run_lstm_real(train, steps=len(test), epochs=50)
            elif model == "GRU":
                forecast = run_gru_real(train, steps=len(test), epochs=50)
            else:
                forecast = run_arima_forecast(train, steps=len(test))

            actual = test.values
            rmse = float(np.sqrt(np.mean((actual - forecast[:len(actual)]) ** 2)))
            mae = float(np.mean(np.abs(actual - forecast[:len(actual)])))

            results.append({
                "fold": i,
                "n_train": len(train),
                "n_test": len(test),
                "RMSE": round(rmse, 4),
                "MAE": round(mae, 4),
            })
        except Exception as e:
            results.append({"fold": i, "error": str(e)})

    # Aggregate
    rmse_list = [r["RMSE"] for r in results if "RMSE" in r]
    mae_list = [r["MAE"] for r in results if "MAE" in r]

    return {
        "model": model,
        "n_splits": n_splits,
        "folds": results,
        "mean_RMSE": round(float(np.mean(rmse_list)), 4) if rmse_list else None,
        "std_RMSE": round(float(np.std(rmse_list)), 4) if rmse_list else None,
        "mean_MAE": round(float(np.mean(mae_list)), 4) if mae_list else None,
        "std_MAE": round(float(np.std(mae_list)), 4) if mae_list else None,
    }