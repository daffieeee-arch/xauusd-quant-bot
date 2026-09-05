"""Bar indicators used by the three strategies."""

from __future__ import annotations

import numpy as np
import pandas as pd


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    prev = close.shift(1)
    tr = pd.concat(
        [(high - low), (high - prev).abs(), (low - prev).abs()],
        axis=1,
    ).max(axis=1)
    return tr.ewm(span=period, adjust=False).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def session_vwap(df: pd.DataFrame) -> pd.Series:
    typical = (df["high"] + df["low"] + df["close"]) / 3.0
    vol = df["volume"].clip(lower=1.0)
    day = df.index.tz_convert("UTC").date
    num = (typical * vol).groupby(day).cumsum()
    den = vol.groupby(day).cumsum()
    return num / den


def rolling_prior_high(df: pd.DataFrame, lookback: int) -> pd.Series:
    return df["high"].shift(2).rolling(lookback).max()


def rolling_prior_low(df: pd.DataFrame, lookback: int) -> pd.Series:
    return df["low"].shift(2).rolling(lookback).min()


def utc_hour(index: pd.DatetimeIndex) -> np.ndarray:
    return index.tz_convert("UTC").hour.to_numpy()


def in_session(index: pd.DatetimeIndex, mode: str) -> np.ndarray:
    hour = utc_hour(index)
    if mode == "all":
        return np.ones(len(index), dtype=bool)
    if mode == "london":
        return (hour >= 7) & (hour < 16)
    if mode == "ny":
        return (hour >= 12) & (hour < 21)
    if mode == "overlap":
        return (hour >= 12) & (hour < 16)
    if mode == "london_ny_skip_open":
        return (hour >= 8) & (hour < 21)
    # london_ny
    return (hour >= 7) & (hour < 21)


def adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    up = high.diff()
    down = -low.diff()
    plus_dm = np.where((up > down) & (up > 0), up, 0.0)
    minus_dm = np.where((down > up) & (down > 0), down, 0.0)
    tr = atr(df, period)
    plus_di = 100 * pd.Series(plus_dm, index=df.index).ewm(span=period, adjust=False).mean() / tr.replace(0, np.nan)
    minus_di = 100 * pd.Series(minus_dm, index=df.index).ewm(span=period, adjust=False).mean() / tr.replace(0, np.nan)
    dx = (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan) * 100
    return dx.ewm(span=period, adjust=False).mean()


def atr_ratio(atr_s: pd.Series, lookback: int = 48) -> pd.Series:
    mid = atr_s.rolling(lookback, min_periods=max(10, lookback // 3)).mean()
    return atr_s / mid.replace(0, np.nan)
