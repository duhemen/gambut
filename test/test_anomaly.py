"""Test anomaly detection."""
import numpy as np
import pandas as pd

from server.core.anomaly import (
    detect_zscore, detect_iqr, detect_anomalies_ensemble, get_anomaly_summary,
)


def test_zscore_detects_outlier():
    series = pd.Series([10, 11, 12, 10, 11, 100, 11, 10])
    result = detect_zscore(series, threshold=2.0)
    assert bool(result[5]) is True   # ← fix: bungkus bool()
    assert int(sum(result)) == 1


def test_iqr_detects_outlier():
    series = pd.Series([10, 11, 12, 10, 11, 100, 11, 10])
    result = detect_iqr(series, multiplier=1.5)
    assert bool(result[5]) is True   # ← fix

def test_ensemble_voting():
    df = pd.DataFrame({
        'wt': [-5, -6, -7, -5, -6, -100, -5, -6],  # outlier di index 5
        'sm': [50, 51, 50, 49, 51, 50, 50, 50],
        'rf': [0, 0, 0, 0, 0, 0, 0, 0],
        'temp': [30, 31, 30, 30, 31, 30, 30, 30],
    })
    result = detect_anomalies_ensemble(df, min_votes=2)
    assert result['anomaly'].iloc[5] is True or result['anomaly'].iloc[5] == True


def test_summary_empty():
    df = pd.DataFrame(columns=['anomaly'])
    summary = get_anomaly_summary(df)
    assert summary['total'] == 0