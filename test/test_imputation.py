"""Test imputasi."""
import pytest
import numpy as np
import pandas as pd

from server.core.imputation import (
    linear_interpolation, spline_interpolation,
    knn_imputation, loess_interpolation, impute,
)


@pytest.fixture
def df_with_nan():
    return pd.DataFrame({
        'wt': [-5.0, np.nan, -11.0, np.nan, -15.0, -18.0],
        'sm': [55.0, 50.0, np.nan, 42.0, 38.0, np.nan],
        'rf': [12.5, 4.2, 0.0, 0.0, 0.0, 0.0],
        'temp': [28.5, 29.8, 31.2, np.nan, 32.2, 33.5],
    })


class TestImputation:
    def test_linear_no_nan(self, df_with_nan):
        result = linear_interpolation(df_with_nan, ['wt', 'sm', 'temp'])
        assert not result['wt'].isna().any()
        assert not result['sm'].isna().any()

    def test_spline_no_nan(self, df_with_nan):
        result = spline_interpolation(df_with_nan, ['wt', 'sm', 'temp'])
        assert not result['wt'].isna().any()

    def test_knn_no_nan(self, df_with_nan):
        result = knn_imputation(df_with_nan, ['wt', 'sm', 'temp'])
        assert not result['wt'].isna().any()

    def test_loess_no_nan(self, df_with_nan):
        result = loess_interpolation(df_with_nan, ['wt', 'sm', 'temp'])
        assert not result['wt'].isna().any()

    def test_dispatcher(self, df_with_nan):
        for method in ['knn', 'spline', 'loess', 'linear']:
            result = impute(df_with_nan.copy(), ['wt'], method=method)
            assert not result['wt'].isna().any(), f"Gagal di {method}"