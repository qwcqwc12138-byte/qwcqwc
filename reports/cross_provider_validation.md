# Cross-Provider Market Data Validation

- Validation date: September 8, 2026
- Primary provider: Yahoo Finance through `yfinance`
- Independent provider: Alpha Vantage `TIME_SERIES_DAILY`
- Securities: AAPL, JPM, and COST
- Common interval: April 16 through September 8, 2026

## Scope and method

The validation selected one security from each research sector and retrieved the 100 most recent daily observations available from Alpha Vantage's free `compact` response. The normalized Alpha Vantage rows were checked with the project's canonical-schema validator and joined to the synchronized Yahoo Finance panel by ticker and trading date. Comparisons use unadjusted open, high, low, close, and volume because the Alpha Vantage daily endpoint used here does not provide adjusted prices or corporate-action fields.

All 300 Alpha Vantage rows matched a Yahoo Finance row. The independent data set contained no missing values and no duplicate date-and-ticker keys.

## Results

| Ticker | Common rows | Mean absolute close difference | Maximum absolute close difference | Mean absolute OHLC difference | Maximum absolute OHLC difference | Mean absolute volume difference | Maximum absolute volume difference |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| AAPL | 100 | $0.000008 | $0.000015 | 0.000167% | 0.006355% | 0.0424% | 2.4115% |
| JPM | 100 | $0.000007 | $0.000015 | 0.000268% | 0.063266% | 0.0175% | 0.4892% |
| COST | 100 | $0.000066 | $0.005017 | 0.000344% | 0.117680% | 0.0745% | 4.1298% |

Across 1,200 OHLC values, 1,198 were within 0.01% between providers. The combined mean absolute OHLC difference was 0.000259%, and the maximum was 0.117680%. The combined mean absolute volume difference was 0.0448%, with a maximum of 4.1298%.

The closing-price snapshot on the validation date was also consistent:

| Ticker | Alpha Vantage close | Yahoo Finance close |
| --- | ---: | ---: |
| AAPL | $316.22 | $316.220001 |
| JPM | $353.51 | $353.510010 |
| COST | $910.18 | $910.179993 |

## Interpretation

The sampled unadjusted prices are practically consistent across the two providers. The small discrepancies are compatible with decimal precision, intraday corrections, and vendor normalization. Volume differs more than price on a few observations, which is expected when vendors apply different correction timing or consolidate feeds differently. These differences do not invalidate the current sample, but they reinforce the need to retain provider provenance and validation manifests.

## Limitations

- The free Alpha Vantage endpoint limits this check to 100 recent observations per ticker; it does not independently verify the full January 2023–September 2026 history.
- The sample covers three of the fifteen securities and should be interpreted as a spot check, not a complete vendor audit.
- This comparison does not independently verify adjusted close, dividends, or stock splits.
- Nasdaq Data Link reconciliation remains dependent on access to an entitled US-equity data table.

This validation is for research and educational use only and does not constitute investment advice or a guarantee of data accuracy.
