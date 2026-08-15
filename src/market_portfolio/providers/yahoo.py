from __future__ import annotations

from collections.abc import Sequence
from datetime import date, timedelta

import pandas as pd

from market_portfolio.providers.base import MarketDataError, MarketDataProvider
from market_portfolio.schema import canonicalize


class YahooFinanceProvider(MarketDataProvider):
    name = "yahoo"

    def fetch(self, tickers: Sequence[str], start: date, end: date) -> pd.DataFrame:
        try:
            import yfinance as yf
        except ImportError as exc:
            raise MarketDataError("Install yfinance before using the Yahoo provider.") from exc

        frames: list[pd.DataFrame] = []
        failures: list[str] = []
        # Sequential history calls expose partial failures and avoid shared-download races.
        for ticker in tickers:
            try:
                raw = yf.Ticker(ticker).history(
                    start=start.isoformat(),
                    end=(end + timedelta(days=1)).isoformat(),
                    auto_adjust=False,
                    actions=True,
                    raise_errors=True,
                )
                if raw.empty:
                    failures.append(f"{ticker}: empty response")
                    continue
                frames.append(self._normalize(raw, ticker))
            except Exception as exc:  # provider-specific network and parsing exceptions vary
                failures.append(f"{ticker}: {exc}")

        if not frames:
            detail = "; ".join(failures[:5])
            raise MarketDataError(f"Yahoo Finance returned no usable data. {detail}")

        result = canonicalize(pd.concat(frames, ignore_index=True))
        result.attrs["failures"] = failures
        return result

    @classmethod
    def _normalize(cls, raw: pd.DataFrame, ticker: str) -> pd.DataFrame:
        index = pd.DatetimeIndex(pd.to_datetime(raw.index))
        if index.tz is not None:
            index = index.tz_localize(None)

        def column(name: str, default: object = pd.NA):
            return raw[name].to_numpy() if name in raw else default

        return pd.DataFrame(
            {
                "date": index,
                "ticker": ticker,
                "open": column("Open"),
                "high": column("High"),
                "low": column("Low"),
                "close": column("Close"),
                "adjusted_close": column("Adj Close"),
                "volume": column("Volume"),
                "dividend": column("Dividends", 0.0),
                "stock_split": column("Stock Splits", 0.0),
                "source": cls.name,
            }
        )
