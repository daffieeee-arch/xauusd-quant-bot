# Wat verder wint (en wat niet)

Geen nieuwe “derde strategie”. Hybrid/confluence zakten al. De edge zit in **wanneer** we de VWAP-fade doen.

## Beslissing

| Idee | Full sample | Out-of-sample (na 11 aug) | Actie |
|------|-------------|---------------------------|--------|
| **M5 MR tight (huidige default)** | PF 1.45 / +€11.2k | **PF 1.95 / +€8.3k** | **Houden** |
| Skip London 07–08 UTC | PF 2.59 / +€26.9k | PF 1.27 / +€3.7k | Kandidaat, nóg niet default |
| Range-filter (ADX/ATR) | PF 1.65 | **PF 0.97 / −€296** | Afgekeurd (overfit) |
| Alleen overlap 12–16 | PF 1.22 | — | Te zwak / meer DD |
| Range + overlap | PF 0.93 | — | Dood |

Nieuwe default = **niet** de flashy skip-open. Die wint in-sample vooral omdat uur 7 in juni–juli giftig was; in augustus was uur 7 juist nuttig. Echte IC-ticks moeten dat breken of bevestigen.

## Uur-anatomie (bestaande M5 MR-tight trades)

| UTC | Trades | Win% | Net |
|-----|--------|------|-----|
| 07 (London open) | 112 | 44% | **−€1.581** |
| **08** | 54 | **67%** | **+€10.296** |
| 09 | 24 | 33% | −€1.611 |
| **10** | 18 | 61% | +€3.788 |
| 11 | 10 | 30% | −€216 |
| 12+ | weinig | — | klein plus |

Dus: niet “meer trades”, maar **minder rotte uren**. Dat is de scalper-edge tot ticks er zijn.

## Wat ik níet ga bouwen tot IC-data er is

- Meer indicator-soep (RSI/MACD/bollinger-stack) — classic curve-fit
- Hybrid terug aanzetten
- Tick-HFT / honderden trades op Yahoo-M5 (geen echte bid/ask)
- DOM-strategie op historie (bestaat niet)

## Wat wél de volgende winstpaden zijn (volgorde)

1. **IC bid/ask ticks** (wacht op Active app) — spread per uur, echte fill, seconden-bars.
2. **Uur-filter valideren op die ticks** — 07/09 skip alleen als het daar ook rood is.
3. **Cost-first**: geen trade als ATR-target < ~2× (spread+slip+commission).
4. **Micro 0.15%** alleen nádat tick-spread de M5-MR edge in leven laat.
5. **News-blackout** (NFP, FOMC, CPI) — later, geen giswerk op Yahoo.

Fat-spread test ($0.35+$0.08) op range+skip bleef plus (PF 1.66) — hoopvol, maar die variant zakte OOS. Op **baseline** moeten we dezelfde stress doen zodra IC-ticks er zijn.

## cBot

Defaults blijven: MeanReversion, SL 0.8 ATR, TP 1.2, 1%/2%, €1k lock, sessie 07–21 UTC.  
Skip-07 is een parameter-kandidaat, geen lock-in.
