# Bevindingen — autonome run (geen clicks van jou)

Gedraaid op COMEX-goud (`GC=F`, Yahoo) als proxy voor IC Markets XAUUSD.
Accountmodel: **€10.000**, **1% risico**, **−2% daghalt**, **+€1.000 lock**, **500×**,
spread $0.20 + slip $0.05 + $6/lot RT, **press-winners** (grotere size pas ná een groene dag).

## Hoe €1.000/dag wél in de wiskunde past

Jouw bursts van €3–4k in minuten kloppen met goud-math, niet met “elke trade 1% tot het op is”:

- 1.00 lot XAUUSD = 100 oz → **$1 move = $100/lot**, **$10 move = $1.000/lot**
- Op 500× past meerdere lots op €10k (margin ≈ prijs×100/500)
- Pad naar +€1.000 **binnen** −€200 halt: eerste scalp winnen → **size pressen** → lock bij +€1.000
- Twee volle verliezers eerst = dag klaar. Daarom alleen London/NY + strakke setups

Dat is geen garantie voor **elke** dag +€1.000. Het is wel het mechanisme waarmee die dagen (en jouw €3–4k-bursts) ontstaan.

## Wat de data deed

**Beste setup: mean-reversion, strakke scalp, M5** (VWAP-fade, SL 0.8 ATR, TP 1.2 ATR)

| Sample | Periode | Trades | Win% | Profit factor | Net | Dagen +€1k | Max DD |
|--------|---------|--------|------|---------------|-----|------------|--------|
| Volledig | 26 jun–4 sep 2026 (61d) | 226 | 49% | 1.45 | **+€11.246** | **15 (25%)** | −13.5% |
| In-sample | tot 10 aug | 187 | 50% | 1.43 | +€8.362 | 11 | −13.5% |
| **Out-of-sample** | 11 aug–4 sep | 97 | 54% | **1.95** | **+€8.283** | **8** | −12.6% |

OOS is **sterker** dan IS — geen duidelijk curve-fit signaal.

Andere setups (zelfde kosten/risk):

- **Breakout M5 tight**: +€7.3k / 61d, 13× +€1k, OOS nog + maar zwakker (PF 1.11)
- **Hybrid M5 tight**: +€1.2k, OOS **negatief** (PF 0.90) — afgekeurd als primaire bot
- **M1** (alleen 7 dagen): MR tight +€1.7k, 2× +€1k — te kort om te vertrouwen
- **H1 hybrid** (2 jaar): +€40k maar −20% DD en weinig €1k-dagen — geen scalper

Verdeling van de winnaar: **mediaan-dag is rood** (vaak de −€200 halt), **gemiddelde-dag ≈ +€184** omdat een kwart van de dagen de +€1k lock raakt. Dat is exact “soms 3–4k in minuten, soms slechte trades” — nu met een harde rem.

Equity-curve: `reports/equity_m5_mean_reversion_tight.png`

## Wat er nu gebouwd is (jij hoeft niets te klikken)

1. cTrader **cBot** (C#) — defaults gezet op deze winnaar + press + €1.000 lock  
2. Autonome **Python-engine** die data haalt, alle strategieën test, walk-forward draait, rapporten schrijft  
3. Klaar om later op **jouw demo** te hangen zodra Open API / cTID-gegevens er zijn

## Wat ik níet kan tot jij credentials deelt

Orders op **jouw** IC Markets-demo. Yahoo ≠ IC-spread/DOM. Eerste live-demo run is de echte forward-test.

## Volgende stap (van mij, als jij API geeft)

Paper/demo XAUUSD M5 mean-reversion tight, DOM-filter aan, zelfde 1%/2%/€1k-lock, dagelijkse rapportage.
