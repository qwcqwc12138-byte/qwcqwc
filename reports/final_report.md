# Stock Market Analysis and Portfolio Optimization: Final Research Report

- Final research date: September 14, 2026 (`America/Los_Angeles`)
- Data interval: January 3, 2023 through September 14, 2026
- Securities: 15 across technology, financials, and consumer companies
- Validated observations: 13,905 rows across 927 trading dates
- One-month project status: 31 of 31 dated daily runs completed
- Purpose: research and education; not investment advice

## 1. Executive Summary

This project delivers a reproducible Python workflow from multi-provider market-data acquisition and validation through exploratory analysis, constrained mean-variance optimization, sensitivity testing, and rolling out-of-sample backtesting. The final Yahoo Finance panel contains 13,905 observations, with complete ordinary and adjusted closing prices and no duplicate ticker-date keys. One dated research package was retained for every calendar day from August 15 through September 14, including weekend audit runs that used the latest available market session.

In the final out-of-sample backtest, the maximum-Sharpe strategy produced the highest historical annualized return and Sharpe ratio. It also produced the highest volatility, largest drawdown magnitude, and greatest turnover. The minimum-volatility strategy produced a lower return but the lowest volatility and smallest drawdown. These results illustrate a historical risk-return tradeoff; they do not establish future performance.

| Strategy | Cumulative return | Annualized return | Annualized volatility | Sharpe ratio | Maximum drawdown | Total turnover |
|---|---:|---:|---:|---:|---:|---:|
| Equal weight | 80.58% | 24.69% | 14.95% | 1.397 | -20.13% | 1.79 |
| Minimum volatility | 61.28% | 19.54% | 11.90% | 1.323 | -13.72% | 3.12 |
| Maximum Sharpe | 121.33% | 34.53% | 18.27% | 1.682 | -22.35% | 7.35 |

## 2. Data, Providers, and Validation

- **Universe:** 15 stocks divided equally among technology, financials, and consumer companies.
- **Primary research source:** Yahoo Finance through the open-source `yfinance` package.
- **Canonical schema:** date, ticker, OHLC, adjusted close, volume, dividend, stock split, and source.
- **Panel quality:** each security has 927 observations; ordinary close and adjusted close are complete; duplicate canonical keys are zero.
- **Corporate actions:** the final panel contains 215 cash-dividend events and two stock-split events.
- **Reproducibility:** every saved provider snapshot has a JSON manifest and SHA-256 digest.

The final September 14 data file has SHA-256 digest `a57653a7a9e754e58f9f76fc274f7b208e9ac11731d244726b764341190e3f15`. Generated provider files and daily research artifacts are intentionally excluded from Git, while the workflow, configuration, tests, and conclusions are source controlled.

### Independent Provider Check

An Alpha Vantage spot check independently compared 100 recent observations for AAPL, JPM, and COST with Yahoo Finance. All 300 observations matched by ticker and trading date. Of 1,200 compared OHLC values, 1,198 differed by no more than 0.01%, and the combined mean absolute OHLC difference was 0.000259%. Volume showed larger but still limited provider differences. The full method and results are documented in [`cross_provider_validation.md`](cross_provider_validation.md).

The spot check does not independently verify adjusted close, corporate actions, the other twelve securities, or the entire January 2023–September 2026 history. Nasdaq Data Link support is implemented, but complete reconciliation requires access to an entitled US-equity table.

## 3. Exploratory Analysis

The synchronized final outputs are stored locally under `artifacts/daily/2026-09-14/eda/`. They include normalized adjusted prices, asset-level return and risk statistics, return correlations, 63-day rolling annualized volatility, and daily-return distributions.

NVDA had the highest full-period annualized return at 108.14% and the highest annualized volatility at 48.34%. NKE had a -25.58% annualized return and a -69.39% maximum drawdown. This dispersion demonstrates why historical winners can dominate unconstrained estimates and why the portfolio model applies both stock and sector caps.

The final panel contains approximately 3.7 years of history. That interval includes meaningful market variation but not multiple complete economic cycles, so estimates remain sensitive to the selected sample.

## 4. Optimization Method and Final Allocations

The optimization workflow uses:

- historical compound returns as expected-return estimates;
- Ledoit-Wolf covariance shrinkage;
- equal-weight, minimum-volatility, and maximum-Sharpe portfolios;
- long-only weights that sum to one;
- a 25% maximum weight per security;
- a 45% maximum exposure per research sector; and
- a 3.80% risk-free rate based on the U.S. Treasury 13-week bill coupon-equivalent rate published for August 14, 2026.

The following estimates use the complete sample through September 14 and are in-sample results, not forecasts.

| Strategy | Estimated annualized return | Estimated volatility | Estimated Sharpe ratio | Largest stock weight |
|---|---:|---:|---:|---:|
| Equal weight | 28.52% | 14.50% | 1.705 | 6.67% |
| Minimum volatility | 20.63% | 11.69% | 1.441 | 25.00% |
| Maximum Sharpe | 47.98% | 16.92% | 2.612 | 25.00% |

The final maximum-Sharpe allocation is:

| Security | Weight |
|---|---:|
| KO | 25.00% |
| NVDA | 25.00% |
| WMT | 20.00% |
| JPM | 15.63% |
| GOOGL | 8.82% |
| META | 5.55% |

All other maximum-Sharpe weights are zero. The final minimum-volatility portfolio is led by KO at 25.00%, PG at 15.58%, V at 12.92%, MSFT at 11.99%, and JPM at 11.23%. Both optimized portfolios reach the 45% consumer-sector cap, confirming that the constraint is active.

## 5. Out-of-Sample Backtest Design

- **Training window:** most recent 252 trading observations.
- **Rebalancing:** every 21 observations.
- **Test period:** January 4, 2024 through September 14, 2026.
- **Test observations:** 675.
- **Rebalances:** 33 per strategy.
- **Trading costs:** 10 basis points per unit of turnover; the initial allocation from cash is treated as 100% turnover.
- **Look-ahead control:** every target allocation is estimated only from information available before its holding period.
- **Holdings treatment:** weights drift with asset returns between rebalances rather than being reset daily.

The maximum-Sharpe strategy's turnover of 7.35 is materially higher than equal weight at 1.79 and minimum volatility at 3.12. Its historical advantage is therefore more exposed to transaction costs, slippage, estimation error, and implementation constraints than the headline return alone suggests.

## 6. Sensitivity Analysis

The final sensitivity grid varies sample end date, estimation window, and individual-stock cap across 18 scenarios. All scenarios completed with finite results and respected their tested position limits.

| Measure | Minimum | Maximum |
|---|---:|---:|
| Fitted annualized return | 32.49% | 64.61% |
| Fitted annualized volatility | 12.41% | 16.61% |
| Fitted Sharpe ratio | 1.884 | 4.164 |

The dispersion remains material. Maximum-Sharpe allocations and fitted performance should therefore be interpreted as model outputs conditional on a particular sample and constraint set. A production decision process should pre-register its windows, costs, and limits and validate them across more market regimes.

## 7. One-Month Operating Record

The project retained 31 dated daily packages from August 15 through September 14. Every package contains the complete research workflow plus an English comparison with the previous successful run. Weekend and holiday packages correctly retain the latest observed trading date while still recording provider revisions, validation results, and model outputs.

The closing September 14 package contains 17 nonempty files across EDA, optimization, sensitivity analysis, backtesting, and the daily summary. No API key, downloaded provider data, or generated chart is committed to the repository.

## 8. Limitations

- The universe uses current companies and therefore contains survivorship bias while excluding delisted securities.
- The historical sample does not span multiple complete economic cycles.
- Historical mean returns are noisy estimates; maximum-Sharpe optimization is especially sensitive to them.
- The backtest does not model bid-ask spreads, market impact, taxes, fractional-share constraints, or capacity limits.
- Sector labels are simplified research categories rather than official GICS classifications.
- Yahoo's most recent observations and historical adjusted prices can be revised after retrieval.
- Independent provider reconciliation covers only three securities, 100 recent unadjusted observations per security, and no corporate actions.
- Historical and simulated results do not represent expected future returns.

## 9. Reproduction

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
market-data fetch --source yahoo --start 2023-01-01 --end 2026-09-14
market-data validate data/processed/yahoo/prices_2023-01-01_2026-09-14.csv
market-data run-all data/processed/yahoo/prices_2023-01-01_2026-09-14.csv --output-dir artifacts/daily/2026-09-14
pytest
ruff check src tests
```

Risk-free-rate source: [U.S. Treasury Daily Treasury Bill Rates](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?field_tdr_date_value=2026&type=daily_treasury_bill_rates). Optimization reference: [PyPortfolioOpt Mean-Variance Optimization](https://pyportfolioopt.readthedocs.io/en/latest/MeanVariance.html).

## 10. Conclusion

The project achieved its intended outcome: a reproducible, tested, provider-aware stock-research pipeline with explicit constraints, daily audit records, independent price spot checks, and out-of-sample evaluation. The strongest historical performance came from the maximum-Sharpe strategy, but its concentration, turnover, volatility, and sensitivity prevent the result from being interpreted as a general investment recommendation. The minimum-volatility and equal-weight results provide essential baselines that make this tradeoff visible.

This report and the accompanying website are for research and educational use only. They do not constitute investment advice, an offer, or a recommendation to buy or sell any security.
