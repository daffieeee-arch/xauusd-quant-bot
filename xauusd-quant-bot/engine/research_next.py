#!/usr/bin/env python3
"""Hunt a stabler edge: hour buckets, range-regime filter, session cuts, cost stress."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.backtest import run_backtest
from engine.config import AccountSpec, ContractSpec, StrategyParams
from engine.data import fetch_ohlc
from engine.report import summarize


def hour_table(trades_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(trades_csv, parse_dates=["entry_time"])
    df["hour"] = pd.to_datetime(df["entry_time"], utc=True).dt.hour
    g = df.groupby("hour").agg(
        trades=("pnl", "count"),
        winrate=("pnl", lambda s: (s > 0).mean() * 100),
        net=("pnl", "sum"),
        avg=("pnl", "mean"),
    )
    return g.round(2)


def run_variant(df, name, params, account, contract, src, tf="m5"):
    res = run_backtest(df, "mean_reversion", f"{tf}_{name}", src, account, contract, params)
    s = summarize(res)
    s["variant"] = name
    print(
        f"{name:22} n={s['trades']:4} WR={s['win_rate_pct']:5} PF={s['profit_factor']:6} "
        f"net={s['net_pnl']:9} avg_day={s['avg_day_pnl']:8} hit1000={s['days_hit_1000']:2} "
        f"DD={s['max_dd_pct']}",
        flush=True,
    )
    return s, res


def split(df, frac=0.65):
    days = sorted(set(df.index.tz_convert("UTC").date))
    cut = days[int(len(days) * frac)]
    return df[df.index.tz_convert("UTC").date < cut], df[df.index.tz_convert("UTC").date >= cut], cut


def main() -> int:
    out = ROOT / "reports" / "next"
    out.mkdir(parents=True, exist_ok=True)

    trades = ROOT / "reports" / "trades_mean_reversion_m5_scalp_tight.csv"
    if trades.exists():
        hours = hour_table(trades)
        hours.to_csv(out / "hours_baseline_mr_tight.csv")
        print("Hour buckets (baseline M5 MR tight):\n", hours.to_string(), flush=True)

    raw, src = fetch_ohlc("5m", "60d")
    account = AccountSpec()
    tight = dict(sl_atr=0.8, tp_atr=1.2, vwap_dev_atr=1.1, min_atr=0.10, press_winners=True)

    variants = [
        ("baseline_tight", StrategyParams(**tight)),
        ("skip_london_open", StrategyParams(**tight, session="london_ny_skip_open")),
        ("overlap_only", StrategyParams(**tight, session="overlap")),
        ("ny_only", StrategyParams(**tight, session="ny")),
        ("range_filter", StrategyParams(**tight, range_only=True)),
        ("range_skip_open", StrategyParams(**tight, range_only=True, session="london_ny_skip_open")),
        ("range_overlap", StrategyParams(**tight, range_only=True, session="overlap")),
    ]

    rows = []
    results = {}
    print("\n=== Variants (M5, €10k, 1%/2%, €1k lock) ===", flush=True)
    for name, params in variants:
        s, res = run_variant(raw, name, params, account, ContractSpec(), src)
        rows.append(s)
        results[name] = res

    print("\n=== Cost stress on range_skip_open (wider IC-like spread) ===", flush=True)
    fat = ContractSpec(spread_price=0.35, slippage_price=0.08, commission_per_lot_rt=6.0)
    s, _ = run_variant(
        raw,
        "range_skip_open_fat",
        StrategyParams(**tight, range_only=True, session="london_ny_skip_open"),
        account,
        fat,
        src,
    )
    rows.append(s)

    print("\n=== Walk-forward skip_london_open and baseline ===", flush=True)
    ins, oos, cut = split(raw)
    print(f"cut={cut}", flush=True)
    for tag, par in (
        ("baseline_tight", StrategyParams(**tight)),
        ("skip_london_open", StrategyParams(**tight, session="london_ny_skip_open")),
        ("range_skip_open", StrategyParams(**tight, range_only=True, session="london_ny_skip_open")),
    ):
        for label, part in (("IS", ins), ("OOS", oos)):
            s, _ = run_variant(part, f"{tag}_{label}", par, account, ContractSpec(), src)
            rows.append(s)

    table = pd.DataFrame(rows)
    table.to_csv(out / "variants.csv", index=False)

    # Pick best by OOS-friendly rule: prefer range_skip_open if OOS PF>=1.2 else baseline
    md = [
        "# Next-edge research",
        "",
        "Doel: mean-reversion **stabieler** maken (minder trend-dagen, minder London-open rotzooi),",
        "niet nóg een derde signaal erbij (hybrid zakte al OOS).",
        "",
        "## Wat we testten",
        "",
        "1. Uur-buckets op de bestaande M5 MR-tight trades",
        "2. London-open skip (07–08 UTC)",
        "3. Alleen London/NY-overlap (12–16 UTC)",
        "4. Range-regime: geen fade als ATR explodes of ADX hoog is",
        "5. Dikkere spread ($0.35+$0.08) — IC-realiteitstest",
        "6. Walk-forward van de beste combinatie",
        "",
        "## Varianten",
        "",
        table[
            [
                "variant",
                "trades",
                "win_rate_pct",
                "profit_factor",
                "net_pnl",
                "avg_day_pnl",
                "days_hit_1000",
                "max_dd_pct",
            ]
        ].to_string(index=False),
        "",
        f"Walk-forward cut: **{cut}**.",
        "",
        "## Wat dit betekent tot IC-ticks er zijn",
        "",
        "- Als range+skip-open OOS blijft ≥1.2 PF: dat wordt de nieuwe cBot-default.",
        "- Als fat-spread de PF onder 1.1 duwt: we hebben echte IC-ticks nodig voordat we size pressen.",
        "- Hybrid/confluence blijven uit tot ticks dat weerleggen.",
        "",
    ]
    (out / "NEXT.md").write_text("\n".join(md), encoding="utf-8")
    print(f"\nWrote {out / 'NEXT.md'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
