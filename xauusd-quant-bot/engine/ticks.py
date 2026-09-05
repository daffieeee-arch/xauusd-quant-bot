"""Decode cTrader tick payloads and build second / minute bars."""

from __future__ import annotations

import pandas as pd


def decode_relative_ticks(tick_data, digits: int = 2) -> pd.DataFrame:
    """cTrader sends newest-first: first timestamp absolute ms, later ones deltas."""
    if not tick_data:
        return pd.DataFrame(columns=["time", "price"])
    rows = []
    t = None
    px = None
    for item in tick_data:
        ts = int(item.timestamp)
        tick = int(item.tick)
        if t is None:
            t = ts
            px = tick
        else:
            t = t + ts
            px = px + tick
        rows.append((t, px / 100_000.0))
    df = pd.DataFrame(rows, columns=["time_ms", "price"])
    df["time"] = pd.to_datetime(df["time_ms"], unit="ms", utc=True)
    df["price"] = df["price"].round(digits)
    return df.sort_values("time").drop(columns=["time_ms"]).reset_index(drop=True)


def merge_bid_ask(bid: pd.DataFrame, ask: pd.DataFrame) -> pd.DataFrame:
    b = bid.rename(columns={"price": "bid"}).set_index("time")
    a = ask.rename(columns={"price": "ask"}).set_index("time")
    out = b.join(a, how="outer").sort_index()
    out["bid"] = out["bid"].ffill()
    out["ask"] = out["ask"].ffill()
    return out.dropna()


def to_bars(quotes: pd.DataFrame, rule: str = "5s") -> pd.DataFrame:
    mid = (quotes["bid"] + quotes["ask"]) / 2.0
    g = mid.resample(rule)
    bars = pd.DataFrame(
        {
            "open": g.first(),
            "high": g.max(),
            "low": g.min(),
            "close": g.last(),
            "volume": g.count(),
            "spread": quotes["ask"].resample(rule).last() - quotes["bid"].resample(rule).last(),
        }
    ).dropna()
    return bars


def synthetic_quotes_from_ohlc(ohlc: pd.DataFrame, spread: float = 0.20) -> pd.DataFrame:
    """Bridge until IC ticks arrive: 4 quotes per bar (OHLC path)."""
    rows = []
    for ts, row in ohlc.iterrows():
        path = [row["open"], row["high"], row["low"], row["close"]]
        for i, px in enumerate(path):
            t = ts + pd.Timedelta(milliseconds=i * 50)
            rows.append((t, px - spread / 2.0, px + spread / 2.0))
    df = pd.DataFrame(rows, columns=["time", "bid", "ask"]).set_index("time")
    return df
