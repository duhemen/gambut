# server/core/imputation.py
"""
Algoritma imputasi data kosong.

Mengacu pada peatfr (R package):
- knn_imputation()
- spline_interpolation()
- linear_interpolation()
- loess_interpolation()  ← NEW
"""
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer

try:
    from statsmodels.nonparametric.smoothers_lowess import lowess
    LOESS_AVAILABLE = True
except ImportError:
    LOESS_AVAILABLE = False


# ============================================================
# LINEAR
# ============================================================
def linear_interpolation(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Interpolasi linear antar titik."""
    df_filled = df.copy()
    for col in columns:
        df_filled[col] = df_filled[col].interpolate(method='linear')
        df_filled[col] = df_filled[col].bfill().ffill()
    return df_filled


# ============================================================
# SPLINE
# ============================================================
def spline_interpolation(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Interpolasi spline orde 2 (parabola)."""
    df_filled = df.copy()
    for col in columns:
        if df_filled[col].notna().sum() > 2:
            try:
                df_filled[col] = df_filled[col].interpolate(method='spline', order=2)
            except Exception:
                df_filled[col] = df_filled[col].interpolate(method='linear')
        else:
            df_filled[col] = df_filled[col].interpolate(method='linear')
        df_filled[col] = df_filled[col].bfill().ffill()
    return df_filled


# ============================================================
# KNN
# ============================================================
def knn_imputation(df: pd.DataFrame, columns: list, k: int = 2) -> pd.DataFrame:
    """KNN imputation."""
    df_filled = df.copy()
    if len(df_filled) < k:
        k = max(1, len(df_filled))
    imputer = KNNImputer(n_neighbors=k)
    df_filled[columns] = imputer.fit_transform(df_filled[columns])
    return df_filled


# ============================================================
# LOESS (NEW)
# ============================================================
def loess_interpolation(df: pd.DataFrame, columns: list,
                        span: float = 0.75) -> pd.DataFrame:
    """
    Loess (Locally Estimated Scatterplot Smoothing).

    Mengacu pada peatfr::loess_interpolation().

    Args:
        df: DataFrame
        columns: kolom yang akan diimputasi
        span: fraksi data yang dipakai untuk smoothing (0.0–1.0)
    """
    df_filled = df.copy()

    if not LOESS_AVAILABLE:
        print("[LOESS] statsmodels tidak tersedia, fallback ke linear")
        return linear_interpolation(df, columns)

    for col in columns:
        series = df_filled[col].copy()
        mask = series.notna()

        if mask.sum() < 3:
            # Terlalu sedikit data valid
            df_filled[col] = series.interpolate(method='linear').bfill().ffill()
            continue

        try:
            x_valid = np.arange(len(series))[mask.values]
            y_valid = series[mask].values

            # Loess hanya bisa interpolasi di titik yang ada,
            # jadi kita fit ke semua x, lalu pakai nilai yang kosong
            smoothed = lowess(y_valid, x_valid, frac=span, return_sorted=False)

            # Isi nilai kosong dengan hasil smoothed
            for i, idx in enumerate(np.where(mask.values)[0]):
                df_filled.loc[df_filled.index[idx], col] = smoothed[i]

            # Kalau masih ada NaN (biasanya di ujung), interpolasi linear
            df_filled[col] = df_filled[col].interpolate(method='linear')
            df_filled[col] = df_filled[col].bfill().ffill()

        except Exception as e:
            print(f"[LOESS] Error pada kolom {col}: {e}")
            df_filled[col] = series.interpolate(method='linear').bfill().ffill()

    return df_filled


# ============================================================
# DISPATCHER
# ============================================================
def impute(df: pd.DataFrame, columns: list, method: str = "knn") -> pd.DataFrame:
    """
    Dispatcher imputasi berdasarkan nama metode.

    Supported:
        - 'knn'    → KNN Imputer (default)
        - 'spline' → Spline Curve
        - 'linear' → Linear Interpolation
        - 'loess'  → Loess Smoothing
    """
    m = (method or "").lower()
    if "knn" in m:
        return knn_imputation(df, columns)
    elif "spline" in m:
        return spline_interpolation(df, columns)
    elif "loess" in m:
        return loess_interpolation(df, columns)
    else:
        return linear_interpolation(df, columns)