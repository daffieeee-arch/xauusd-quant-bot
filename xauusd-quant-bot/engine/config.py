"""Account, contract and risk defaults for IC Markets-style XAUUSD CFDs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AccountSpec:
    start_equity: float = 10_000.0
    currency: str = "EUR"
    # Treat EUR ≈ USD for demo P&L (typical IC Markets USD/EUR demo).
    leverage: int = 500
    risk_pct: float = 1.0
    max_daily_loss_pct: float = 2.0
    daily_profit_target: float = 1_000.0
    max_trades_per_day: int = 40
    cooldown_bars_after_loss: int = 2
    max_open: int = 1


@dataclass(frozen=True)
class ContractSpec:
    """IC Markets XAUUSD: 1.00 lot = 100 oz. $1 price move = $100 / lot."""

    ounces_per_lot: float = 100.0
    min_lot: float = 0.01
    lot_step: float = 0.01
    # Raw-spread style costs (conservative).
    spread_price: float = 0.20  # $0.20 typical London/NY gold
    commission_per_lot_rt: float = 6.0  # $6 round-turn / lot
    slippage_price: float = 0.05
    stop_out_pct: float = 50.0  # IC Markets stop-out ~50%


@dataclass(frozen=True)
class StrategyParams:
    atr_period: int = 14
    sl_atr: float = 1.2
    tp_atr: float = 1.8
    min_atr: float = 0.12
    breakout_lookback: int = 20
    breakout_buffer_atr: float = 0.15
    vwap_dev_atr: float = 1.4
    ema_period: int = 50
    ema_fast: int = 9
    ema_slow: int = 21
    session: str = "london_ny"  # all | london | ny | london_ny
    # After the day is green, press size toward the daily target (capped).
    press_winners: bool = True
    press_max_mult: float = 4.0
    lock_at_daily_target: bool = True


STRATEGIES = ("breakout", "mean_reversion", "hybrid", "confluence")
