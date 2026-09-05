# Autonomous XAUUSD backtest report

Account: €10,000 start · 1% risk · 2% daily halt · +€1,000 daily target lock · 500× leverage.
Costs: $0.20 spread + $0.05 slip + $6/lot round-turn (IC Markets Raw-style conservative).
Winner press: size scales up only after the day is green (max 4×), so a first scalp can become a €1k–€4k burst without lifting the −2% halt.

## Summary

| strategy | timeframe | source | trades | win_rate_pct | profit_factor | net_pnl | equity_end | max_dd_pct | days | avg_day_pnl | median_day_pnl | best_day | worst_day | green_days | days_hit_1000 | days_halted | pct_days_hit_1000 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| breakout | m1_default | GC=F | 27 | 33.33 | 1.072 | 136.54 | 10136.54 | -13.73 | 7 | 19.51 | -216.3 | 1488.87 | -289.55 | 1 | 1 | 6 | 14.29 |
| mean_reversion | m1_default | GC=F | 30 | 36.67 | 0.909 | -214.61 | 9785.39 | -15.64 | 7 | -30.66 | -234.02 | 1034.07 | -291.19 | 1 | 1 | 6 | 14.29 |
| hybrid | m1_default | GC=F | 50 | 36.0 | 0.648 | -1430.36 | 8569.64 | -15.91 | 7 | -204.34 | -217.74 | -93.0 | -258.47 | 0 | 0 | 6 | 0.0 |
| confluence | m1_default | GC=F | 37 | 43.24 | 1.144 | 412.89 | 10412.89 | -9.31 | 7 | 58.98 | -204.46 | 1573.45 | -225.85 | 1 | 1 | 6 | 14.29 |
| breakout | m1_scalp_tight | GC=F | 35 | 45.71 | 1.105 | 321.4 | 10321.4 | -15.23 | 7 | 45.91 | -220.19 | 1349.81 | -255.34 | 2 | 1 | 6 | 14.29 |
| mean_reversion | m1_scalp_tight | GC=F | 29 | 51.72 | 1.794 | 1677.67 | 11677.67 | -9.53 | 7 | 239.67 | -230.74 | 1307.28 | -238.87 | 2 | 2 | 6 | 28.57 |
| hybrid | m1_scalp_tight | GC=F | 36 | 33.33 | 0.573 | -1329.1 | 8670.9 | -14.83 | 7 | -189.87 | -220.08 | 142.87 | -300.42 | 1 | 0 | 6 | 0.0 |
| confluence | m1_scalp_tight | GC=F | 28 | 53.57 | 1.62 | 1589.17 | 11589.17 | -9.28 | 7 | 227.02 | -223.77 | 1444.93 | -285.5 | 3 | 2 | 6 | 28.57 |
| breakout | m5_default | GC=F | 276 | 43.12 | 1.056 | 1598.55 | 11598.55 | -23.1 | 61 | 26.21 | -221.24 | 1626.42 | -332.25 | 10 | 7 | 40 | 11.48 |
| mean_reversion | m5_default | GC=F | 193 | 45.6 | 1.517 | 10502.38 | 20502.38 | -16.03 | 61 | 172.17 | -208.93 | 1965.69 | -386.88 | 16 | 14 | 50 | 22.95 |
| hybrid | m5_default | GC=F | 181 | 43.65 | 1.19 | 3500.14 | 13500.14 | -16.9 | 61 | 57.38 | -200.95 | 1664.18 | -473.63 | 15 | 7 | 38 | 11.48 |
| confluence | m5_default | GC=F | 177 | 40.68 | 0.902 | -1426.78 | 8573.22 | -31.22 | 61 | -23.39 | -45.84 | 1421.46 | -297.78 | 12 | 1 | 14 | 1.64 |
| breakout | m5_scalp_tight | GC=F | 278 | 46.04 | 1.242 | 7278.6 | 17278.6 | -17.4 | 61 | 119.32 | -215.53 | 1696.66 | -378.09 | 14 | 13 | 49 | 21.31 |
| mean_reversion | m5_scalp_tight | GC=F | 226 | 49.12 | 1.45 | 11245.58 | 21245.58 | -13.47 | 61 | 184.35 | -207.18 | 2068.61 | -396.8 | 18 | 15 | 51 | 24.59 |
| hybrid | m5_scalp_tight | GC=F | 251 | 43.82 | 1.045 | 1196.08 | 11196.08 | -30.88 | 61 | 19.61 | -214.42 | 1660.91 | -319.14 | 14 | 6 | 39 | 9.84 |
| confluence | m5_scalp_tight | GC=F | 239 | 42.26 | 0.934 | -1351.0 | 8649.0 | -33.74 | 61 | -22.15 | -149.02 | 1435.48 | -294.9 | 14 | 2 | 24 | 3.28 |
| breakout | h1_default | GC=F | 466 | 44.85 | 1.298 | 14161.03 | 24161.03 | -26.19 | 612 | 23.14 | 0.0 | 1850.2 | -753.67 | 122 | 10 | 52 | 1.63 |
| mean_reversion | h1_default | GC=F | 489 | 35.79 | 0.803 | -4601.19 | 5398.81 | -50.32 | 612 | -7.58 | 0.0 | 668.42 | -330.29 | 130 | 0 | 11 | 0.0 |
| hybrid | h1_default | GC=F | 544 | 47.43 | 1.401 | 40487.72 | 50487.72 | -20.35 | 612 | 66.16 | 0.0 | 3371.06 | -2067.59 | 174 | 40 | 258 | 6.54 |
| confluence | h1_default | GC=F | 23 | 39.13 | 0.976 | -29.77 | 9970.23 | -6.18 | 612 | -0.05 | 0.0 | 142.57 | -101.22 | 9 | 0 | 0 | 0.0 |

## How €1,000/day is modelled

- 1.00 lot XAUUSD = 100 oz → **$1 gold move = $100/lot**, **$10 move = $1,000/lot**.
- Your discretionary €3–4k bursts are the same math: a few dollars of gold × several lots at 500×.
- With a hard −€200 daily halt, a +€1,000 day needs **a win streak or size press after being green**, not two full losers first.
- This report counts how often the **+€1,000 lock** actually fired in history (`days_hit_1000`).

## Notes

- Daily target path: 1 lot × $10 gold move ≈ €1000. Press-winners scales size only after the day is green; -2% halt stays hard.

Yahoo/COMEX gold is a proxy for IC Markets XAUUSD (spread/hours differ). Demo API comes later.

## Walk-forward (see WALKFORWARD.md)

M5 65/35 split, cut 2026-08-11. **mean_reversion tight stayed profitable out-of-sample (PF 1.95, +€8.3k, 8 target days).** Hybrid tight failed OOS. Primary bot default is therefore mean-reversion tight.
