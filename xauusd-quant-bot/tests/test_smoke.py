"""Offline smoke tests — no broker / Yahoo required."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from engine.backtest import run_backtest
from engine.config import AccountSpec, ContractSpec, StrategyParams
from engine.indicators import adx, atr, ema, in_session, session_vwap
from engine.strategies import SIGNALS, enrich


def _synthetic_ohlc(n: int = 400) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    idx = pd.date_range("2026-06-01", periods=n, freq="5min", tz="UTC")
    close = 4000 + np.sin(np.linspace(0, 20, n)) * 12 + rng.normal(0, 0.4, n)
    high = close + rng.uniform(0.2, 1.5, n)
    low = close - rng.uniform(0.2, 1.5, n)
    open_ = close + rng.normal(0, 0.3, n)
    vol = rng.integers(50, 500, n)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": vol},
        index=idx,
    )


def test_indicators_finite():
    df = _synthetic_ohlc()
    a = atr(df, 14)
    e = ema(df["close"], 21)
    v = session_vwap(df)
    d = adx(df, 14)
    assert a.dropna().gt(0).all()
    assert e.notna().sum() > 100
    assert v.notna().sum() > 100
    assert d.dropna().between(0, 100).all()


def test_session_skip_open():
    idx = pd.date_range("2026-06-02 06:00", periods=5, freq="1h", tz="UTC")
    mask = in_session(idx, "london_ny_skip_open")
    assert list(mask) == [False, False, True, True, True]


@pytest.mark.parametrize("name", list(SIGNALS))
def test_signals_enrich_no_crash(name):
    df = _synthetic_ohlc()
    p = StrategyParams(sl_atr=0.8, tp_atr=1.2, vwap_dev_atr=1.1, min_atr=0.05)
    enriched = enrich(df, p)
    fn = SIGNALS[name]
    i = 80
    sig = fn(enriched.iloc[i], enriched.iloc[i - 1], p)
    assert sig in (-1, 0, 1)


def test_backtest_runs_offline():
    df = _synthetic_ohlc(500)
    res = run_backtest(
        df,
        strategy="mean_reversion",
        timeframe="m5_synth",
        source="synthetic",
        account=AccountSpec(risk_pct=0.5, max_trades_per_day=80),
        contract=ContractSpec(),
        params=StrategyParams(sl_atr=0.8, tp_atr=1.2, vwap_dev_atr=1.0, min_atr=0.05),
    )
    assert res.equity_end > 0
    assert res.n >= 0
