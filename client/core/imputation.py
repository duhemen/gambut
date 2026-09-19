# app/core/imputation.py
import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer

def linear_interpolation(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    df_filled = df.copy()
    for col in columns:
        df_filled[col] = df_filled[col].interpolate(method='linear')
    return df_filled

def spline_interpolation(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    df_filled = df.copy()
    for col in columns:
        # Menangani interpolasi jika baris data masih terlalu sedikit
        if len(df_filled.dropna(subset=[col])) > 2:
            df_filled[col] = df_filled[col].interpolate(method='spline', order=2)
        else:
            df_filled[col] = df_filled[col].interpolate(method='linear')
    return df_filled

def knn_imputation(df: pd.DataFrame, columns: list, k: int = 2) -> pd.DataFrame:
    df_filled = df.copy()
    imputer = KNNImputer(n_neighbors=k)
    df_filled[columns] = imputer.fit_transform(df_filled[columns])
    return df_filled
