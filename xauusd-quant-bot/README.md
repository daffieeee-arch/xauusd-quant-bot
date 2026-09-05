# XAUUSD Quant Bot (cTrader / IC Markets)

Demo-first multi-strategy scalper for **XAUUSD** as a **cTrader cBot** (C#).

## What you get

| Piece | Path |
|-------|------|
| Main cBot (3 strategies + rotate) | [`src/cBots/XauUsdQuantBot.cs`](src/cBots/XauUsdQuantBot.cs) |
| DOM imbalance indicator (live L2) | [`src/indicators/DomImbalance.cs`](src/indicators/DomImbalance.cs) |
| Data / Level II research | [`docs/DATA_AND_EDGE.md`](docs/DATA_AND_EDGE.md) |
| Install & test steps | [`docs/INSTALL_CTRADER.md`](docs/INSTALL_CTRADER.md) |
| Backtest scorecard | [`backtest/SCORECARD.md`](backtest/SCORECARD.md) |

## Strategies

1. **Breakout** — prior-range break with ATR buffer  
2. **MeanReversion** — fade session VWAP stretch (EMA soft filter)  
3. **Hybrid** — EMA cross / pullback near VWAP + volatility gate  
4. **RotateAll** — first valid signal among the three (use only after singles look OK)

Shared: London/NY session filter, spread cap, ATR stop/target, **1% risk**, **2% daily loss halt**, optional **Level II DOM imbalance** filter.

## Research summary (IC Markets data)

- cTrader Raw Spread exposes **Level II Market Depth** (aggregated LP liquidity), not true exchange Level III.
- DOM is usable **live/demo** via `MarketData.GetMarketDepth`; **not** reliably in historical backtests.
- Backtest OHLC strategies first; add DOM confirmation on demo forward-test.

## Goal vs risk

€1000/day on €10,000 (= 10%/day) **conflicts** with a **2% daily loss stop**. The bot enforces your risk rules; treat €1000/day as a later equity-scaled ambition after positive expectancy is proven.

## Quick start

1. Paste `XauUsdQuantBot.cs` into cTrader Algo → Build.  
2. Backtest each strategy on XAUUSD M1 (see scorecard).  
3. Attach best mode on **demo** with `UseDomFilter = true`.  

Defaults assume demo equity ≈ €10,000, risk 1%, max daily loss 2%.
