# Stock Market Analysis and Portfolio Optimization: Final Research Report

- Research run date: September 8, 2026 (`America/Los_Angeles`)
- Data interval: January 3, 2023 through September 8, 2026
- Number of securities: 15
- One-month project status: 25 of 31 daily runs completed
- Purpose: education and research; not investment advice

## 1. Executive summary

This project establishes a reproducible workflow from market-data acquisition and validation through exploratory analysis, constrained optimization, and out-of-sample backtesting. The synchronized Yahoo Finance data set contains 13,845 rows and 923 trading days for each security. Ordinary and adjusted closing prices have no missing values, and the canonical primary key has no duplicates. Twenty-five dated daily research packages have been retained from August 15 through September 8.

In the rolling out-of-sample backtest from January 4, 2024 through September 8, 2026, the maximum-Sharpe strategy produced the highest historical annualized return and Sharpe ratio, but also the highest volatility and largest drawdown of the three strategies. The minimum-volatility strategy returned less but had the lowest annualized volatility and smallest maximum drawdown. These results illustrate a historical risk-return tradeoff; they do not demonstrate that any strategy will remain effective.

| Strategy | Cumulative return | Annualized return | Annualized volatility | Sharpe ratio | Maximum drawdown | Total turnover |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Equal weight | 79.60% | 24.60% | 14.99% | 1.388 | -20.13% | 1.77 |
| Minimum volatility | 61.13% | 19.62% | 11.92% | 1.328 | -13.72% | 3.08 |
| Maximum Sharpe | 121.57% | 34.82% | 18.30% | 1.695 | -22.35% | 7.17 |

## 2. Data and conventions

- **Universe:** 15 stocks divided equally among technology, financials, and consumer companies.
- **Return calculation:** adjusted closing prices are used to avoid mechanical jumps caused by stock splits and cash dividends.
- **Panel quality:** all 15 securities cover the same 923 trading days, for 100% panel coverage. There are no missing ordinary or adjusted closes and no duplicate canonical keys. The data includes 214 cash-dividend events and two stock-split events.
- **Data limitation:** `yfinance` is an open-source interface to public Yahoo data, not an official Yahoo SDK. Provider licensing should be considered when interpreting the research.
- **Cross-provider status:** a 300-row Alpha Vantage spot check for AAPL, JPM, and COST found all rows on matching Yahoo Finance trading dates. Of 1,200 compared OHLC values, 1,198 were within 0.01%; the combined mean absolute OHLC difference was 0.000259%. See [`cross_provider_validation.md`](cross_provider_validation.md). Adjusted prices, corporate actions, the other twelve securities, and Nasdaq Data Link remain outside this independent check.

## 3. Exploratory analysis

Complete synchronized outputs are stored locally under `artifacts/daily/2026-09-08/eda/`. They include normalized adjusted prices, return correlations, 63-day rolling annualized volatility, and daily-return distributions.

Over the historical period, NVDA's annualized return and volatility were substantially higher than those of the other securities. NKE had a negative historical annualized return and a maximum drawdown of approximately -68.21%. This demonstrates how chasing historical winners can increase concentration and estimation instability, and it explains the need for both stock and sector caps in portfolio optimization.

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
| Equal weight | 28.55% | 14.52% | 1.704 | 6.67% |
| Minimum volatility | 20.47% | 11.69% | 1.426 | 25.00% |
| Maximum Sharpe | 48.29% | 16.78% | 2.651 | 25.00% |

The main maximum-Sharpe weights are NVDA 25.00%, KO 25.00%, WMT 20.00%, JPM 17.41%, GOOGL 8.85%, and META 3.74%. The minimum-volatility portfolio places more weight on KO, PG, V, MSFT, and JPM. Both optimized portfolios reach the 45% consumer-sector cap exactly, showing that the sector constraint is active in the fitted solutions.

## 5. Out-of-sample backtest design

- **Training window:** the most recent 252 trading days.
- **Rebalancing:** every 21 trading days.
- **Test period:** January 4, 2024 through September 8, 2026, covering 671 return observations.
- **Trading costs:** 10 bps per unit of turnover; the first allocation from cash is treated as 100% turnover.
- **Look-ahead control:** weights at each rebalance date are estimated only from prices available before that date and are then applied to the next return interval.
- **Holdings treatment:** weights are allowed to drift with asset prices between rebalances rather than being reset to target weights each day.

Total turnover for the maximum-Sharpe strategy is approximately 7.17, substantially above the equal-weight and minimum-volatility strategies. It is therefore more sensitive to trading costs, slippage, and estimation-window changes. Any advantage in live execution may be smaller than the frictionless headline result.

## 6. Sensitivity analysis

The sensitivity study varies the sample end date, estimation window, and single-stock cap across 18 scenarios. For samples ending September 8, 2026, estimated maximum-Sharpe ratios range from 3.737–3.810 for 126 observations, 2.338–2.594 for 252 observations, and 1.776–1.859 for 504 observations. Across the entire grid, fitted annual returns range from 30.26% to 66.20%, volatilities from 12.23% to 16.96%, and Sharpe ratios from 1.776 to 4.220. The dispersion demonstrates material sensitivity to the sample, lookback window, and position cap.

The research must therefore avoid selecting whichever window or constraint produces the most attractive result. Production-grade work should specify windows, costs, and constraints in advance, then validate them across more market regimes and a longer sample.

## 7. Limitations

- The universe is selected from current companies, creating survivorship bias and excluding delisted securities.
- Approximately 3.7 years of history does not span multiple complete economic cycles.
- Historical means are noisy expected-return estimates, and maximum-Sharpe optimization is particularly sensitive to them.
- The backtest does not model bid–ask spreads, market impact, taxes, fractional-share constraints, or capacity limits.
- The three research sectors are simplified categories and are not standard GICS classifications.
- Independent reconciliation is limited to 100 recent unadjusted observations for AAPL, JPM, and COST; adjusted prices, corporate actions, the remaining securities, and entitled Nasdaq data have not been independently verified.

## 8. Reproduction

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
market-data fetch --source yahoo --start 2023-01-01 --end 2026-09-08
market-data validate data/processed/yahoo/prices_2023-01-01_2026-09-08.csv
market-data run-all data/processed/yahoo/prices_2023-01-01_2026-09-08.csv --output-dir artifacts/daily/2026-09-08
pytest
ruff check .
```

Risk-free-rate source: [U.S. Treasury Daily Treasury Bill Rates](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value=2026&type=daily_treasury_bill_rates). Optimization reference: [PyPortfolioOpt Mean-Variance Optimization](https://pyportfolioopt.readthedocs.io/en/latest/MeanVariance.html).
