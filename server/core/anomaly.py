# server/core/anomaly.py
"""
Anomaly Detection untuk data gambut.

Fitur UNGGULAN yang tidak ada di peatfr:
- Z-score (statistik klasik)
- IQR (robust terhadap outlier)
- Isolation Forest (ML-based)
- Ensemble (voting dari 3 metode)
"""
import numpy as np
import pandas as pd

try:
    from sklearn.ensemble import IsolationForest
    SKLEARN_OK = True
except ImportError:
    SKLEARN_OK = False


# ============================================================
# Z-SCORE
# ============================================================
def detect_zscore(series: pd.Series, threshold: float = 3.0) -> np.ndarray:
    """
    Deteksi outlier dengan Z-score.

    |z| > threshold → outlier (default 3.0 = 99.7%)
    """
    values = series.astype(float).values
    mean, std = np.nanmean(values), np.nanstd(values)

    if std < 1e-9:
        return np.zeros(len(values), dtype=bool)

    z = np.abs((values - mean) / std)
    return z > threshold


# ============================================================
# IQR (Interquartile Range)
# ============================================================
def detect_iqr(series: pd.Series, multiplier: float = 1.5) -> np.ndarray:
    """
    Deteksi outlier dengan IQR.

    Outlier jika:
        nilai < Q1 - multiplier * IQR
        atau
        nilai > Q3 + multiplier * IQR

    multiplier 1.5 = outlier standar
    multiplier 3.0 = extreme outlier
    """
    values = series.astype(float).values
    q1, q3 = np.nanpercentile(values, [25, 75])
    iqr = q3 - q1

    if iqr < 1e-9:
        return np.zeros(len(values), dtype=bool)

    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    return (values < lower) | (values > upper)


# ============================================================
# ISOLATION FOREST
# ============================================================
def detect_isolation_forest(df: pd.DataFrame,
                            columns: list,
                            contamination: float = 0.1,
                            random_state: int = 42) -> np.ndarray:
    """
    Deteksi outlier dengan Isolation Forest (ML).

    Return: bool array (True = outlier)
    """
    if not SKLEARN_OK or df.empty or len(df) < 10:
        return np.zeros(len(df), dtype=bool)

    try:
        X = df[columns].astype(float).fillna(0).values
        model = IsolationForest(
            contamination=min(contamination, 0.5),
            random_state=random_state,
            n_estimators=100,
        )
        preds = model.fit_predict(X)  # 1 = normal, -1 = outlier
        return preds == -1
    except Exception as e:
        print(f"[ANOMALY] Isolation Forest error: {e}")
        return np.zeros(len(df), dtype=bool)


# ============================================================
# ENSEMBLE
# ============================================================
def detect_anomalies_ensemble(df: pd.DataFrame,
                              columns: list = None,
                              min_votes: int = 2) -> pd.DataFrame:
    """
    Ensemble anomaly detection.

    Kolom yang dicek: wt, sm, rf, temp
    Setiap baris dianggap anomali kalau ≥ min_votes metode sepakat.

    Return: df dengan tambahan kolom:
        - anomaly (bool): True kalau anomali
        - anomaly_votes (int): berapa metode yang vote anomali
        - anomaly_reason (str): metode mana yang vote
    """
    if columns is None:
        columns = ['wt', 'sm', 'rf', 'temp']

    df_out = df.copy()
    n = len(df_out)

    if n == 0:
        df_out['anomaly'] = []
        df_out['anomaly_votes'] = []
        df_out['anomaly_reason'] = []
        return df_out

    # ─── Kumpulkan votes ─────────────────────────────
    votes = np.zeros((n, 4), dtype=bool)  # 3 metode × 4 kolom

    for i, col in enumerate(columns):
        if col not in df_out.columns:
            continue

        series = df_out[col]

        # Z-score per kolom
        try:
            z_out = detect_zscore(series, threshold=2.5)
            votes[:, 0] |= z_out
        except Exception:
            pass

        # IQR per kolom
        try:
            iqr_out = detect_iqr(series, multiplier=1.5)
            votes[:, 1] |= iqr_out
        except Exception:
            pass

    # Isolation Forest (multivariate — semua kolom sekaligus)
    try:
        iso_out = detect_isolation_forest(df_out, columns, contamination=0.15)
        votes[:, 2] = iso_out
    except Exception:
        pass

    # ─── Hitung total votes ──────────────────────────
    vote_counts = votes.sum(axis=1)
    is_anomaly = vote_counts >= min_votes

    # Buat reason string
    reasons = []
    method_names = ["Z-score", "IQR", "IsolationForest"]
    for row_idx in range(n):
        methods_voted = [
            method_names[j]
            for j in range(3)
            if votes[row_idx, j]
        ]
        reasons.append(" + ".join(methods_voted) if methods_voted else "")

    df_out['anomaly'] = is_anomaly
    df_out['anomaly_votes'] = vote_counts
    df_out['anomaly_reason'] = reasons

    return df_out


# ============================================================
# SUMMARY
# ============================================================
def get_anomaly_summary(df_detected: pd.DataFrame) -> dict:
    """Ringkasan hasil deteksi anomali."""
    if 'anomaly' not in df_detected.columns:
        return {"total": 0, "anomalies": 0, "normal": 0}

    total = len(df_detected)
    anomalies = int(df_detected['anomaly'].sum())

    # Distribusi berdasarkan kolom yang bermasalah
    anomaly_rows = df_detected[df_detected['anomaly']]
    reasons = anomaly_rows['anomaly_reason'].value_counts().to_dict() if anomalies > 0 else {}

    return {
        "total": total,
        "anomalies": anomalies,
        "normal": total - anomalies,
        "anomaly_rate": round(anomalies / total * 100, 2) if total > 0 else 0.0,
        "by_reason": reasons,
        "indices": anomaly_rows.index.tolist()[:20],  # limit 20
    }