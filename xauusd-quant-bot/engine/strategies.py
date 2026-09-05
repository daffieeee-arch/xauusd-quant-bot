"""Signal generation: breakout, mean-reversion, hybrid, confluence."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import StrategyParams
from . import indicators as ind


def enrich(df: pd.DataFrame, p: StrategyParams) -> pd.DataFrame:
    out = df.copy()
    out["atr"] = ind.atr(out, p.atr_period)
    out["ema"] = ind.ema(out["close"], p.ema_period)
    out["ema_fast"] = ind.ema(out["close"], p.ema_fast)
    out["ema_slow"] = ind.ema(out["close"], p.ema_slow)
    out["vwap"] = ind.session_vwap(out)
    out["prior_high"] = ind.rolling_prior_high(out, p.breakout_lookback)
    out["prior_low"] = ind.rolling_prior_low(out, p.breakout_lookback)
    out["in_sess"] = ind.in_session(out.index, p.session)
    out["adx"] = ind.adx(out, p.atr_period)
    out["atr_ratio"] = ind.atr_ratio(out["atr"], 48)
    return out


def _bar_ok(row: pd.Series, p: StrategyParams) -> bool:
    if not bool(row["in_sess"]):
        return False
    atr = float(row["atr"])
    return np.isfinite(atr) and atr >= p.min_atr


def signal_breakout(row: pd.Series, prev: pd.Series, p: StrategyParams) -> int:
    if not _bar_ok(row, p):
        return 0
    atr = float(row["atr"])
    buf = atr * p.breakout_buffer_atr
    close, open_ = float(row["close"]), float(row["open"])
    hi, lo = float(row["prior_high"]), float(row["prior_low"])
    if not np.isfinite(hi) or not np.isfinite(lo):
        return 0
    if close > hi + buf and close > open_:
        return 1
    if close < lo - buf and close < open_:
        return -1
    return 0


def _is_range_regime(row: pd.Series, p: StrategyParams) -> bool:
    if not p.range_only:
        return True
    ratio = float(row.get("atr_ratio", np.nan))
    adx_v = float(row.get("adx", np.nan))
    if np.isfinite(ratio) and ratio > p.max_atr_ratio:
        return False
    if np.isfinite(adx_v) and adx_v > p.max_adx:
        return False
    return True


def signal_mean_reversion(row: pd.Series, prev: pd.Series, p: StrategyParams) -> int:
    if not _bar_ok(row, p) or not _is_range_regime(row, p):
        return 0
    vwap = float(row["vwap"])
    ema = float(row["ema"])
    close = float(row["close"])
    atr = float(row["atr"])
    if not np.isfinite(vwap) or not np.isfinite(ema) or vwap <= 0:
        return 0
    dev = close - vwap
    thr = atr * p.vwap_dev_atr
    if dev >= thr and close > ema * 0.998:
        return -1
    if dev <= -thr and close < ema * 1.002:
        return 1
    return 0


def signal_hybrid(row: pd.Series, prev: pd.Series, p: StrategyParams) -> int:
    if not _bar_ok(row, p):
        return 0
    vwap = float(row["vwap"])
    close = float(row["close"])
    prev_close = float(prev["close"])
    f1, s1 = float(row["ema_fast"]), float(row["ema_slow"])
    f0, s0 = float(prev["ema_fast"]), float(prev["ema_slow"])
    atr = float(row["atr"])
    if not all(np.isfinite(x) for x in (f1, s1, f0, s0, close, prev_close)):
        return 0
    near = (not np.isfinite(vwap)) or vwap <= 0 or abs(close - vwap) <= atr * 0.8
    bull_cross = f0 <= s0 and f1 > s1
    bear_cross = f0 >= s0 and f1 < s1
    bull = f1 > s1 and close > prev_close and near
    bear = f1 < s1 and close < prev_close and near
    if bull_cross or bull:
        return 1
    if bear_cross or bear:
        return -1
    return 0


SIGNALS = {
    "breakout": signal_breakout,
    "mean_reversion": signal_mean_reversion,
    "hybrid": signal_hybrid,
}


def signal_confluence(row: pd.Series, prev: pd.Series, p: StrategyParams) -> int:
    votes = [
        signal_breakout(row, prev, p),
        signal_mean_reversion(row, prev, p),
        signal_hybrid(row, prev, p),
    ]
    score = sum(votes)
    if score >= 2:
        return 1
    if score <= -2:
        return -1
    return 0


SIGNALS["confluence"] = signal_confluence
