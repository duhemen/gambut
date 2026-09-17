# server/core/index_calc.py
"""Optimisasi Nelder-Mead untuk Indeks Kerawanan Gambut"""
import numpy as np
from scipy.optimize import minimize


def objective_function(weights, wt, sm, rf, temp):
    w1, w2, w3, w4 = weights
    index_calc = (w1 * (-wt)) + (w2 * (100 - sm)) + (w3 * (300 - rf)) + (w4 * temp)
    return np.var(index_calc) + (w1 + w2 + w3 + w4 - 1.0) ** 2


def calculate_peat_fire_index(wt_val, sm_val, rf_val, temp_val):
    """Return (score, status)"""
    try:
        wt = np.array([float(wt_val)])
        sm = np.array([float(sm_val)])
        rf = np.array([float(rf_val)])
        temp = np.array([float(temp_val)])

        initial_weights = [0.4, 0.3, 0.2, 0.1]
        res = minimize(
            objective_function,
            initial_weights,
            args=(wt, sm, rf, temp),
            method='Nelder-Mead',
            options={'xatol': 1e-4, 'maxiter': 500}
        )
        w1, w2, w3, w4 = res.x
        final_score = (w1 * (-wt_val)) + (w2 * (100 - sm_val)) + \
                      (w3 * (300 - rf_val)) + (w4 * temp_val)
        final_score = float(np.clip(final_score, 0, 100))

        if final_score >= 65.0:
            status = "🔴 BAHAYA"
        elif final_score >= 40.0:
            status = "🟡 SIAGA"
        else:
            status = "🟢 AMAN"
        return final_score, status
    except Exception as e:
        print(f"[ERROR NELDER-MEAD]: {e}")
        return 0.0, "🟢 AMAN"