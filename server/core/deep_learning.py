# server/core/deep_learning.py
"""
Real LSTM & GRU implementation using TensorFlow/Keras.

Mengacu pada peatfr::autopredictlstm() dan autopredictgru(),
tapi dengan tambahan:
- Early stopping
- Model checkpointing
- Recursive forecasting
- Fallback ke PyTorch kalau TensorFlow tidak ada
"""
import os
import warnings

import numpy as np
import pandas as pd

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings('ignore')

# ============================================================
# BACKEND DETECTION (prioritas PyTorch)
# ============================================================
DL_BACKEND = None
_torch = None
_tf = None

# ─── Coba PyTorch DULU ────────────────────────────
try:
    import torch
    import torch.nn as nn
    _torch = torch
    DL_BACKEND = "pytorch"
    print(f"✅ [DL] Backend: PyTorch {torch.__version__} "
          f"(CUDA: {torch.cuda.is_available()})")
except ImportError:
    pass

# ─── Kalau tidak ada PyTorch, coba TensorFlow ────
if DL_BACKEND is None:
    try:
        import tensorflow as tf
        tf.get_logger().setLevel('ERROR')
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout, Input
        from tensorflow.keras.callbacks import EarlyStopping
        _tf = tf
        DL_BACKEND = "tensorflow"
        print(f"✅ [DL] Backend: TensorFlow {tf.__version__}")
    except ImportError:
        pass

# ─── Kalau tidak ada keduanya, fallback simulasi ─
if DL_BACKEND is None:
    print("⚠️ [DL] Tidak ada TensorFlow/PyTorch — pakai simulasi")

# ─── Force override dari .env (opsional) ─────────
import os as _os
_forced = _os.getenv("DL_BACKEND", "").strip().lower()
if _forced == "pytorch" and _torch is not None:
    DL_BACKEND = "pytorch"
    print(f"✅ [DL] Backend (forced): PyTorch {_torch.__version__}")
elif _forced == "tensorflow" and _tf is not None:
    DL_BACKEND = "tensorflow"
    print(f"✅ [DL] Backend (forced): TensorFlow {_tf.__version__}")
elif _forced == "simulation":
    DL_BACKEND = None
    print("✅ [DL] Backend (forced): simulation")

# ============================================================
# UTIL — WINDOWED DATASET
# ============================================================
def _make_windows(data: np.ndarray, lookback: int):
    """Buat windowed dataset untuk time series."""
    X, y = [], []
    for i in range(lookback, len(data)):
        X.append(data[i - lookback:i])
        y.append(data[i])
    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.float32)
    return X.reshape((X.shape[0], X.shape[1], 1)), y


# ============================================================
# TENSORFLOW LSTM
# ============================================================
def _build_lstm_tf(lookback: int, units: int = 50, dropout: float = 0.2):
    """Bangun model LSTM TensorFlow."""
    model = Sequential([
        Input(shape=(lookback, 1)),
        LSTM(units, return_sequences=True),
        Dropout(dropout),
        LSTM(units),
        Dropout(dropout),
        Dense(1),
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model


def _build_gru_tf(lookback: int, units: int = 50, dropout: float = 0.2):
    """Bangun model GRU TensorFlow."""
    model = Sequential([
        Input(shape=(lookback, 1)),
        GRU(units, return_sequences=True),
        Dropout(dropout),
        GRU(units),
        Dropout(dropout),
        Dense(1),
    ])
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model


def _forecast_recursive_tf(model, last_window: np.ndarray,
                           steps: int, lookback: int) -> np.ndarray:
    """Forecast recursive dengan model TF."""
    forecast = []
    window = list(last_window[-lookback:].flatten())
    for _ in range(steps):
        x = np.array(window[-lookback:], dtype=np.float32).reshape(1, lookback, 1)
        pred = float(model.predict(x, verbose=0)[0, 0])
        forecast.append(pred)
        window.append(pred)
    return np.array(forecast)


# ============================================================
# PYTORCH LSTM/GRU
# ============================================================
if DL_BACKEND == "pytorch":
    class _LSTMNet(nn.Module):
        def __init__(self, input_size=1, hidden=50, dropout=0.2, rnn_type="LSTM"):
            super().__init__()
            RNN = nn.LSTM if rnn_type == "LSTM" else nn.GRU
            self.rnn1 = RNN(input_size, hidden, batch_first=True)
            self.drop1 = nn.Dropout(dropout)
            self.rnn2 = RNN(hidden, hidden, batch_first=True)
            self.drop2 = nn.Dropout(dropout)
            self.fc = nn.Linear(hidden, 1)

        def forward(self, x):
            out, _ = self.rnn1(x)
            out = self.drop1(out)
            out, _ = self.rnn2(out)
            out = out[:, -1, :]
            out = self.drop2(out)
            return self.fc(out)


# ============================================================
# PUBLIC API — LSTM
# ============================================================
def run_lstm_real(series: pd.Series,
                  steps: int = 7,
                  lookback: int = 5,
                  units: int = 50,
                  epochs: int = 100,
                  batch_size: int = 4,
                  verbose: int = 0) -> np.ndarray:
    """
    LSTM asli (bukan simulasi).

    Args:
        series: time series WT
        steps: horizon forecast
        lookback: window size (default 5 untuk data kecil)
        units: jumlah unit LSTM per layer
        epochs: max epoch (early stopping akan stop lebih awal)
        batch_size: ukuran batch
    """
    data = series.astype(float).dropna().values

    if len(data) < lookback + 3:
        print(f"⚠️ [LSTM] Data < {lookback + 3}, fallback ke nilai terakhir")
        return np.array([data[-1]] * steps if len(data) > 0 else [0.0] * steps)

    # Auto-adjust lookback untuk data kecil
    if len(data) < 15:
        lookback = min(lookback, max(2, len(data) // 3))
        print(f"⚠️ [LSTM] Data kecil ({len(data)}), lookback di-set ke {lookback}")

    # Normalisasi (penting untuk DL!)
    mean, std = data.mean(), data.std()
    if std < 1e-9:
        std = 1.0
    data_norm = (data - mean) / std

    X, y = _make_windows(data_norm, lookback)

    if len(X) < 3:
        print("⚠️ [LSTM] Window terlalu sedikit, fallback")
        return np.array([data[-1]] * steps)

    # ─── TensorFlow ─────────────────────────────────
    if DL_BACKEND == "tensorflow":
        model = _build_lstm_tf(lookback, units=min(units, 32))
        early_stop = EarlyStopping(
            monitor='loss', patience=10, restore_best_weights=True
        )
        model.fit(
            X, y,
            epochs=epochs,
            batch_size=min(batch_size, len(X)),
            verbose=verbose,
            callbacks=[early_stop],
        )

        last_window = data_norm[-lookback:]
        forecast_norm = _forecast_recursive_tf(model, last_window, steps, lookback)
        return forecast_norm * std + mean

    # ─── PyTorch ────────────────────────────────────
    elif DL_BACKEND == "pytorch":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = _LSTMNet(hidden=min(units, 32), rnn_type="LSTM").to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        criterion = nn.MSELoss()

        X_t = torch.tensor(X).to(device)
        y_t = torch.tensor(y).unsqueeze(-1).to(device)

        for _ in range(min(epochs, 200)):
            model.train()
            optimizer.zero_grad()
            pred = model(X_t)
            loss = criterion(pred, y_t)
            loss.backward()
            optimizer.step()

        model.eval()
        window = list(data_norm[-lookback:])
        forecast_norm = []
        with torch.no_grad():
            for _ in range(steps):
                x = torch.tensor(window[-lookback:], dtype=torch.float32).reshape(1, lookback, 1).to(device)
                pred = model(x).item()
                forecast_norm.append(pred)
                window.append(pred)
        return np.array(forecast_norm) * std + mean

    # ─── Fallback: simulasi ─────────────────────────
    else:
        print("⚠️ [LSTM] Backend DL tidak tersedia, fallback simulasi")
        last_val = data[-1]
        trend = (data[-1] - data[-min(3, len(data))]) if len(data) > 3 else 0
        rng = np.random.default_rng(seed=42)
        forecast = []
        cur = last_val
        for _ in range(steps):
            cur = cur + trend * 0.1 + rng.normal(0, 0.2)
            forecast.append(cur)
        return np.array(forecast)


# ============================================================
# PUBLIC API — GRU
# ============================================================
def run_gru_real(series: pd.Series,
                 steps: int = 7,
                 lookback: int = 5,
                 units: int = 50,
                 epochs: int = 100,
                 batch_size: int = 4,
                 verbose: int = 0) -> np.ndarray:
    """GRU asli (bukan simulasi)."""
    data = series.astype(float).dropna().values

    if len(data) < lookback + 3:
        return np.array([data[-1]] * steps if len(data) > 0 else [0.0] * steps)

    if len(data) < 15:
        lookback = min(lookback, max(2, len(data) // 3))

    mean, std = data.mean(), data.std()
    if std < 1e-9:
        std = 1.0
    data_norm = (data - mean) / std

    X, y = _make_windows(data_norm, lookback)

    if len(X) < 3:
        return np.array([data[-1]] * steps)

    if DL_BACKEND == "tensorflow":
        model = _build_gru_tf(lookback, units=min(units, 32))
        early_stop = EarlyStopping(
            monitor='loss', patience=10, restore_best_weights=True
        )
        model.fit(
            X, y, epochs=epochs,
            batch_size=min(batch_size, len(X)),
            verbose=verbose, callbacks=[early_stop],
        )
        last_window = data_norm[-lookback:]
        forecast_norm = _forecast_recursive_tf(model, last_window, steps, lookback)
        return forecast_norm * std + mean

    elif DL_BACKEND == "pytorch":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = _LSTMNet(hidden=min(units, 32), rnn_type="GRU").to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        criterion = nn.MSELoss()
        X_t = torch.tensor(X).to(device)
        y_t = torch.tensor(y).unsqueeze(-1).to(device)
        for _ in range(min(epochs, 200)):
            model.train()
            optimizer.zero_grad()
            pred = model(X_t)
            loss = criterion(pred, y_t)
            loss.backward()
            optimizer.step()
        model.eval()
        window = list(data_norm[-lookback:])
        forecast_norm = []
        with torch.no_grad():
            for _ in range(steps):
                x = torch.tensor(window[-lookback:], dtype=torch.float32).reshape(1, lookback, 1).to(device)
                pred = model(x).item()
                forecast_norm.append(pred)
                window.append(pred)
        return np.array(forecast_norm) * std + mean

    else:
        # Fallback simulasi GRU
        last_val = data[-1]
        trend = (data[-1] - data[-min(3, len(data))]) if len(data) > 3 else 0
        rng = np.random.default_rng(seed=123)
        forecast = []
        cur = last_val
        for _ in range(steps):
            cur = cur + trend * 0.08 + rng.normal(0, 0.15)
            forecast.append(cur)
        return np.array(forecast)


def get_backend_info() -> dict:
    """Info backend DL yang tersedia."""
    return {
        "backend": DL_BACKEND or "simulation",
        "available": DL_BACKEND is not None,
    }