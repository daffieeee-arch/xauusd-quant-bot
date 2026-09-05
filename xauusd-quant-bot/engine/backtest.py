"""Event-driven XAUUSD backtest with IC Markets-style costs and daily target logic."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .config import AccountSpec, ContractSpec, StrategyParams
from .strategies import SIGNALS, enrich


@dataclass
class Trade:
    strategy: str
    side: int
    entry_time: pd.Timestamp
    exit_time: pd.Timestamp
    entry: float
    exit: float
    lots: float
    pnl: float
    reason: str
    day_pnl_after: float


@dataclass
class BacktestResult:
    strategy: str
    timeframe: str
    source: str
    equity_start: float
    equity_end: float
    trades: list[Trade]
    equity_curve: pd.Series
    daily: pd.DataFrame
    notes: list[str] = field(default_factory=list)

    @property
    def n(self) -> int:
        return len(self.trades)

    @property
    def net(self) -> float:
        return sum(t.pnl for t in self.trades)

    @property
    def wins(self) -> int:
        return sum(1 for t in self.trades if t.pnl > 0)

    @property
    def win_rate(self) -> float:
        return (self.wins / self.n) if self.n else 0.0

    @property
    def profit_factor(self) -> float:
        gp = sum(t.pnl for t in self.trades if t.pnl > 0)
        gl = abs(sum(t.pnl for t in self.trades if t.pnl < 0))
        if gl <= 1e-9:
            return float("inf") if gp > 0 else 0.0
        return gp / gl

    @property
    def max_dd_pct(self) -> float:
        curve = self.equity_curve
        if curve.empty:
            return 0.0
        peak = curve.cummax()
        dd = (curve - peak) / peak * 100.0
        return float(dd.min())

    @property
    def target_days(self) -> int:
        if self.daily.empty:
            return 0
        return int((self.daily["pnl"] >= 1000.0).sum())

    @property
    def halt_days(self) -> int:
        if self.daily.empty:
            return 0
        return int((self.daily["halted"] > 0).sum())


def _round_lot(lots: float, spec: ContractSpec) -> float:
    if lots < spec.min_lot:
        return 0.0
    steps = np.floor(lots / spec.lot_step) * spec.lot_step
    return float(round(steps, 2))


def _pnl(side: int, entry: float, exit_px: float, lots: float, contract: ContractSpec) -> float:
    move = (exit_px - entry) * side
    gross = move * contract.ounces_per_lot * lots
    comm = contract.commission_per_lot_rt * lots
    return gross - comm


def _size_lots(
    equity: float,
    sl_dist: float,
    day_pnl: float,
    account: AccountSpec,
    contract: ContractSpec,
    params: StrategyParams,
    price: float,
) -> float:
    risk_money = equity * (account.risk_pct / 100.0)
    if params.press_winners and day_pnl > 0:
        # Press size as the day goes green — this is how a +€3–4k burst happens
        # after a first winner, without raising the -2% daily halt.
        mult = 1.0 + (day_pnl / max(account.daily_profit_target / 4.0, 1.0))
        mult = min(mult, params.press_max_mult)
        risk_money *= mult
    risk_per_lot = sl_dist * contract.ounces_per_lot
    if risk_per_lot <= 0:
        return 0.0
    lots = risk_money / risk_per_lot
    # Leverage / free-margin cap (500x, 50% stop-out buffer).
    notional_per_lot = price * contract.ounces_per_lot
    margin_per_lot = notional_per_lot / account.leverage
    max_lots_margin = (equity * 0.8) / max(margin_per_lot, 1e-9)
    lots = min(lots, max_lots_margin)
    return _round_lot(lots, contract)


def run_backtest(
    raw: pd.DataFrame,
    strategy: str,
    timeframe: str,
    source: str,
    account: AccountSpec | None = None,
    contract: ContractSpec | None = None,
    params: StrategyParams | None = None,
) -> BacktestResult:
    account = account or AccountSpec()
    contract = contract or ContractSpec()
    params = params or StrategyParams()
    fn = SIGNALS[strategy]
    df = enrich(raw, params)

    equity = account.start_equity
    notes: list[str] = []
    trades: list[Trade] = []
    eq_times: list[pd.Timestamp] = []
    eq_vals: list[float] = []

    open_side = 0
    open_entry = 0.0
    open_lots = 0.0
    open_sl = 0.0
    open_tp = 0.0
    open_time: pd.Timestamp | None = None

    day_key = None
    day_start_eq = equity
    day_pnl = 0.0
    trades_today = 0
    cooldown = -1
    halted = False
    target_hit = False
    daily_rows: list[dict] = []

    def close_day(stamp):
        daily_rows.append(
            {
                "date": stamp,
                "pnl": day_pnl,
                "equity": equity,
                "trades": trades_today,
                "halted": int(halted),
                "target": int(target_hit),
            }
        )

    n = len(df)
    idx = df.index

    for i in range(1, n):
        ts = idx[i]
        row = df.iloc[i]
        prev = df.iloc[i - 1]
        d = ts.tz_convert("UTC").date()
        if d != day_key:
            if day_key is not None:
                close_day(day_key)
            day_key = d
            day_start_eq = equity
            day_pnl = 0.0
            trades_today = 0
            cooldown = -1
            halted = False
            target_hit = False

        half_spread = (contract.spread_price + contract.slippage_price) / 2.0
        high, low, opn = float(row["high"]), float(row["low"]), float(row["open"])
        atr = float(row["atr"]) if np.isfinite(row["atr"]) else 0.0

        # Manage open trade on this bar (conservative: SL before TP if both hit).
        if open_side != 0:
            hit_sl = (open_side == 1 and low <= open_sl) or (open_side == -1 and high >= open_sl)
            hit_tp = (open_side == 1 and high >= open_tp) or (open_side == -1 and low <= open_tp)
            exit_px = None
            reason = ""
            if hit_sl and hit_tp:
                exit_px = open_sl
                reason = "sl_and_tp_same_bar"
            elif hit_sl:
                exit_px = open_sl
                reason = "sl"
            elif hit_tp:
                exit_px = open_tp
                reason = "tp"
            if exit_px is not None:
                # Pay remaining half-spread on exit.
                exit_px = exit_px - open_side * half_spread
                pnl = _pnl(open_side, open_entry, exit_px, open_lots, contract)
                equity += pnl
                day_pnl = equity - day_start_eq
                trades.append(
                    Trade(
                        strategy=strategy,
                        side=open_side,
                        entry_time=open_time,
                        exit_time=ts,
                        entry=open_entry,
                        exit=exit_px,
                        lots=open_lots,
                        pnl=pnl,
                        reason=reason,
                        day_pnl_after=day_pnl,
                    )
                )
                if pnl < 0:
                    cooldown = i + account.cooldown_bars_after_loss
                open_side = 0
                if day_pnl <= -account.start_equity * (account.max_daily_loss_pct / 100.0):
                    halted = True
                if params.lock_at_daily_target and day_pnl >= account.daily_profit_target:
                    target_hit = True
                    halted = True

        if open_side != 0:
            eq_times.append(ts)
            eq_vals.append(equity)
            continue

        if halted or trades_today >= account.max_trades_per_day or i < cooldown:
            eq_times.append(ts)
            eq_vals.append(equity)
            continue

        # Signal on the *closed* previous bar, fill at this open + spread.
        sig = fn(prev, df.iloc[i - 2] if i >= 2 else prev, params)
        if sig == 0 or not np.isfinite(atr) or atr < params.min_atr:
            eq_times.append(ts)
            eq_vals.append(equity)
            continue

        sl_dist = atr * params.sl_atr
        tp_dist = atr * params.tp_atr
        if sl_dist <= 0:
            eq_times.append(ts)
            eq_vals.append(equity)
            continue

        lots = _size_lots(equity, sl_dist, day_pnl, account, contract, params, opn)
        if lots <= 0:
            eq_times.append(ts)
            eq_vals.append(equity)
            continue

        entry = opn + sig * half_spread
        open_side = sig
        open_entry = entry
        open_lots = lots
        open_sl = entry - sig * sl_dist
        open_tp = entry + sig * tp_dist
        open_time = ts
        trades_today += 1

        eq_times.append(ts)
        eq_vals.append(equity)

    if day_key is not None:
        close_day(day_key)

    # Force-flat leftover
    if open_side != 0 and n:
        last = df.iloc[-1]
        ts = idx[-1]
        exit_px = float(last["close"]) - open_side * (contract.spread_price / 2.0)
        pnl = _pnl(open_side, open_entry, exit_px, open_lots, contract)
        equity += pnl
        trades.append(
            Trade(
                strategy=strategy,
                side=open_side,
                entry_time=open_time,
                exit_time=ts,
                entry=open_entry,
                exit=exit_px,
                lots=open_lots,
                pnl=pnl,
                reason="eod_flat",
                day_pnl_after=day_pnl + pnl,
            )
        )

    daily = pd.DataFrame(daily_rows)
    curve = pd.Series(eq_vals, index=pd.DatetimeIndex(eq_times), name="equity") if eq_times else pd.Series(dtype=float)
    if equity < account.start_equity * (contract.stop_out_pct / 100.0):
        notes.append("Account would have hit stop-out during this sample.")
    notes.append(
        "Daily target path: 1 lot × $10 gold move ≈ €1000. "
        "Press-winners scales size only after the day is green; -2% halt stays hard."
    )
    return BacktestResult(
        strategy=strategy,
        timeframe=timeframe,
        source=source,
        equity_start=account.start_equity,
        equity_end=equity,
        trades=trades,
        equity_curve=curve,
        daily=daily,
        notes=notes,
    )
