"""Download and cache gold / XAUUSD OHLC from public sources."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yfinance as yf

CACHE = Path(__file__).resolve().parent.parent / "data"
CACHE.mkdir(parents=True, exist_ok=True)

# Prefer spot-like ticker; fall back to COMEX gold futures.
TICKERS = ("GC=F", "XAUUSD=X")


def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [str(c[0]).lower() for c in df.columns]
    else:
        df.columns = [str(c).lower() for c in df.columns]
    rename = {
        "adj close": "close",
        "adj_close": "close",
    }
    df = df.rename(columns=rename)
    keep = [c for c in ("open", "high", "low", "close", "volume") if c in df.columns]
    return df[keep].dropna(subset=["open", "high", "low", "close"])


def fetch_ohlc(interval: str, period: str, ticker: str | None = None) -> tuple[pd.DataFrame, str]:
    last_err = None
    tried = [ticker] if ticker else list(TICKERS)
    for t in tried:
        if not t:
            continue
        path = CACHE / f"{t.replace('=', '_').replace('/', '_')}_{interval}_{period}.csv"
        try:
            raw = yf.download(
                t,
                interval=interval,
                period=period,
                auto_adjust=True,
                progress=False,
                threads=False,
            )
            if raw is None or raw.empty:
                raise RuntimeError(f"empty download {t} {interval} {period}")
            df = _flatten_columns(raw)
            if df.empty:
                raise RuntimeError("no OHLC after flatten")
            df.index = pd.to_datetime(df.index, utc=True)
            df = df[~df.index.duplicated(keep="last")].sort_index()
            df.to_csv(path)
            return df, t
        except Exception as exc:  # noqa: BLE001 — try next ticker
            last_err = exc
            if path.exists():
                cached = pd.read_csv(path, index_col=0, parse_dates=True)
                cached.index = pd.to_datetime(cached.index, utc=True)
                if not cached.empty:
                    return cached, f"{t}(cache)"
    raise RuntimeError(f"Could not fetch gold OHLC: {last_err}")


def load_all() -> dict[str, tuple[pd.DataFrame, str]]:
    """M1 (short), M5 (medium), H1 (long) — whatever Yahoo allows."""
    specs = (
        ("1m", "7d", "m1"),
        ("5m", "60d", "m5"),
        ("1h", "2y", "h1"),
    )
    out: dict[str, tuple[pd.DataFrame, str]] = {}
    for interval, period, key in specs:
        df, src = fetch_ohlc(interval, period)
        out[key] = (df, src)
    return out
