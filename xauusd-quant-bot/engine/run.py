#!/usr/bin/env python3
"""Fetch gold data, run all strategies, write reports. No UI required."""

from __future__ import annotations

import sys
from pathlib import Path

# Allow `python -m engine.run` from repo or `python engine/run.py`
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.backtest import run_backtest
from engine.config import STRATEGIES, AccountSpec, StrategyParams
from engine.data import load_all
from engine.report import write_reports


def main() -> int:
    print("Fetching gold OHLC (Yahoo: GC=F / XAUUSD=X)…", flush=True)
    datasets = load_all()
    for tf, (df, src) in datasets.items():
        print(f"  {tf}: {len(df)} bars  {df.index.min()} → {df.index.max()}  src={src}", flush=True)

    results = []
    # Baseline + a slightly tighter scalp set aimed at more daily-target hits on M1/M5.
    param_sets = [
        ("default", StrategyParams()),
        (
            "scalp_tight",
            StrategyParams(
                sl_atr=0.8,
                tp_atr=1.2,
                min_atr=0.10,
                breakout_lookback=12,
                vwap_dev_atr=1.1,
                press_winners=True,
                press_max_mult=4.0,
            ),
        ),
    ]

    for tf, (df, src) in datasets.items():
        if len(df) < 80:
            print(f"Skip {tf}: too few bars", flush=True)
            continue
        for name, params in param_sets:
            # Tight scalp is only meaningful on fast TFs
            if name == "scalp_tight" and tf == "h1":
                continue
            for strat in STRATEGIES:
                print(f"Backtest {strat}/{tf}/{name}…", flush=True)
                res = run_backtest(
                    df,
                    strategy=strat,
                    timeframe=f"{tf}_{name}",
                    source=src,
                    account=AccountSpec(),
                    params=params,
                )
                print(
                    f"    trades={res.n} net={res.net:.0f} WR={res.win_rate*100:.1f}% "
                    f"PF={res.profit_factor:.2f} target_days={res.target_days} "
                    f"DD={res.max_dd_pct:.1f}%",
                    flush=True,
                )
                results.append(res)

    out = ROOT / "reports"
    md = write_reports(results, out)
    print(f"\nWrote {md}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
