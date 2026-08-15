from __future__ import annotations

from collections.abc import Sequence
from datetime import date

import pandas as pd

from market_portfolio.providers.base import MarketDataError, MarketDataProvider
from market_portfolio.schema import canonicalize


class NasdaqDataLinkProvider(MarketDataProvider):
    name = "nasdaq_data_link"

    def __init__(self, api_key: str, table_code: str = "SHARADAR/SEP") -> None:
        if not api_key:
            raise MarketDataError("NASDAQ_DATA_LINK_API_KEY is required.")
        self.api_key = api_key
        self.table_code = table_code

    def fetch(self, tickers: Sequence[str], start: date, end: date) -> pd.DataFrame:
        try:
            import nasdaqdatalink
        except ImportError as exc:
            raise MarketDataError(
                "Install nasdaq-data-link before using the Nasdaq Data Link provider."
            ) from exc

        nasdaqdatalink.ApiConfig.api_key = self.api_key
        frames: list[pd.DataFrame] = []
        for ticker in tickers:
            try:
                raw = nasdaqdatalink.get_table(
                    self.table_code,
                    ticker=ticker,
                    date={"gte": start.isoformat(), "lte": end.isoformat()},
                    paginate=True,
                )
            except Exception as exc:
                raise MarketDataError(
                    f"Nasdaq Data Link failed for {ticker} using {self.table_code}. "
                    "Confirm the table subscription and API key."
                ) from exc
            if raw.empty:
                continue
            frames.append(self._normalize(raw, ticker))

        if not frames:
            raise MarketDataError(
                f"Nasdaq Data Link table {self.table_code} returned no data "
                "for the requested range."
            )
        return canonicalize(pd.concat(frames, ignore_index=True))

    @classmethod
    def _normalize(cls, raw: pd.DataFrame, fallback_ticker: str) -> pd.DataFrame:
        columns = {str(column).lower(): column for column in raw.columns}

        def values(*candidates: str, default: object = pd.NA):
            for candidate in candidates:
                if candidate in columns:
                    return raw[columns[candidate]].to_numpy()
            return default

        return canonicalize(
            pd.DataFrame(
                {
                    "date": values("date"),
                    "ticker": values("ticker", default=fallback_ticker),
                    "open": values("open", "openunadj"),
                    "high": values("high", "highunadj"),
                    "low": values("low", "lowunadj"),
                    "close": values("close", "closeunadj"),
                    "adjusted_close": values("closeadj", "adj_close", "adjusted_close"),
                    "volume": values("volume", "volumeunadj"),
                    "dividend": values("dividend", "dividends", default=0.0),
                    "stock_split": values("split", "splitratio", default=0.0),
                    "source": cls.name,
                }
            )
        )
