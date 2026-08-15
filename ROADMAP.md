# One-Month Project Roadmap

Project period: **August 15–September 14, 2026**. Work is organized around one reviewable milestone per week. Every milestone retains runnable code, automated tests, and a concise research record.

## Week 1: Data acquisition (August 15–21)

Goal: establish a reliable and reproducible market-data entry point.

- [x] Define a cross-sector universe of 15 stocks
- [x] Integrate Yahoo Finance, Alpha Vantage, and Nasdaq Data Link
- [x] Standardize OHLCV, adjusted prices, dividends, and stock splits
- [x] Read API keys from environment variables rather than the repository
- [x] Save a data manifest and SHA-256 hash for reproducibility
- [x] Fetch live Yahoo Finance data and record missingness and observed date coverage
- [ ] Cross-check two or three securities with another provider when the required API key or subscription is available

Acceptance criterion: Yahoo Finance data for all 15 securities can be saved and passes `market-data validate`; AAPL, JPM, and COST are manually spot-checked.

The initial acceptance result is documented in [`reports/part1_data_quality.md`](reports/part1_data_quality.md).

## Week 2: Exploratory analysis and data quality (August 22–28)

Goal: turn provider data into trustworthy research inputs.

- [x] Calculate simple returns, log returns, annualized returns, and annualized volatility
- [x] Check missing trading days, price anomalies, split and dividend effects, and survivorship bias
- [x] Plot normalized prices, return distributions, rolling volatility, and a correlation heat map
- [x] Produce a rerunnable Jupyter notebook and a data-quality report

Acceptance criterion: every figure can be regenerated from a saved CSV, and the analysis clearly distinguishes ordinary close from adjusted close.

## Week 3: Portfolio optimization (August 29–September 4)

Goal: compare asset-allocation methods with explicit assumptions.

- [x] Establish an equal-weight baseline
- [x] Implement minimum-volatility and maximum-Sharpe portfolios with PyPortfolioOpt
- [x] Apply Ledoit–Wolf covariance shrinkage to reduce estimation noise
- [x] Add long-only, single-asset, and sector-exposure constraints
- [x] Record the risk-free-rate source and date without presenting backtest results as future promises

Acceptance criterion: report weights, expected return, volatility, Sharpe ratio, and whether every constraint is satisfied.

## Week 4: Backtesting, robustness, and delivery (September 5–14)

Goal: test the method rather than display a single optimized solution.

- [x] Run a rolling out-of-sample backtest that prevents look-ahead bias
- [x] Add rebalancing-frequency and trading-cost assumptions
- [x] Compare equity curves, drawdowns, and turnover for equal-weight, minimum-volatility, and maximum-Sharpe portfolios
- [x] Test sensitivity to end date, estimation window, and position caps
- [x] Complete the README, figures, conclusions, limitations, and reproduction steps

Acceptance criterion: after installing dependencies in a clean environment, fixed commands rebuild the data, figures, and core findings.

## Daily operating rhythm

- Run the automated research update at 6:00 PM America/Los_Angeles from August 15 through September 14.
- Refresh market data, validate the canonical panel, rerun the analysis, and compare results with the previous successful run.
- Preserve the last successful artifacts if a provider or analysis step fails.
- Write generated files, reports, chart labels, and source-controlled artifacts in English.
- Deliver the short user-facing daily progress update in Chinese.

## GitHub collaboration rhythm

- Create one milestone per week and split each checklist item into a focused issue.
- Develop features on a topic branch and merge through a pull request.
- Require Ruff and pytest to pass; explain changes to research conclusions in the pull-request description.
- Never commit API keys, downloaded provider data, or temporary charts. Small, appropriately licensed test fixtures may be committed.
- Create a dated tag at the end of each week to preserve a reproducible checkpoint.
