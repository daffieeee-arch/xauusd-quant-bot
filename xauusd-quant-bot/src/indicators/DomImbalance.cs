// Optional helper: visualize Level II imbalance on chart (live/demo).
// Attach on XAUUSD. Backtest will usually show flat/zero (no historical DOM).
using System;
using cAlgo.API;
using cAlgo.API.Internals;

namespace cAlgo.Indicators
{
    [Indicator(IsOverlay = false, TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class DomImbalance : Indicator
    {
        [Parameter("Top levels", DefaultValue = 5, MinValue = 1, MaxValue = 20)]
        public int TopLevels { get; set; }

        [Output("Imbalance", LineColor = "Orange", PlotType = PlotType.Histogram, Thickness = 3)]
        public IndicatorDataSeries Imbalance { get; set; }

        private MarketDepth _md;

        protected override void Initialize()
        {
            _md = MarketData.GetMarketDepth(SymbolName);
            _md.Updated += OnUpdated;
        }

        private void OnUpdated()
        {
            var index = Bars.Count - 1;
            if (index < 0)
                return;

            double bid = 0, ask = 0;
            var n = 0;
            foreach (var e in _md.BidEntries)
            {
                if (n++ >= TopLevels) break;
                bid += e.VolumeInUnits;
            }

            n = 0;
            foreach (var e in _md.AskEntries)
            {
                if (n++ >= TopLevels) break;
                ask += e.VolumeInUnits;
            }

            var sum = bid + ask;
            Imbalance[index] = sum <= 0 ? 0 : (bid - ask) / sum;
        }

        public override void Calculate(int index)
        {
        }
    }
}
