// -------------------------------------------------------------------------------------------------
// XauUsdQuantBot — multi-strategy XAUUSD scalper for cTrader / IC Markets (demo-first)
// Strategies: Breakout | MeanReversion | Hybrid | RotateAll
// Risk defaults: 1% per trade, 2% max daily loss
// DOM (Level II) filter: live/demo only — skipped when MarketDepth empty (typical in backtest)
// -------------------------------------------------------------------------------------------------
using System;
using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;

namespace cAlgo.Robots
{
    public enum StrategyMode
    {
        Breakout,
        MeanReversion,
        Hybrid,
        RotateAll
    }

    public enum SessionFilterMode
    {
        AllSessions,
        LondonNY,
        LondonOnly,
        NewYorkOnly
    }

    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class XauUsdQuantBot : Robot
    {
        // ---- Strategy ----
        [Parameter("Strategy Mode", DefaultValue = StrategyMode.Hybrid)]
        public StrategyMode StrategyMode { get; set; }

        [Parameter("Session Filter", DefaultValue = SessionFilterMode.LondonNY)]
        public SessionFilterMode SessionFilter { get; set; }

        // ---- Risk ----
        [Parameter("Risk % per trade", DefaultValue = 1.0, MinValue = 0.1, MaxValue = 5.0)]
        public double RiskPercent { get; set; }

        [Parameter("Max daily loss %", DefaultValue = 2.0, MinValue = 0.5, MaxValue = 10.0)]
        public double MaxDailyLossPercent { get; set; }

        [Parameter("Max daily profit % (optional halt)", DefaultValue = 0.0, MinValue = 0.0)]
        public double MaxDailyProfitPercent { get; set; }

        [Parameter("Max trades per day", DefaultValue = 12, MinValue = 1, MaxValue = 100)]
        public int MaxTradesPerDay { get; set; }

        [Parameter("Cooldown bars after loss", DefaultValue = 3, MinValue = 0, MaxValue = 50)]
        public int CooldownBarsAfterLoss { get; set; }

        [Parameter("Max open positions", DefaultValue = 1, MinValue = 1, MaxValue = 3)]
        public int MaxOpenPositions { get; set; }

        // ---- Execution filters ----
        [Parameter("Max spread (price)", DefaultValue = 0.40, MinValue = 0.05)]
        public double MaxSpreadPrice { get; set; }

        [Parameter("Use DOM filter (L2)", DefaultValue = true)]
        public bool UseDomFilter { get; set; }

        [Parameter("DOM top levels", DefaultValue = 5, MinValue = 1, MaxValue = 20)]
        public int DomTopLevels { get; set; }

        [Parameter("DOM min imbalance", DefaultValue = 0.25, MinValue = 0.05, MaxValue = 0.9)]
        public double DomMinImbalance { get; set; }

        [Parameter("SL ATR multiplier", DefaultValue = 1.2, MinValue = 0.3)]
        public double SlAtrMult { get; set; }

        [Parameter("TP ATR multiplier", DefaultValue = 1.8, MinValue = 0.3)]
        public double TpAtrMult { get; set; }

        [Parameter("ATR periods", DefaultValue = 14, MinValue = 5)]
        public int AtrPeriods { get; set; }

        // ---- Breakout ----
        [Parameter("Breakout lookback bars", DefaultValue = 20, MinValue = 5)]
        public int BreakoutLookback { get; set; }

        [Parameter("Breakout buffer ATR", DefaultValue = 0.15, MinValue = 0.0)]
        public double BreakoutBufferAtr { get; set; }

        // ---- Mean reversion ----
        [Parameter("VWAP deviation ATR", DefaultValue = 1.4, MinValue = 0.5)]
        public double VwapDeviationAtr { get; set; }

        [Parameter("EMA period (MR filter)", DefaultValue = 50, MinValue = 10)]
        public int EmaPeriod { get; set; }

        // ---- Hybrid ----
        [Parameter("Hybrid EMA fast", DefaultValue = 9, MinValue = 3)]
        public int HybridEmaFast { get; set; }

        [Parameter("Hybrid EMA slow", DefaultValue = 21, MinValue = 5)]
        public int HybridEmaSlow { get; set; }

        [Parameter("Min ATR (price) to trade", DefaultValue = 0.15, MinValue = 0.01)]
        public double MinAtrPrice { get; set; }

        private const string BotLabel = "XAUQ";

        private AverageTrueRange _atr;
        private ExponentialMovingAverage _ema;
        private ExponentialMovingAverage _emaFast;
        private ExponentialMovingAverage _emaSlow;
        private MarketDepth _marketDepth;

        private double _dayStartEquity;
        private int _dayStamp = -1;
        private int _tradesToday;
        private int _cooldownUntilBar = -1;
        private int _rotateIndex;
        private double _lastDomImbalance;
        private bool _domAvailable;

        private double _sessionVwapNum;
        private double _sessionVwapDen;
        private int _vwapDayStamp = -1;

        protected override void OnStart()
        {
            _atr = Indicators.AverageTrueRange(AtrPeriods, MovingAverageType.Exponential);
            _ema = Indicators.ExponentialMovingAverage(Bars.ClosePrices, EmaPeriod);
            _emaFast = Indicators.ExponentialMovingAverage(Bars.ClosePrices, HybridEmaFast);
            _emaSlow = Indicators.ExponentialMovingAverage(Bars.ClosePrices, HybridEmaSlow);

            _marketDepth = MarketData.GetMarketDepth(SymbolName);
            _marketDepth.Updated += OnMarketDepthUpdated;

            ResetDayIfNeeded();
            Print("XauUsdQuantBot started | Mode={0} | Risk={1}% | MaxDDDay={2}% | DOM={3}",
                StrategyMode, RiskPercent, MaxDailyLossPercent, UseDomFilter);
            Print("NOTE: DOM (Level II) is live/demo liquidity. Historical backtests usually have empty DOM.");
            Print("NOTE: €1000/day on €10k conflicts with 2% daily loss halt — optimize expectancy first.");
        }

        protected override void OnStop()
        {
            if (_marketDepth != null)
                _marketDepth.Updated -= OnMarketDepthUpdated;
        }

        private void OnMarketDepthUpdated()
        {
            _lastDomImbalance = ComputeDomImbalance();
            _domAvailable = _marketDepth.BidEntries.Count > 0 || _marketDepth.AskEntries.Count > 0;
        }

        protected override void OnBar()
        {
            ResetDayIfNeeded();
            UpdateSessionVwap();

            if (!CanTradeNow())
                return;

            if (Positions.FindAll(BotLabel, SymbolName).Length >= MaxOpenPositions)
                return;

            var atr = _atr.Result.Last(1);
            if (double.IsNaN(atr) || atr < MinAtrPrice)
                return;

            TradeType? signal = null;
            string reason = null;

            switch (StrategyMode)
            {
                case StrategyMode.Breakout:
                    signal = SignalBreakout(atr, out reason);
                    break;
                case StrategyMode.MeanReversion:
                    signal = SignalMeanReversion(atr, out reason);
                    break;
                case StrategyMode.Hybrid:
                    signal = SignalHybrid(atr, out reason);
                    break;
                case StrategyMode.RotateAll:
                    signal = SignalRotate(atr, out reason);
                    break;
            }

            if (signal == null)
                return;

            if (!PassesDomFilter(signal.Value))
            {
                Print("DOM filter blocked {0} | imbalance={1:F2} available={2}",
                    signal.Value, _lastDomImbalance, _domAvailable);
                return;
            }

            Enter(signal.Value, atr, reason ?? StrategyMode.ToString());
        }

        private TradeType? SignalRotate(double atr, out string reason)
        {
            // Try strategies in rotation order; take first valid signal this bar.
            var order = new[]
            {
                StrategyMode.Hybrid,
                StrategyMode.Breakout,
                StrategyMode.MeanReversion
            };

            for (var i = 0; i < order.Length; i++)
            {
                var idx = (_rotateIndex + i) % order.Length;
                TradeType? s = null;
                string r = null;
                switch (order[idx])
                {
                    case StrategyMode.Breakout:
                        s = SignalBreakout(atr, out r);
                        break;
                    case StrategyMode.MeanReversion:
                        s = SignalMeanReversion(atr, out r);
                        break;
                    case StrategyMode.Hybrid:
                        s = SignalHybrid(atr, out r);
                        break;
                }

                if (s != null)
                {
                    _rotateIndex = (idx + 1) % order.Length;
                    reason = "Rotate:" + r;
                    return s;
                }
            }

            reason = null;
            return null;
        }

        // A) Momentum / range breakout on prior N bars
        private TradeType? SignalBreakout(double atr, out string reason)
        {
            reason = null;
            if (Bars.Count < BreakoutLookback + 5)
                return null;

            var high = double.MinValue;
            var low = double.MaxValue;
            for (var i = 2; i <= BreakoutLookback + 1; i++)
            {
                high = Math.Max(high, Bars.HighPrices.Last(i));
                low = Math.Min(low, Bars.LowPrices.Last(i));
            }

            var buffer = atr * BreakoutBufferAtr;
            var close1 = Bars.ClosePrices.Last(1);
            var open1 = Bars.OpenPrices.Last(1);

            // Require decisive close through range + candle in direction
            if (close1 > high + buffer && close1 > open1)
            {
                reason = "BreakoutLong";
                return TradeType.Buy;
            }

            if (close1 < low - buffer && close1 < open1)
            {
                reason = "BreakoutShort";
                return TradeType.Sell;
            }

            return null;
        }

        // B) Mean reversion vs session VWAP, with EMA regime filter
        private TradeType? SignalMeanReversion(double atr, out string reason)
        {
            reason = null;
            var vwap = GetSessionVwap();
            if (vwap <= 0 || Bars.Count < EmaPeriod + 5)
                return null;

            var close1 = Bars.ClosePrices.Last(1);
            var ema = _ema.Result.Last(1);
            var deviation = close1 - vwap;
            var threshold = atr * VwapDeviationAtr;

            // Fade stretch only when not violently trending against fade (soft EMA filter)
            if (deviation >= threshold && close1 > ema * 0.998)
            {
                // Extended above VWAP → short fade
                reason = "MR_Short_VWAP";
                return TradeType.Sell;
            }

            if (deviation <= -threshold && close1 < ema * 1.002)
            {
                reason = "MR_Long_VWAP";
                return TradeType.Buy;
            }

            return null;
        }

        // C) Hybrid: EMA cross + pullback to VWAP band + volatility OK
        private TradeType? SignalHybrid(double atr, out string reason)
        {
            reason = null;
            if (Bars.Count < HybridEmaSlow + 5)
                return null;

            var vwap = GetSessionVwap();
            var close1 = Bars.ClosePrices.Last(1);
            var close2 = Bars.ClosePrices.Last(2);
            var fast1 = _emaFast.Result.Last(1);
            var slow1 = _emaSlow.Result.Last(1);
            var fast2 = _emaFast.Result.Last(2);
            var slow2 = _emaSlow.Result.Last(2);

            var nearVwap = vwap <= 0 || Math.Abs(close1 - vwap) <= atr * 0.8;

            var bullCross = fast2 <= slow2 && fast1 > slow1;
            var bearCross = fast2 >= slow2 && fast1 < slow1;

            // Momentum continuation if already aligned and price holds near VWAP pullback
            var bullTrend = fast1 > slow1 && close1 > close2 && nearVwap;
            var bearTrend = fast1 < slow1 && close1 < close2 && nearVwap;

            if (bullCross || bullTrend)
            {
                reason = bullCross ? "Hybrid_BullCross" : "Hybrid_BullPullback";
                return TradeType.Buy;
            }

            if (bearCross || bearTrend)
            {
                reason = bearCross ? "Hybrid_BearCross" : "Hybrid_BearPullback";
                return TradeType.Sell;
            }

            return null;
        }

        private void Enter(TradeType side, double atr, string reason)
        {
            var slPips = PriceToPips(atr * SlAtrMult);
            var tpPips = PriceToPips(atr * TpAtrMult);
            if (slPips < Symbol.PipSize)
                return;

            var volume = ComputeVolumeForRisk(slPips);
            if (volume < Symbol.VolumeInUnitsMin)
            {
                Print("Volume below minimum — skip. Computed={0}", volume);
                return;
            }

            volume = Symbol.NormalizeVolumeInUnits(volume, RoundingMode.Down);
            var result = ExecuteMarketOrder(side, SymbolName, volume, BotLabel, slPips, tpPips, reason);

            if (!result.IsSuccessful)
            {
                Print("Order failed: {0}", result.Error);
                return;
            }

            _tradesToday++;
            Print("ENTER {0} vol={1} SL={2:F1}p TP={3:F1}p reason={4} spread={5:F2} domImb={6:F2}",
                side, volume, slPips, tpPips, reason, Symbol.Spread, _lastDomImbalance);
        }

        protected override void OnPositionClosed(Position position)
        {
            if (position.Label != BotLabel || position.SymbolName != SymbolName)
                return;

            if (position.NetProfit < 0 && CooldownBarsAfterLoss > 0)
                _cooldownUntilBar = Bars.Count + CooldownBarsAfterLoss;

            Print("EXIT {0} P/L={1:F2} reason={2}", position.TradeType, position.NetProfit, position.Comment);
        }

        private bool CanTradeNow()
        {
            ResetDayIfNeeded();

            if (_tradesToday >= MaxTradesPerDay)
                return false;

            if (Bars.Count < _cooldownUntilBar)
                return false;

            if (!InSession())
                return false;

            var spread = Symbol.Ask - Symbol.Bid;
            if (spread > MaxSpreadPrice)
                return false;

            var dayPnlPct = DayPnlPercent();
            if (dayPnlPct <= -MaxDailyLossPercent)
            {
                Print("Daily loss halt: {0:F2}%", dayPnlPct);
                return false;
            }

            if (MaxDailyProfitPercent > 0 && dayPnlPct >= MaxDailyProfitPercent)
                return false;

            return true;
        }

        private bool PassesDomFilter(TradeType side)
        {
            if (!UseDomFilter)
                return true;

            // Backtest / no depth: do not block OHLC strategies
            if (!_domAvailable)
                return true;

            // Positive imbalance = more bid volume → bullish pressure
            if (side == TradeType.Buy)
                return _lastDomImbalance >= DomMinImbalance;

            return _lastDomImbalance <= -DomMinImbalance;
        }

        private double ComputeDomImbalance()
        {
            if (_marketDepth == null)
                return 0;

            double bidVol = 0;
            double askVol = 0;
            var n = 0;
            foreach (var e in _marketDepth.BidEntries)
            {
                if (n++ >= DomTopLevels)
                    break;
                bidVol += e.VolumeInUnits;
            }

            n = 0;
            foreach (var e in _marketDepth.AskEntries)
            {
                if (n++ >= DomTopLevels)
                    break;
                askVol += e.VolumeInUnits;
            }

            var sum = bidVol + askVol;
            if (sum <= 0)
                return 0;

            return (bidVol - askVol) / sum;
        }

        // Symbol.PipValue ≈ P/L for 1 unit moving 1 pip on cTrader.
        private double ComputeVolumeForRisk(double stopPips)
        {
            var riskMoney = Account.Equity * (RiskPercent / 100.0);
            if (riskMoney <= 0 || stopPips <= 0)
                return 0;

            var riskPerUnit = stopPips * Symbol.PipValue;
            if (riskPerUnit <= 0)
                return 0;

            return riskMoney / riskPerUnit;
        }

        private double PriceToPips(double priceDistance)
        {
            if (Symbol.PipSize <= 0)
                return 0;
            return priceDistance / Symbol.PipSize;
        }

        private void ResetDayIfNeeded()
        {
            var stamp = Server.Time.Year * 1000 + Server.Time.DayOfYear;
            if (stamp == _dayStamp)
                return;

            _dayStamp = stamp;
            _dayStartEquity = Account.Equity;
            _tradesToday = 0;
            _cooldownUntilBar = -1;
            ResetVwap();
            Print("New day | equity={0:F2}", _dayStartEquity);
        }

        private double DayPnlPercent()
        {
            if (_dayStartEquity <= 0)
                return 0;
            return (Account.Equity - _dayStartEquity) / _dayStartEquity * 100.0;
        }

        private bool InSession()
        {
            var hour = Server.Time.Hour; // UTC
            switch (SessionFilter)
            {
                case SessionFilterMode.AllSessions:
                    return true;
                case SessionFilterMode.LondonOnly:
                    return hour >= 7 && hour < 16;
                case SessionFilterMode.NewYorkOnly:
                    return hour >= 12 && hour < 21;
                case SessionFilterMode.LondonNY:
                default:
                    // London 07-16 UTC, NY 12-21 UTC → trade 07-21, prefer overlap naturally via volatility
                    return hour >= 7 && hour < 21;
            }
        }

        private void ResetVwap()
        {
            _vwapDayStamp = _dayStamp;
            _sessionVwapNum = 0;
            _sessionVwapDen = 0;
        }

        private void UpdateSessionVwap()
        {
            if (_vwapDayStamp != _dayStamp)
                ResetVwap();

            // Use previous closed bar
            var typical = (Bars.HighPrices.Last(1) + Bars.LowPrices.Last(1) + Bars.ClosePrices.Last(1)) / 3.0;
            var vol = Math.Max(Bars.TickVolumes.Last(1), 1);
            _sessionVwapNum += typical * vol;
            _sessionVwapDen += vol;
        }

        private double GetSessionVwap()
        {
            if (_sessionVwapDen <= 0)
                return 0;
            return _sessionVwapNum / _sessionVwapDen;
        }
    }
}
