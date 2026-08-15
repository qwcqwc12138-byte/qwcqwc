# Stock Market Analysis and Portfolio Optimization: Final Research Report

- Research run date: August 14, 2026 (`America/Los_Angeles`)
- Data interval: January 3, 2023 through August 14, 2026
- Number of securities: 15
- Purpose: education and research; not investment advice

## 1. Executive summary

This project establishes a reproducible workflow from market-data acquisition and validation through exploratory analysis, constrained optimization, and out-of-sample backtesting. The Yahoo Finance data set contains 13,605 rows and 907 trading days for each security. Ordinary and adjusted closing prices have no missing values, and the canonical primary key has no duplicates.

In the rolling out-of-sample backtest from January 4, 2024 through August 14, 2026, the maximum-Sharpe strategy produced the highest historical annualized return and Sharpe ratio, but also the highest volatility and largest drawdown of the three strategies. The minimum-volatility strategy returned less but had the lowest annualized volatility and smallest maximum drawdown. These results illustrate a historical risk-return tradeoff; they do not demonstrate that any strategy will remain effective.

| Strategy | Cumulative return | Annualized return | Annualized volatility | Sharpe ratio | Maximum drawdown | Total turnover |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Equal weight | 81.46% | 25.77% | 15.03% | 1.46 | -20.13% | 1.77 |
| Minimum volatility | 62.96% | 20.67% | 11.93% | 1.41 | -13.72% | 3.08 |
| Maximum Sharpe | 123.45% | 36.25% | 18.40% | 1.76 | -22.35% | 7.17 |

## 2. Data and conventions

- **Universe:** 15 stocks divided equally among technology, financials, and consumer companies.
- **Return calculation:** adjusted closing prices are used to avoid mechanical jumps caused by stock splits and cash dividends.
- **Panel quality:** all 15 securities cover the same 907 trading days, for 100% panel coverage. There are no OHLC relationship violations and no adjusted daily returns with an absolute value above 25%. The data includes 208 cash-dividend events and two stock-split events.
- **Data limitation:** `yfinance` is an open-source interface to public Yahoo data, not an official Yahoo SDK. Provider licensing and an independent data source should be considered when interpreting the research.
- **Cross-provider status:** Alpha Vantage and Nasdaq Data Link adapters are implemented, but final price reconciliation requires the user's API key or a corresponding data subscription.

## 3. Exploratory analysis

Complete outputs are stored locally under `artifacts/eda/`. They include normalized adjusted prices, return correlations, 63-day rolling annualized volatility, and daily-return distributions.

Over the historical period, NVDA's annualized return and volatility were substantially higher than those of the other securities. NKE had a negative historical annualized return and a maximum drawdown of approximately -66.50%. This demonstrates how chasing historical winners can increase concentration and estimation instability, and it explains the need for both stock and sector caps in portfolio optimization.

## 4. Optimization method and constraints

The model uses PyPortfolioOpt with the following design:

- expected returns estimated from historical compound returns;
- Ledoit–Wolf covariance shrinkage as the risk model;
- a 15-stock equal-weight baseline;
- minimum-variance and maximum-Sharpe optimization objectives;
- long-only weights that sum to one, with a 25% single-stock cap and a 45% single-sector cap; and
- a 3.80% risk-free rate from the U.S. Treasury's 13-week bill coupon-equivalent rate published for August 14, 2026.

The full-sample optimization estimates below are in-sample results and should not be confused with the subsequent out-of-sample backtest.

| Strategy | Estimated annualized return | Estimated volatility | Estimated Sharpe ratio | Largest stock weight |
| --- | ---: | ---: | ---: | ---: |
| Equal weight | 29.49% | 14.55% | 1.77 | 6.67% |
| Minimum volatility | 20.90% | 11.67% | 1.47 | 25.00% |
| Maximum Sharpe | 49.96% | 16.75% | 2.76 | 25.00% |

The main maximum-Sharpe weights are NVDA 25.00%, KO 24.15%, WMT 20.85%, JPM 18.40%, GOOGL 9.55%, and META 2.05%. The minimum-volatility portfolio places more weight on KO, PG, V, MSFT, and JPM. Both optimized portfolios reach the 45% sector cap exactly, showing that the sector constraint is active in the fitted solutions.

## 5. Out-of-sample backtest design

- **Training window:** the most recent 252 trading days.
- **Rebalancing:** every 21 trading days.
- **Test period:** January 4, 2024 through August 14, 2026, covering 655 trading days.
- **Trading costs:** 10 bps per unit of turnover; the first allocation from cash is treated as 100% turnover.
- **Look-ahead control:** weights at each rebalance date are estimated only from prices available before that date and are then applied to the next return interval.
- **Holdings treatment:** weights are allowed to drift with asset prices between rebalances rather than being reset to target weights each day.

Total turnover for the maximum-Sharpe strategy is approximately 7.17, substantially above the equal-weight and minimum-volatility strategies. It is therefore more sensitive to trading costs, slippage, and estimation-window changes. Any advantage in live execution may be smaller than the frictionless headline result.

## 6. Sensitivity analysis

The sensitivity study varies the sample end date, estimation window, and single-stock cap. For samples ending August 14, 2026, the estimated maximum-Sharpe ratio changes materially with window length: approximately 3.19 for 126 days, 2.79–2.97 for 252 days, and 2.00–2.03 for 504 days. Moving the end date to May 14, 2026 raises the estimated Sharpe ratio for the 252-day window to approximately 4.86–5.33, demonstrating substantial end-date sensitivity. Shorter windows produce more optimistic estimates because recent trends and estimation error act together. Relaxing the stock cap from 20% to 35% directly increases the largest position for some windows.

The research must therefore avoid selecting whichever window or constraint produces the most attractive result. Production-grade work should specify windows, costs, and constraints in advance, then validate them across more market regimes and a longer sample.

## 7. Limitations

- The universe is selected from current companies, creating survivorship bias and excluding delisted securities.
- Approximately 3.6 years of history does not span multiple complete economic cycles.
- Historical means are noisy expected-return estimates, and maximum-Sharpe optimization is particularly sensitive to them.
- The backtest does not model bid–ask spreads, market impact, taxes, fractional-share constraints, or capacity limits.
- The three research sectors are simplified categories and are not standard GICS classifications.
- The final data set has not been reconciled against licensed Alpha Vantage or Nasdaq data.

## 8. Reproduction

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
market-data fetch --source yahoo --start 2023-01-01 --end 2026-08-14
market-data run-all data/processed/yahoo/prices_2023-01-01_2026-08-14.csv --output-dir artifacts
pytest
ruff check .
```

Risk-free-rate source: [U.S. Treasury Daily Treasury Bill Rates](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value=2026&type=daily_treasury_bill_rates). Optimization reference: [PyPortfolioOpt Mean-Variance Optimization](https://pyportfolioopt.readthedocs.io/en/latest/MeanVariance.html).
