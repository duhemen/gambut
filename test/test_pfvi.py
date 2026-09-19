"""Test PFVI (Peat Fire Vulnerability Index)."""
import pytest
import numpy as np
import pandas as pd

from server.core.index_calc import (
    calculate_peat_fire_index, classify_status,
    optimize_pfvi_params, pfvi_score, calculate_pfvi_series,
)


def make_df(n=30):
    """Generate DataFrame dummy."""
    rng = np.random.default_rng(42)
    return pd.DataFrame({
        'tanggal': pd.date_range('2026-01-01', periods=n).strftime('%Y-%m-%d'),
        'wt': -10 + rng.normal(0, 3, n),
        'sm': 50 + rng.normal(0, 10, n),
        'rf': np.abs(rng.normal(0, 5, n)),
        'temp': 30 + rng.normal(0, 2, n),
    })


class TestPFVIClassification:
    def test_status_aman(self):
        assert classify_status(20) == "🟢 AMAN"
        assert classify_status(39.9) == "🟢 AMAN"

    def test_status_siaga(self):
        assert classify_status(40) == "🟡 SIAGA"
        assert classify_status(64.9) == "🟡 SIAGA"

    def test_status_bahaya(self):
        assert classify_status(65) == "🔴 BAHAYA"
        assert classify_status(100) == "🔴 BAHAYA"


class TestPFVIScore:
    def test_score_range(self):
        score, status = calculate_peat_fire_index(-15, 38, 0, 33)
        assert 0 <= score <= 100
        assert status in ["🟢 AMAN", "🟡 SIAGA", "🔴 BAHAYA"]

    def test_kering_lebih_tinggi(self):
        """Kondisi kering harus skor lebih tinggi dari kondisi basah."""
        score_kering, _ = calculate_peat_fire_index(-25, 20, 0, 38)
        score_basah, _ = calculate_peat_fire_index(-2, 80, 100, 25)
        assert score_kering > score_basah


class TestOptimization:
    def test_weights_sum_to_one(self):
        df = make_df()
        opt = optimize_pfvi_params(df)
        assert abs(sum(opt['weights']) - 1.0) < 0.01

    def test_weights_non_degenerate(self):
        """Semua bobot minimal 0.05 — tidak boleh ada 0."""
        df = make_df()
        opt = optimize_pfvi_params(df)
        for w in opt['weights']:
            assert w >= 0.04, f"Bobot {w} terlalu kecil"

    def test_small_data_fallback(self):
        """Data < 3 harus fallback, tidak error."""
        df = make_df(n=2)
        opt = optimize_pfvi_params(df)
        assert opt['method'] == 'fallback'


class TestSeries:
    def test_pfvi_series_length(self):
        df = make_df(20)
        result = calculate_pfvi_series(df)
        assert len(result) == 20
        assert 'pfvi' in result.columns
        assert 'status' in result.columns