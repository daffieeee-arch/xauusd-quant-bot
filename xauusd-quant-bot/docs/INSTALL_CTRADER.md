# Install & test on IC Markets demo (cTrader)

## Prerequisites

1. IC Markets **cTrader** demo (prefer **Raw Spread** for scalping).
2. cTrader **Desktop** (Windows/Mac) with Algo enabled.
3. Symbol: usually `XAUUSD` (confirm exact name in Market Watch).
4. Chart timeframe for the bot instance: **M1** (recommended) or **M5**.

## Install the cBot

1. Open cTrader → **Algo**.
2. New cBot → C# → replace template with  
   `src/cBots/XauUsdQuantBot.cs`
3. Build (compile). Fix any API version warnings if your cTrader build differs slightly.
4. Attach to **XAUUSD** chart on demo.
5. Set parameters:
   - `StrategyMode`: `Breakout`, `MeanReversion`, `Hybrid`, or `RotateAll`
   - `RiskPercent`: `1`
   - `MaxDailyLossPercent`: `2`
   - `UseDomFilter`: `true` on demo forward-test; `false` for pure OHLC backtests

## Backtest protocol (do this before trusting demo P&L)

For **each** of Breakout / MeanReversion / Hybrid:

1. Symbol: XAUUSD, TF: M1  
2. Period: at least 3–6 months; then a separate out-of-sample month  
3. Commission: match your Raw Spread account (often ~$6 round-turn / lot — confirm in account specs)  
4. Spread: use **historical** or conservative fixed spread for gold  
5. Record: net P&L, profit factor, max equity DD, #trades, win rate, avg R  

Winner selection:

- Prefer highest **profit factor** with DD under your comfort (e.g. <15%) and ≥30 trades in sample.
- Then run **RotateAll** only if single strategies are individually positive (rotation is for diversification, not magic).

## Demo forward-test

1. Enable `UseDomFilter = true`.
2. Run during London + New York overlap first (`SessionFilter = LondonNY`).
3. Log every trade reason from the bot print output for 2 weeks.
4. Do **not** raise risk above 1% / 2% daily until metrics are stable.
