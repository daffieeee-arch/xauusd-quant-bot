"""Equity curve for the leading M5 mean-reversion tight setup."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from engine.backtest import run_backtest
from engine.config import AccountSpec, StrategyParams
from engine.data import fetch_ohlc


def main() -> int:
    df, src = fetch_ohlc("5m", "60d")
    params = StrategyParams(sl_atr=0.8, tp_atr=1.2, vwap_dev_atr=1.1, min_atr=0.10)
    res = run_backtest(df, "mean_reversion", "m5", src, AccountSpec(), params=params)
    out = ROOT / "reports"
    out.mkdir(exist_ok=True)

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=False)
    if not res.equity_curve.empty:
        axes[0].plot(res.equity_curve.index, res.equity_curve.values, color="#1f6feb", lw=1.2)
    axes[0].axhline(10_000, color="#888", ls="--", lw=0.8)
    axes[0].set_title("Equity — M5 mean-reversion tight (press winners, €1k lock / −2% halt)")
    axes[0].set_ylabel("Equity")
    axes[0].grid(True, alpha=0.3)

    if not res.daily.empty:
        colors = ["#2da44e" if v >= 0 else "#cf222e" for v in res.daily["pnl"]]
        axes[1].bar(range(len(res.daily)), res.daily["pnl"], color=colors, width=0.9)
        axes[1].axhline(1000, color="#2da44e", ls="--", lw=0.8, label="€1000 target")
        axes[1].axhline(-200, color="#cf222e", ls="--", lw=0.8, label="−€200 halt")
        axes[1].legend(loc="upper right", fontsize=8)
    axes[1].set_title("Daily P&L")
    axes[1].set_ylabel("EUR")
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    path = out / "equity_m5_mean_reversion_tight.png"
    fig.savefig(path, dpi=120)
    print(f"Wrote {path}  net={res.net:.0f} target_days={res.target_days}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
