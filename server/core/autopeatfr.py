# server/core/autopeatfr.py
"""Pipeline all-in-one dengan ensemble + confidence interval."""
import numpy as np
import pandas as pd

from server.core.imputation import impute
from server.core.forecasting import run_forecast, evaluate_forecast
from server.core.deep_learning import get_backend_info
from server.core.index_calc import (
    optimize_pfvi_params, pfvi_score, classify_status
)


def autopeatfr(df: pd.DataFrame,
               imputation: str = "knn",
               model: str = "ENSEMBLE",
               h: int = 7,
               evaluate: bool = True,
               ensemble_ci: bool = True) -> dict:
    """
    Pipeline all-in-one.

    Args:
        model: 'ARIMA' | 'LSTM' | 'GRU' | 'ENSEMBLE'
        ensemble_ci: kalau True & model ENSEMBLE, hitung CI 95%
    """
    result = {
        "imputation": imputation,
        "model": model,
        "horizon": h,
        "dl_backend": get_backend_info(),
        "success": False,
    }

    try:
        # ─── 1. Imputasi ─────────────────────────────
        cols = ['wt', 'sm', 'rf', 'temp']
        missing = [c for c in cols if c not in df.columns]
        if missing:
            result["error"] = f"Kolom hilang: {missing}"
            return result

        df_clean = impute(df.copy(), cols, method=imputation)
        result["n_rows"] = len(df_clean)

        # ─── 2. Optimasi PFVI ────────────────────────
        opt = optimize_pfvi_params(df_clean)
        weights = opt['weights']
        normalization = opt['normalization']
        result["weights"] = weights
        result["normalization"] = normalization
        result["pfvi_method"] = opt['method']

        # ─── 3. Forecast ─────────────────────────────
        wt_series = df_clean['wt'].astype(float)

        if model.upper() == "ENSEMBLE":
            from server.core.ensemble import ensemble_forecast
            ens_result = ensemble_forecast(wt_series, steps=h)
            forecast = ens_result["forecast"]
            result["forecast_individual"] = {
                k: [round(float(x), 2) for x in v]
                for k, v in ens_result["individual"].items()
            }
            result["forecast_weights"] = {
                k: round(float(v), 4)
                for k, v in ens_result["weights"].items()
            }
            if ensemble_ci:
                result["ci_lower"] = [round(float(x), 2) for x in ens_result["ci_lower"]]
                result["ci_upper"] = [round(float(x), 2) for x in ens_result["ci_upper"]]
                result["ci_level"] = 0.95
        else:
            forecast = run_forecast(wt_series, model=model, steps=h)

        result["forecast_wt"] = [round(float(x), 2) for x in forecast]

        # ─── 4. Evaluasi ─────────────────────────────
        if evaluate and len(wt_series.dropna()) >= 10:
            result["evaluation"] = evaluate_forecast(
                wt_series, model=model, test_ratio=0.2
            )

        # ─── 5. PFVI forecast ────────────────────────
        last_row = df_clean.dropna(subset=cols).iloc[-1]
        sm_last = float(last_row['sm'])
        rf_last = float(last_row['rf'])
        temp_last = float(last_row['temp'])

        pfvi_forecast = []
        for i, fwt in enumerate(forecast):
            score = pfvi_score(fwt, sm_last, rf_last, temp_last, weights, normalization)
            score = float(np.clip(score, 0, 100))
            entry = {
                "step": i + 1,
                "wt": round(float(fwt), 2),
                "score": round(score, 2),
                "status": classify_status(score),
            }
            if "ci_lower" in result:
                entry["wt_lower"] = result["ci_lower"][i]
                entry["wt_upper"] = result["ci_upper"][i]
            pfvi_forecast.append(entry)
        result["pfvi_forecast"] = pfvi_forecast

        # ─── 6. PFVI historis ────────────────────────
        historical = []
        for _, row in df_clean.iterrows():
            score = pfvi_score(row['wt'], row['sm'], row['rf'], row['temp'],
                               weights, normalization)
            score = float(np.clip(score, 0, 100))
            historical.append({
                "tanggal": str(row['tanggal']),
                "pfvi": round(score, 2),
                "status": classify_status(score),
            })
        result["pfvi_historical"] = historical

        result["success"] = True
        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        result["error"] = str(e)
        return result