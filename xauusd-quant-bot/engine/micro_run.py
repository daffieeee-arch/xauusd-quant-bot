#!/usr/bin/env python3
"""Hundreds-of-scalps mode: tiny risk so the -2% halt allows many trades."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.backtest import run_backtest
from engine.config import AccountSpec, StrategyParams
from engine.data import fetch_ohlc
from engine.report import summarize, write_reports


def main() -> int:
    account = AccountSpec(
        risk_pct=0.15,
        max_trades_per_day=200,
        cooldown_bars_after_loss=1,
    )
    params = StrategyParams(
        sl_atr=0.6,
        tp_atr=0.9,
        min_atr=0.08,
        breakout_lookback=8,
        vwap_dev_atr=0.9,
        press_winners=True,
        press_max_mult=3.0,
    )
    results = []
    for interval, period, tf in (("1m", "7d", "m1"), ("5m", "60d", "m5")):
        df, src = fetch_ohlc(interval, period)
        print(f"{tf}: {len(df)} bars {src}", flush=True)
        for strat in ("mean_reversion", "breakout", "confluence"):
            res = run_backtest(df, strat, f"{tf}_micro", src, account=account, params=params)
            s = summarize(res)
            print(
                f"  {strat:16} trades={s['trades']:4} WR={s['win_rate_pct']} "
                f"PF={s['profit_factor']} net={s['net_pnl']} "
                f"avg_day={s['avg_day_pnl']} hit1000={s['days_hit_1000']}",
                flush=True,
            )
            results.append(res)
    out = ROOT / "reports" / "micro"
    write_reports(results, out)
    print(f"Wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
