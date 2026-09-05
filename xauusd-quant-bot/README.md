# XAUUSD Quant Bot (cTrader / IC Markets)

Autonome research-pipeline + cTrader cBot voor **XAUUSD**. Jij hoeft geen sheets of UI te bedienen: `python3 -m engine.run` haalt data, test strategieën en schrijft rapporten.

## Status

- Engine + walk-forward gedraaid. Winnaar: **M5 mean-reversion tight** (OOS PF 1.95).
- Lees [`reports/FINDINGS.md`](reports/FINDINGS.md) — dat is het inhoudelijke rapport.
- Demo-orders op **jouw** IC-account volgen pas na API-credentials.

## Onderdelen

| Stuk | Pad |
|------|-----|
| Autonome engine | [`engine/`](engine/) |
| cBot (C#) | [`src/cBots/XauUsdQuantBot.cs`](src/cBots/XauUsdQuantBot.cs) |
| DOM-indicator | [`src/indicators/DomImbalance.cs`](src/indicators/DomImbalance.cs) |
| Bevindingen | [`reports/FINDINGS.md`](reports/FINDINGS.md) |
| Ruwe tabellen | [`reports/REPORT.md`](reports/REPORT.md), [`reports/WALKFORWARD.md`](reports/WALKFORWARD.md) |
| Broker-data | [`docs/DATA_AND_EDGE.md`](docs/DATA_AND_EDGE.md) |

## Zelf draaien (hier, zonder cTrader)

```bash
pip install -r requirements.txt
python3 -m engine.run
python3 -m engine.walkforward
python3 -m engine.plot
```

## Strategieën

1. **Breakout** — range-break + ATR-buffer  
2. **MeanReversion** — VWAP-stretch fade (primaire default)  
3. **Hybrid** — EMA-cross / pullback (OOS gezakt)  
4. **Confluence** — 2+ strategieën eens  

Risk: 1% per trade, −2% daghalt, +€1.000 lock, press-winners alleen als de dag groen is, 500× margin-cap.

## €1.000/dag

Niet “elke kalenderdag”. Wel: 1 lot × $10 goud ≈ €1.000, plus size-press ná de eerste win. In de 61-daagse M5-sample raakte de winnaar **15 dagen** de lock (~25%), net **+€11k**, OOS bevestigd.
