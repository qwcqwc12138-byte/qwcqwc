# Python Stock Market Data Analysis and Portfolio Optimization

This educational quantitative-research project provides a complete workflow from **data acquisition → data quality → exploratory analysis → constrained optimization → out-of-sample backtesting → research reporting**. Market data from Yahoo Finance, Alpha Vantage, and Nasdaq Data Link is converted to one canonical long-form schema before entering the tested analysis pipeline.

> This project is for research and education only. It does not constitute investment advice. Market data remains subject to each provider's licensing terms, rate limits, and acceptable-use policies.

## Stock universe (15 companies)

| Sector | Companies and tickers |
| --- | --- |
| Technology | Apple (`AAPL`), Microsoft (`MSFT`), Nvidia (`NVDA`), Alphabet (`GOOGL`), Meta (`META`) |
| Financials | JPMorgan (`JPM`), Goldman Sachs (`GS`), Bank of America (`BAC`), Visa (`V`), Mastercard (`MA`) |
| Consumer | Costco (`COST`), Walmart (`WMT`), Procter & Gamble (`PG`), Coca-Cola (`KO`), Nike (`NKE`) |

The universe is managed in [`config/universe.yaml`](config/universe.yaml), so the securities can be changed without editing the analysis code.

## Quick start

Python 3.11 or newer is required. In PowerShell, run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

To run JupyterLab locally, install the optional notebook dependencies:

```powershell
python -m pip install -e ".[dev,notebook]"
```

Yahoo Finance does not require an API key, so it is the simplest way to verify the full workflow:

```powershell
market-data list-universe
market-data fetch --source yahoo --start 2023-01-01 --end 2026-09-08
market-data validate data/processed/yahoo/prices_2023-01-01_2026-09-08.csv
market-data run-all data/processed/yahoo/prices_2023-01-01_2026-09-08.csv --output-dir artifacts
```

The package can also be invoked without the installed console command:

```powershell
python -m market_portfolio fetch --source yahoo --start 2023-01-01 --end 2026-09-08
```

The pipeline produces:

- canonical CSV data at `data/processed/<source>/prices_<start>_<end>.csv`;
- a traceable JSON manifest containing the provider, tickers, requested dates, row count, and file SHA-256;
- exploratory analysis covering asset metrics, correlations, normalized prices, return distributions, and rolling volatility;
- equal-weight, minimum-volatility, and maximum-Sharpe allocations, sector exposures, and sensitivity results; and
- out-of-sample returns, equity curves, turnover, weight histories, risk metrics, and plots.

Generated files are stored under `artifacts/`, which is ignored by Git. The reproducible notebook is [`notebooks/01_full_research.ipynb`](notebooks/01_full_research.ipynb), and the completed numerical study is [`reports/final_report.md`](reports/final_report.md).

## Method and historical results

The default study uses adjusted closing prices, a 252-trading-day training window, rebalancing every 21 trading days, a 10 bps trading-cost assumption, long-only positions, a 25% single-stock cap, and a 45% sector cap. Covariance is estimated with Ledoit–Wolf shrinkage. The 3.80% risk-free rate is the U.S. Treasury 13-week bill coupon-equivalent rate published for August 14, 2026.

Latest synchronized rolling out-of-sample results from January 4, 2024 through September 8, 2026:

| Strategy | Annualized return | Annualized volatility | Sharpe ratio | Maximum drawdown |
| --- | ---: | ---: | ---: | ---: |
| Equal weight | 24.60% | 14.99% | 1.388 | -20.13% |
| Minimum volatility | 19.62% | 11.92% | 1.328 | -13.72% |
| Maximum Sharpe | 34.82% | 18.30% | 1.695 | -22.35% |

These figures describe one historical sample under specific model assumptions. They are not expected returns or promises of future performance. The maximum-Sharpe strategy is particularly sensitive to expected-return estimates, window selection, and trading costs.

## API keys and provider differences

Store provider keys in `.env`, which is excluded from Git:

```dotenv
ALPHA_VANTAGE_API_KEY=your_key
NASDAQ_DATA_LINK_API_KEY=your_key
```

Then run:

```powershell
market-data fetch --source alpha-vantage --start 2026-05-01 --end 2026-09-08
market-data fetch --source nasdaq-data-link --start 2023-01-01 --end 2026-09-08
```

- **Yahoo Finance:** the project uses the open-source `yfinance` package. It is not an official Yahoo SDK. It is appropriate for research and education, subject to the applicable data terms.
- **Alpha Vantage:** the adapter requests the daily endpoint one ticker at a time. Free plans impose request-frequency and historical-depth limits; the delay between requests is configurable.
- **Nasdaq Data Link:** the default adapter reads the `SHARADAR/SEP` table, which normally requires a corresponding subscription. Users with access to a different table can change `table_code` in the configuration. A Nasdaq Data Link API key does not automatically include all US equity history.

An independent Alpha Vantage spot check compared 100 recent observations for AAPL, JPM, and COST with Yahoo Finance. All 300 rows matched by trading date, 1,198 of 1,200 OHLC values were within 0.01%, and the combined mean absolute OHLC difference was 0.000259%. See [`reports/cross_provider_validation.md`](reports/cross_provider_validation.md) for the full results and limitations. Adjusted prices and corporate actions remain outside the scope of this spot check.

## Canonical data schema

Each row represents one security on one trading day:

`date, ticker, open, high, low, close, adjusted_close, volume, dividend, stock_split, source`

Date, ticker, and close cannot be null. Duplicate `date + ticker + source` keys are removed, and price and volume fields are coerced to numeric values. If adjusted close is unavailable, the pipeline temporarily falls back to ordinary close while retaining the exact provider name.

## Development and testing

```powershell
pytest
ruff check .
```

Unit tests do not access the internet or consume provider quotas. GitHub Actions runs the same checks for every push and pull request.

## Open-source references

- [yfinance](https://github.com/ranaroussi/yfinance): Yahoo Finance data access
- [Alpha Vantage Python wrapper](https://github.com/RomelTorres/alpha_vantage): API usage reference; this project calls the official HTTP endpoints directly so rate limits and errors remain explicit
- [Nasdaq Data Link Python](https://github.com/Nasdaq/data-link-python): official Python client
- [PyPortfolioOpt](https://github.com/PyPortfolio/PyPortfolioOpt): constrained optimization, covariance shrinkage, and portfolio performance calculations

The latest detailed comparison is generated under `artifacts/daily/2026-09-08/summary.md`; generated research artifacts remain outside Git. See [`ROADMAP.md`](ROADMAP.md) for the one-month plan and weekly acceptance criteria. All repository artifacts are maintained in English. The daily Codex progress message is delivered in Chinese for the user.
