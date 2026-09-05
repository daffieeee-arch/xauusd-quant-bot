# Autonomous XAUUSD backtest report

Account: €10,000 start · 1% risk · 2% daily halt · +€1,000 daily target lock · 500× leverage.
Costs: $0.20 spread + $0.05 slip + $6/lot round-turn (IC Markets Raw-style conservative).
Winner press: size scales up only after the day is green (max 4×), so a first scalp can become a €1k–€4k burst without lifting the −2% halt.

## Summary

| strategy | timeframe | source | trades | win_rate_pct | profit_factor | net_pnl | equity_end | max_dd_pct | days | avg_day_pnl | median_day_pnl | best_day | worst_day | green_days | days_hit_1000 | days_halted | pct_days_hit_1000 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mean_reversion | m1_micro | GC=F | 799 | 46.43 | 1.027 | 263.45 | 10263.45 | -8.54 | 7 | 37.64 | -201.31 | 1011.62 | -211.73 | 2 | 1 | 5 | 14.29 |
| breakout | m1_micro | GC=F | 643 | 43.08 | 0.873 | -856.51 | 9143.49 | -10.0 | 7 | -122.36 | -144.73 | 19.95 | -210.52 | 2 | 0 | 3 | 0.0 |
| confluence | m1_micro | GC=F | 279 | 37.28 | 0.68 | -935.65 | 9064.35 | -10.42 | 7 | -133.66 | -157.87 | 19.95 | -206.1 | 1 | 0 | 2 | 0.0 |
| mean_reversion | m5_micro | GC=F | 2149 | 51.98 | 1.46 | 24598.96 | 34598.96 | -4.66 | 61 | 403.26 | 210.89 | 1175.37 | -245.31 | 40 | 19 | 32 | 31.15 |
| breakout | m5_micro | GC=F | 1167 | 42.84 | 1.013 | 141.7 | 10141.7 | -6.12 | 61 | 2.26 | -14.18 | 251.94 | -138.87 | 20 | 0 | 0 | 0.0 |
| confluence | m5_micro | GC=F | 427 | 41.45 | 0.929 | -272.09 | 9727.91 | -4.6 | 61 | -4.46 | 0.0 | 102.11 | -102.15 | 23 | 0 | 0 | 0.0 |

## How €1,000/day is modelled

- 1.00 lot XAUUSD = 100 oz → **$1 gold move = $100/lot**, **$10 move = $1,000/lot**.
- Your discretionary €3–4k bursts are the same math: a few dollars of gold × several lots at 500×.
- With a hard −€200 daily halt, a +€1,000 day needs **a win streak or size press after being green**, not two full losers first.
- This report counts how often the **+€1,000 lock** actually fired in history (`days_hit_1000`).

## Notes

- Daily target path: 1 lot × $10 gold move ≈ €1000. Press-winners scales size only after the day is green; -2% halt stays hard.

Yahoo/COMEX gold is a proxy for IC Markets XAUUSD (spread/hours differ). Demo API comes later.
