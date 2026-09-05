#!/usr/bin/env python3
"""In-sample / out-of-sample split for the leading M5 setups."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.backtest import run_backtest
from engine.config import AccountSpec, StrategyParams
from engine.data import fetch_ohlc
from engine.report import summarize


def split_by_days(df, is_frac: float = 0.65):
    days = sorted(set(df.index.tz_convert("UTC").date))
    cut = days[int(len(days) * is_frac)]
    ins = df[df.index.tz_convert("UTC").date < cut]
    oos = df[df.index.tz_convert("UTC").date >= cut]
    return ins, oos, cut


def main() -> int:
    df, src = fetch_ohlc("5m", "60d")
    ins, oos, cut = split_by_days(df, 0.65)
    print(f"Source={src}  IS {ins.index.min()}→{ins.index.max()}  OOS {oos.index.min()}→{oos.index.max()}  cut={cut}")

    setups = [
        ("mean_reversion", StrategyParams(sl_atr=0.8, tp_atr=1.2, vwap_dev_atr=1.1, min_atr=0.10)),
        ("breakout", StrategyParams(sl_atr=0.8, tp_atr=1.2, breakout_lookback=12, min_atr=0.10)),
        ("hybrid", StrategyParams(sl_atr=0.8, tp_atr=1.2, min_atr=0.10)),
        ("mean_reversion", StrategyParams()),
    ]

    lines = [
        "# Walk-forward (M5, 65% in-sample / 35% out-of-sample)",
        "",
        f"Data: {src}  cut date **{cut}**.",
        "",
        "| setup | split | trades | win% | PF | net | avg day | days_hit_1000 | max DD% |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for i, (name, params) in enumerate(setups, 1):
        for label, part in (("IS", ins), ("OOS", oos)):
            res = run_backtest(
                part,
                strategy=name,
                timeframe=f"m5_wf_{label.lower()}_{i}",
                source=src,
                account=AccountSpec(),
                params=params,
            )
            s = summarize(res)
            tag = f"{name} {'tight' if params.sl_atr < 1.0 else 'default'}"
            lines.append(
                f"| {tag} | {label} | {s['trades']} | {s['win_rate_pct']} | {s['profit_factor']} | "
                f"{s['net_pnl']} | {s['avg_day_pnl']} | {s['days_hit_1000']} | {s['max_dd_pct']} |"
            )
            print(f"{tag:28} {label:3} trades={res.n:4} PF={res.profit_factor:.2f} net={res.net:.0f} target_days={res.target_days}")

    out = ROOT / "reports" / "WALKFORWARD.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
