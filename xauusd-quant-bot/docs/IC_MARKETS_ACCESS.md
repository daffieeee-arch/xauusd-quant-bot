# Wat ik van jou nodig heb (IC Markets / cTrader)

Zonder dit kan ik alleen Yahoo/COMEX-proxy gebruiken. Voor echte scalps (seconden, tikkers, honderden trades) moet de dataset **jouw IC Markets bid/ask** zijn.

## Eenmalig — Open API (dit kan alleen jij)

Spotware laat mij geen app op jouw cTID aanmaken.

1. Ga naar https://openapi.ctrader.com/apps  
2. Log in met je **cTrader ID** (zelfde als cTrader).  
3. **Add new app**  
   - Name: `XAUUSD Quant Research`  
   - Description: `Personal research: download XAUUSD tick/bar history and later paper-trade my IC Markets demo.`  
   - Redirect URL: `https://localhost` (tweede URL, niet alleen de default playground)  
4. Save. Wacht tot status **Active** (Spotware-review, kan even duren).  
5. Kopieer **Client ID** + **Client Secret**.  
6. Open de grant-link (ik stuur die als ik ID heb, of vul zelf in):  
   `https://id.ctrader.com/my/settings/openapi/grantingaccess/?client_id=CLIENT_ID&redirect_uri=https://localhost&scope=trading&product=web`  
7. Allow access → je landt op `https://localhost/?code=...`  
8. Plak die hele URL naar mij (of alleen `code=`). Ik wissel hem om voor tokens.

Daarna doe ik de rest: tick-download, seconden-bars, analyse, bot.

## Plakblok (kopieer en vul in)

```
CTRADER_CLIENT_ID=
CTRADER_CLIENT_SECRET=
CTRADER_REDIRECT_URI=https://localhost
CTRADER_AUTH_CODE_OR_REDIRECT_URL=
IC_DEMO_ACCOUNT_NUMBER=
IC_ACCOUNT_CURRENCY=EUR
IC_ACCOUNT_TYPE=Raw Spread   (of Standard)
IC_LEVERAGE=500
IC_SYMBOL=XAUUSD
STARTING_EQUITY=10000
```

Optioneel maar nuttig (screenshot of tekst uit cTrader → Market Watch → XAUUSD → spec):

```
MIN_LOT=
LOT_STEP=
COMMISSION_PER_LOT_RT=
TYPICAL_SPREAD_YOU_SEE=
PIP_SIZE_OR_TICK_SIZE=
```

## Wat ik daarmee download

| Data | Via Open API | Historisch? | Nodig voor tick-scalp |
|------|----------------|-------------|------------------------|
| Bid/Ask **ticks** | `GetTickData` | Ja (chunks van ~1 week, 5 req/s) | Ja — kern |
| M1 / seconden-bars | `GetTrendbars` + ticks aggregeren | Ja | Ja |
| Live quotes | stream | n.v.t. | Ja, later demo |
| Level II DOM | live `MarketDepth` | **Nee** | Alleen vooruit opnemen |
| Level III | bestaat niet op XAUUSD CFD | — | — |

FIX API geeft **geen** tick-historie. Open API wel.

## Risk bij “honderden trades per dag”

−2% daghalt + 1% per trade = na **twee verliezers** stop.  
Honderden scalps kan wél als risico per trade **veel kleiner** is (bijv. 0.05–0.15%), zodat scratch/spread het account niet in twee ticks leegtrekt. Dat zet ik zo zodra IC-ticks er zijn.

## Demo eerst

Alleen **demo**-accountnummer. Geen live-wachtwoord nodig. Client secret + refresh token zijn genoeg; behandel ze als wachtwoord.
