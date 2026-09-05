# IC Markets / cTrader data & edge research

## What IC Markets actually gives you on cTrader

| Data | Available? | Usable in backtest? | Notes |
|------|------------|---------------------|-------|
| Bid/Ask ticks & bars | Yes | Yes | Core for OHLC strategies |
| Spreads / commissions | Yes (live) | Partially | Model commission + typical XAUUSD spread in backtest |
| Level II DOM (Market Depth) | Yes on Raw Spread | **No historical DOM** | Aggregated LP liquidity ladder via `MarketData.GetMarketDepth` |
| True Level III (individual orders) | **No** | N/A | OTC FX/CFD gold is not an exchange order book |
| VWAP DOM / Price DOM | UI yes | No | Useful manually; algo gets Bid/Ask depth entries |
| Volume | Tick volume / broker volume | Yes (as provided) | Not exchange volume |

### Level II vs Level III (important)

- **Level II on IC Markets cTrader** = depth of market from their pricing aggregator: volume available at each price level from liquidity providers. Fills use VWAP against that book.
- **Level III** (full individual resting orders) is an **exchange** concept. XAUUSD CFD at a retail broker does **not** expose real L3. Do not design a strategy that assumes visible iceberg orders or “real” spoofing detection — you only see aggregated LP quotes.

### Implication for our bot

1. **OHLC/tick strategies (A/B/C)** can be **backtested** in cTrader Algo.
2. **DOM imbalance filter** is a **live/demo confirmation** only. In backtest it is skipped (or optionally ignored) because cTrader does not store historical DOM.
3. Edge validation order:
   - Backtest A/B/C on M1/M5 XAUUSD with commission + realistic spread.
   - Walk-forward / out-of-sample.
   - Demo forward-test with DOM filter ON.
   - Only then consider tiny live size.

## Target realism: €1000/day on €10,000

With your rules:

- Risk per trade: **1%** → €100 risked per trade
- Max daily loss: **2%** → bot **stops** after ≈ −€200 day P&L

To make **+€1000/day** you need **+10R net** in one day while a −2R day already kills trading. That is not compatible with the risk model. Realistic path:

1. Optimize for **positive expectancy** and controlled drawdown on demo.
2. Let equity compound under 1%/2% rules.
3. €1000/day becomes plausible only at much larger equity (e.g. ~€50k–€100k+) if expectancy holds — not as day-1 target on €10k.

The bot therefore optimizes for **process metrics**: win rate, profit factor, max DD, avg R, trades/day — not a forced €1000/day parameter.

**Path that can still produce €1000 days on €10k:** first trade at 1% risk; if the day is green, press size (capped) toward a €1000 lock; hard-stop at −2%. Math: 1.00 lot × $10 gold move ≈ €1000. Backtests (see `reports/FINDINGS.md`) show this lock firing on a minority of days, with most other days hitting the halt — net still positive on the winning setup.
