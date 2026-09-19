# server/core/index_calc.py
"""
Peat Fire Vulnerability Index (PFVI) — Optimisasi Nelder-Mead.

Mengacu pada metodologi peatfr (R package):
- Normalisasi min-max tiap variabel sebelum weighting
- Bobot optimal di-cari dari SELURUH time series
- Constraint: setiap bobot ∈ [0.05, 1.0], total = 1.0
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize


# ============================================================
# NORMALIZATION
# ============================================================
def _minmax(arr: np.ndarray) -> np.ndarray:
    """Normalisasi min-max ke [0, 1]."""
    arr = np.asarray(arr, dtype=float)
    lo, hi = np.nanmin(arr), np.nanmax(arr)
    if hi - lo < 1e-9:
        return np.zeros_like(arr)
    return (arr - lo) / (hi - lo)


def _normalize_features(wt, sm, rf, temp):
    """
    Normalisasi 4 fitur pembentuk PFVI.
    Setelah normalisasi, semua nilai ∈ [0, 1] dan arahnya
    mengikuti 'semakin tinggi = semakin rawan'.

    Returns:
        (n_wt, n_sm, n_rf, n_temp)
    """
    n_wt = _minmax(-np.asarray(wt, dtype=float))       # WT dalam → rawan
    n_sm = _minmax(100 - np.asarray(sm, dtype=float))  # SM rendah → rawan
    n_rf = _minmax(300 - np.asarray(rf, dtype=float))  # RF rendah → rawan
    n_temp = _minmax(np.asarray(temp, dtype=float))    # Suhu tinggi → rawan
    return n_wt, n_sm, n_rf, n_temp


# ============================================================
# PFVI — SCORING
# ============================================================
def pfvi_score(wt, sm, rf, temp, weights, normalization=None) -> float:
    w1, w2, w3, w4 = weights

    if normalization is None:
        return (w1 * (-float(wt))) + (w2 * (100 - float(sm))) + \
               (w3 * (300 - float(rf))) + (w4 * float(temp))

    (mn_wt, mx_wt, mn_sm, mx_sm,
     mn_rf, mx_rf, mn_tm, mx_tm) = normalization

    def _norm(v, lo, hi):
        if hi - lo < 1e-9:
            return 0.0
        n = (v - lo) / (hi - lo)
        return max(0.0, min(1.0, n))   # ⬅️ TAMBAH CLIP

    n_wt = 1.0 - _norm(wt, mn_wt, mx_wt)
    n_sm = 1.0 - _norm(sm, mn_sm, mx_sm)
    n_rf = 1.0 - _norm(rf, mn_rf, mx_rf)
    n_tm = _norm(temp, mn_tm, mx_tm)

    score_01 = (w1 * n_wt) + (w2 * n_sm) + (w3 * n_rf) + (w4 * n_tm)
    return score_01 * 100.0


# ============================================================
# OBJECTIVE — NELDER-MEAD
# ============================================================
def _objective_function(weights, n_wt, n_sm, n_rf, n_temp):
    """
    Fungsi objektif:
        - Minimalkan variansi PFVI (biar konsisten)
        - Penalti kalau total bobot != 1.0
        - Regularisasi entropi: cegah bobot degenerate (0,0,0,1)
    """
    pfvi = (weights[0] * n_wt) + (weights[1] * n_sm) + \
           (weights[2] * n_rf) + (weights[3] * n_temp)

    variance = float(np.var(pfvi))
    constraint = (sum(weights) - 1.0) ** 2

    # Entropy regularization — biar bobot tersebar merata
    eps = 1e-9
    entropy = -np.sum(weights * np.log(weights + eps))
    entropy_target = np.log(4.0)  # entropy max untuk 4 bobot merata
    entropy_penalty = (entropy_target - entropy) * 0.5  # skala kecil

    return variance + constraint * 100.0 + entropy_penalty


# ============================================================
# OPTIMIZATION
# ============================================================
def optimize_pfvi_params(df: pd.DataFrame) -> dict:
    """
    Optimasi bobot PFVI dari seluruh time series.

    Returns:
        dict: {
            'weights': [w1, w2, w3, w4],
            'normalization': (mn_wt, mx_wt, mn_sm, mx_sm, ...),
            'n_samples': int,
            'method': 'normalized' | 'legacy',
        }
    """
    fallback = {
        'weights': [0.4, 0.3, 0.2, 0.1],
        'normalization': None,
        'n_samples': 0,
        'method': 'fallback',
    }

    try:
        # Ambil & filter data
        cols = ['wt', 'sm', 'rf', 'temp']
        df_clean = df[cols].dropna()
        if len(df_clean) < 3:
            print("[PFVI] Data < 3, pakai bobot default")
            return fallback

        wt = df_clean['wt'].astype(float).values
        sm = df_clean['sm'].astype(float).values
        rf = df_clean['rf'].astype(float).values
        temp = df_clean['temp'].astype(float).values

        # Normalisasi
        n_wt, n_sm, n_rf, n_temp = _normalize_features(wt, sm, rf, temp)

        # Simpan parameter normalisasi (min, max) untuk dipakai nanti
        normalization = (
            float(np.min(wt)),  float(np.max(wt)),
            float(np.min(sm)),  float(np.max(sm)),
            float(np.min(rf)),  float(np.max(rf)),
            float(np.min(temp)), float(np.max(temp)),
        )

        # Initial guess
        x0 = np.array([0.25, 0.25, 0.25, 0.25])

        # Bounds: minimal 0.05 supaya setiap variabel punya kontribusi
        bounds = [(0.05, 1.0)] * 4

        # Optimasi
        result = minimize(
            _objective_function,
            x0,
            args=(n_wt, n_sm, n_rf, n_temp),
            method='Nelder-Mead',
            bounds=bounds,
            options={'xatol': 1e-4, 'fatol': 1e-4, 'maxiter': 1000},
        )

        if not result.success:
            print(f"[PFVI] Optimasi tidak konvergen: {result.message}")

        weights = result.x
        # Normalisasi total = 1.0
        total = float(weights.sum())
        if total > 0:
            weights = weights / total

        weights_list = [round(float(w), 4) for w in weights]
        print(f"[PFVI] Bobot optimal (normalized): {weights_list}")

        return {
            'weights': weights_list,
            'normalization': normalization,
            'n_samples': len(df_clean),
            'method': 'normalized',
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[PFVI] Error: {e}")
        return fallback


# ============================================================
# STATUS
# ============================================================
def classify_status(score: float) -> str:
    if score >= 65.0:
        return "🔴 BAHAYA"
    elif score >= 40.0:
        return "🟡 SIAGA"
    else:
        return "🟢 AMAN"


# ============================================================
# PUBLIC API — SINGLE POINT
# ============================================================
def calculate_peat_fire_index(wt_val, sm_val, rf_val, temp_val,
                              weights=None, normalization=None) -> tuple:
    """
    Hitung PFVI satu titik.

    Returns:
        (score, status)
    """
    try:
        if weights is None:
            weights = [0.4, 0.3, 0.2, 0.1]

        score = pfvi_score(wt_val, sm_val, rf_val, temp_val,
                           weights, normalization)
        score = float(np.clip(score, 0, 100))
        return score, classify_status(score)
    except Exception as e:
        print(f"[PFVI] Error: {e}")
        return 0.0, "🟢 AMAN"


# ============================================================
# PUBLIC API — TIME SERIES
# ============================================================
def calculate_pfvi_series(df: pd.DataFrame, weights=None,
                          normalization=None) -> pd.DataFrame:
    """Hitung PFVI untuk seluruh time series."""
    df_out = df.copy()

    if weights is None:
        opt = optimize_pfvi_params(df)
        weights = opt['weights']
        normalization = opt['normalization']

    scores, statuses = [], []
    for _, row in df_out.iterrows():
        score = pfvi_score(row['wt'], row['sm'], row['rf'], row['temp'],
                           weights, normalization)
        score = float(np.clip(score, 0, 100))
        scores.append(round(score, 2))
        statuses.append(classify_status(score))

    df_out['pfvi'] = scores
    df_out['status'] = statuses
    return df_out