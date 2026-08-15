# Part 1 Data Quality Acceptance Report

- Acceptance date: August 14, 2026 (`America/Los_Angeles`)
- Provider: Yahoo Finance through `yfinance`
- Requested interval: January 1, 2023 through August 14, 2026, inclusive

## Summary

- Requested securities: 15; successfully returned: 15
- Total rows: 13,605
- Observations per security: 907 trading days
- First observed trading day: January 3, 2023
- Last observed trading day: August 14, 2026
- Missing `close` values: 0
- Missing `adjusted_close` values: 0
- Duplicate `date + ticker + source` keys: 0
- Canonical schema validation: passed

## Security-level coverage

| Ticker | Rows | First date | Last date |
| --- | ---: | --- | --- |
| AAPL | 907 | 2023-01-03 | 2026-08-14 |
| BAC | 907 | 2023-01-03 | 2026-08-14 |
| COST | 907 | 2023-01-03 | 2026-08-14 |
| GOOGL | 907 | 2023-01-03 | 2026-08-14 |
| GS | 907 | 2023-01-03 | 2026-08-14 |
| JPM | 907 | 2023-01-03 | 2026-08-14 |
| KO | 907 | 2023-01-03 | 2026-08-14 |
| MA | 907 | 2023-01-03 | 2026-08-14 |
| META | 907 | 2023-01-03 | 2026-08-14 |
| MSFT | 907 | 2023-01-03 | 2026-08-14 |
| NKE | 907 | 2023-01-03 | 2026-08-14 |
| NVDA | 907 | 2023-01-03 | 2026-08-14 |
| PG | 907 | 2023-01-03 | 2026-08-14 |
| V | 907 | 2023-01-03 | 2026-08-14 |
| WMT | 907 | 2023-01-03 | 2026-08-14 |

## Interpretation and next step

Identical row counts indicate no obvious security-specific coverage gaps over this interval, but they do not replace cross-provider price verification. When the required API key or subscription is available, the next step is to compare a sample of AAPL, JPM, and COST observations with Alpha Vantage or Nasdaq Data Link and record differences in price conventions, retrieval time, and data licensing.

The downloaded CSV and manifest are stored under `data/processed/yahoo/` and excluded through `.gitignore`. The repository retains this acceptance summary but does not commit raw provider data.
