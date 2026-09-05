# Walk-forward (M5, 65% in-sample / 35% out-of-sample)

Data: GC=F  cut date **2026-08-11**.

| setup | split | trades | win% | PF | net | avg day | days_hit_1000 | max DD% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| mean_reversion tight | IS | 187 | 50.27 | 1.428 | 8362.07 | 214.41 | 11 | -13.47 |
| mean_reversion tight | OOS | 97 | 53.61 | 1.953 | 8282.64 | 376.48 | 8 | -12.6 |
| breakout tight | IS | 188 | 45.74 | 1.303 | 5197.78 | 133.28 | 8 | -17.4 |
| breakout tight | OOS | 143 | 46.15 | 1.107 | 1472.21 | 66.92 | 3 | -13.91 |
| hybrid tight | IS | 149 | 46.98 | 1.326 | 4535.59 | 116.3 | 6 | -16.17 |
| hybrid tight | OOS | 123 | 42.28 | 0.903 | -994.32 | -45.2 | 1 | -15.64 |
| mean_reversion default | IS | 139 | 48.2 | 1.661 | 8697.58 | 223.01 | 10 | -10.61 |
| mean_reversion default | OOS | 74 | 37.84 | 1.28 | 1580.38 | 71.84 | 4 | -15.06 |
