# Market Portfolio Lab website

The English-language project site for the Python stock-market data analysis and
portfolio-optimization research repository.

## What the site covers

- a 15-stock universe across technology, financials, and consumer companies;
- data acquisition through Yahoo Finance, Alpha Vantage, and Nasdaq Data Link;
- schema validation and reproducibility controls;
- a 300-row Alpha Vantage spot check for AAPL, JPM, and COST;
- constrained equal-weight, minimum-volatility, and maximum-Sharpe portfolios;
- rolling out-of-sample backtests and documented research limitations; and
- the August 15–September 14, 2026 daily research window.

The published snapshot is synchronized through September 8, 2026: 25 daily runs
are complete, the validated Yahoo Finance panel contains 13,845 rows, and the
latest observed trading date is September 8.

The independent provider check matched all 300 Alpha Vantage observations to
Yahoo Finance trading dates. Of 1,200 compared OHLC values, 1,198 were within
0.01%. This limited check does not independently verify adjusted prices or
corporate actions.

All performance figures are historical research results. The site is for
research and education and does not provide investment advice.

## Local development

Requires Node.js 22.13 or newer.

```bash
pnpm install
pnpm run dev
pnpm run build
pnpm test
```

The page content is in `app/page.tsx`, styling is in `app/globals.css`, and the
social preview is `public/og.png`.
