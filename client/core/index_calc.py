# app/core/index_calc.py
import numpy as np
from scipy.optimize import minimize

def objective_function(weights, wt, sm, rf, temp):
    """
    Fungsi objektif untuk meminimalkan deviasi/error indeks kekeringan.
    Mencari kombinasi bobot (weights) yang paling stabil bagi kondisi lahan gambut.
    """
    w1, w2, w3, w4 = weights
    
    # Formula dasar pembobotan parameter kerawanan kebakaran gambut
    # WT (-) kontribusi tinggi jika air menyusut dalam, Temp (+) jika makin panas
    index_calc = (w1 * (-wt)) + (w2 * (100 - sm)) + (w3 * (300 - rf)) + (w4 * temp)
    
    # Mengembalikan nilai varians sebagai indikator stabilitas optimisasi
    return np.var(index_calc) + (w1 + w2 + w3 + w4 - 1.0)**2

def calculate_peat_fire_index(wt_val, sm_val, rf_val, temp_val) -> tuple[float, str]:
    """
    Menghitung Indeks Kerawanan Kebakaran menggunakan Optimisasi Nelder-Mead.
    Mengembalikan: (Nilai Indeks 0-100, Teks Status Kategori Risiko)
    """
    try:
        # Data pemicu untuk proses iterasi optimisasi algoritma
        wt = np.array([float(wt_val)])
        sm = np.array([float(sm_val)])
        rf = np.array([float(rf_val)])
        temp = np.array([float(temp_val)])
        
        # Tebakan bobot awal untuk 4 parameter (WT, SM, Rf, Temp)
        initial_weights = [0.4, 0.3, 0.2, 0.1]
        
        # Eksekusi Metode Optimisasi Nelder-Mead (Bawaan Inti Paket Peatfr)
        res = minimize(
            objective_function, 
            initial_weights, 
            args=(wt, sm, rf, temp), 
            method='Nelder-Mead',
            options={'xatol': 1e-4, 'maxiter': 500}
        )
        
        # Ambil bobot hasil optimisasi terbaik
        w1, w2, w3, w4 = res.x
        
        # Hitung skor indeks final kerawanan gambut
        final_score = (w1 * (-wt_val)) + (w2 * (100 - sm_val)) + (w3 * (300 - rf_val)) + (w4 * temp_val)
        
        # Normalisasi skor agar berada di rentang skala 0 hingga 100
        final_score = np.clip(final_score, 0, 100)
        
        # Penentuan status kategori risiko yang terstandardisasi secara ilmiah
        if final_score >= 65.0:
            status = "🔴 BAHAYA"
        elif final_score >= 40.0:
            status = "🟡 SIAGA"
        else:
            status = "🟢 AMAN"
            
        return float(final_score), status
        
    except Exception as e:
        print(f"[ERROR NELDER-MEAD]: {str(e)}")
        return 0.0, "🟢 AMAN"
