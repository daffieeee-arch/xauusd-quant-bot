# Strategy backtest scorecard

Fill one row per run. Compare Breakout / MeanReversion / Hybrid before enabling RotateAll.

| Run ID | Strategy | TF | Period (in/OOS) | Commission | Spread model | Trades | Win% | Profit factor | Net P&L | Max DD% | Avg R | Notes |
|--------|----------|----|-----------------|------------|--------------|--------|------|---------------|---------|---------|-------|-------|
| 1 | Breakout | M1 | | | | | | | | | | |
| 2 | MeanReversion | M1 | | | | | | | | | | |
| 3 | Hybrid | M1 | | | | | | | | | | |
| 4 | Best + DOM demo | M1 | forward 2w | live | live | | | | | | | DOM on |

## Pass criteria (demo promotion)

- Profit factor ≥ 1.2 on in-sample **and** positive on out-of-sample month
- Max equity drawdown within comfort (suggested < 15%)
- ≥ 30 trades in sample (avoid curve-fit on noise)
- Demo 2 weeks: no broken risk halt; daily loss 2% respected
- Only then consider tiny live size (still 1% / 2%)

## Parameter notes

Default risk: **1%** per trade, **2%** max daily loss, account start **€10,000**.

Do not tune toward €1000/day on €10k — that fights the daily loss halt. Tune for expectancy; scale equity later.
