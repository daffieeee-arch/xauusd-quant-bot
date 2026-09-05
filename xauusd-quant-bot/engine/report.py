"""Write markdown + CSV reports from backtest results."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .backtest import BacktestResult


def summarize(r: BacktestResult) -> dict:
    daily = r.daily
    avg_day = float(daily["pnl"].mean()) if len(daily) else 0.0
    med_day = float(daily["pnl"].median()) if len(daily) else 0.0
    best_day = float(daily["pnl"].max()) if len(daily) else 0.0
    worst_day = float(daily["pnl"].min()) if len(daily) else 0.0
    pos_days = int((daily["pnl"] > 0).sum()) if len(daily) else 0
    n_days = int(len(daily))
    return {
        "strategy": r.strategy,
        "timeframe": r.timeframe,
        "source": r.source,
        "trades": r.n,
        "win_rate_pct": round(r.win_rate * 100, 2),
        "profit_factor": round(r.profit_factor, 3) if r.profit_factor != float("inf") else "inf",
        "net_pnl": round(r.net, 2),
        "equity_end": round(r.equity_end, 2),
        "max_dd_pct": round(r.max_dd_pct, 2),
        "days": n_days,
        "avg_day_pnl": round(avg_day, 2),
        "median_day_pnl": round(med_day, 2),
        "best_day": round(best_day, 2),
        "worst_day": round(worst_day, 2),
        "green_days": pos_days,
        "days_hit_1000": r.target_days,
        "days_halted": r.halt_days,
        "pct_days_hit_1000": round(100.0 * r.target_days / n_days, 2) if n_days else 0.0,
    }


def _md_table(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    header = "| " + " | ".join(cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    body = []
    for _, row in df.iterrows():
        body.append("| " + " | ".join(str(row[c]) for c in df.columns) + " |")
    return "\n".join([header, sep, *body])


def write_reports(results: list[BacktestResult], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = [summarize(r) for r in results]
    table = pd.DataFrame(rows)
    csv_path = out_dir / "summary.csv"
    table.to_csv(csv_path, index=False)

    # Per-result trade logs
    for r in results:
        slug = f"{r.strategy}_{r.timeframe}"
        if r.trades:
            pd.DataFrame(
                [
                    {
                        "entry_time": t.entry_time,
                        "exit_time": t.exit_time,
                        "side": "buy" if t.side == 1 else "sell",
                        "entry": t.entry,
                        "exit": t.exit,
                        "lots": t.lots,
                        "pnl": t.pnl,
                        "reason": t.reason,
                    }
                    for t in r.trades
                ]
            ).to_csv(out_dir / f"trades_{slug}.csv", index=False)
        if not r.daily.empty:
            r.daily.to_csv(out_dir / f"daily_{slug}.csv", index=False)

    md = out_dir / "REPORT.md"
    md.write_text(_markdown(table, results), encoding="utf-8")
    return md


def _markdown(table: pd.DataFrame, results: list[BacktestResult]) -> str:
    lines = [
        "# Autonomous XAUUSD backtest report",
        "",
        "Account: €10,000 start · 1% risk · 2% daily halt · +€1,000 daily target lock · 500× leverage.",
        "Costs: $0.20 spread + $0.05 slip + $6/lot round-turn (IC Markets Raw-style conservative).",
        "Winner press: size scales up only after the day is green (max 4×), so a first scalp can become a €1k–€4k burst without lifting the −2% halt.",
        "",
        "## Summary",
        "",
        _md_table(table),
        "",
        "## How €1,000/day is modelled",
        "",
        "- 1.00 lot XAUUSD = 100 oz → **$1 gold move = $100/lot**, **$10 move = $1,000/lot**.",
        "- Your discretionary €3–4k bursts are the same math: a few dollars of gold × several lots at 500×.",
        "- With a hard −€200 daily halt, a +€1,000 day needs **a win streak or size press after being green**, not two full losers first.",
        "- This report counts how often the **+€1,000 lock** actually fired in history (`days_hit_1000`).",
        "",
        "## Notes",
        "",
    ]
    seen = set()
    for r in results:
        for n in r.notes:
            if n not in seen:
                seen.add(n)
                lines.append(f"- {n}")
    lines.append("")
    lines.append("Yahoo/COMEX gold is a proxy for IC Markets XAUUSD (spread/hours differ). Demo API comes later.")
    lines.append("")
    return "\n".join(lines)
