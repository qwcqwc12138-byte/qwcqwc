from __future__ import annotations

import time
from collections.abc import Sequence
from datetime import date
from typing import Any

import pandas as pd
import requests

from market_portfolio.providers.base import MarketDataError, MarketDataProvider
from market_portfolio.schema import canonicalize


class AlphaVantageProvider(MarketDataProvider):
    name = "alpha_vantage"
    endpoint = "https://www.alphavantage.co/query"

    def __init__(
        self,
        api_key: str,
        request_delay_seconds: float = 12.5,
        output_size: str = "full",
        session: requests.Session | None = None,
    ) -> None:
        if not api_key:
            raise MarketDataError("ALPHA_VANTAGE_API_KEY is required.")
        if output_size not in {"compact", "full"}:
            raise ValueError("Alpha Vantage output_size must be 'compact' or 'full'.")
        self.api_key = api_key
        self.request_delay_seconds = max(0.0, request_delay_seconds)
        self.output_size = output_size
        self.session = session or requests.Session()

    def fetch(self, tickers: Sequence[str], start: date, end: date) -> pd.DataFrame:
        frames: list[pd.DataFrame] = []
        for position, ticker in enumerate(tickers):
            if position and self.request_delay_seconds:
                time.sleep(self.request_delay_seconds)
            try:
                response = self.session.get(
                    self.endpoint,
                    params={
                        "function": "TIME_SERIES_DAILY",
                        "symbol": ticker,
                        "outputsize": self.output_size,
                        "datatype": "json",
                        "apikey": self.api_key,
                    },
                    timeout=30,
                )
                response.raise_for_status()
                payload = response.json()
            except (requests.RequestException, ValueError) as exc:
                raise MarketDataError(f"Alpha Vantage request failed for {ticker}: {exc}") from exc
            frame = self._parse_payload(payload, ticker)
            mask = frame["date"].between(pd.Timestamp(start), pd.Timestamp(end), inclusive="both")
            frames.append(frame.loc[mask])

        return canonicalize(pd.concat(frames, ignore_index=True))

    @classmethod
    def _parse_payload(cls, payload: dict[str, Any], ticker: str) -> pd.DataFrame:
        for key in ("Error Message", "Information", "Note"):
            if key in payload:
                raise MarketDataError(f"Alpha Vantage response for {ticker}: {payload[key]}")

        series = payload.get("Time Series (Daily)")
        if not isinstance(series, dict) or not series:
            raise MarketDataError(f"Alpha Vantage returned no daily series for {ticker}.")

        records = []
        for day, values in series.items():
            records.append(
                {
                    "date": day,
                    "ticker": ticker,
                    "open": values.get("1. open"),
                    "high": values.get("2. high"),
                    "low": values.get("3. low"),
                    "close": values.get("4. close"),
                    "adjusted_close": values.get("5. adjusted close", values.get("4. close")),
                    "volume": values.get("6. volume", values.get("5. volume")),
                    "dividend": values.get("7. dividend amount", 0.0),
                    "stock_split": values.get("8. split coefficient", 0.0),
                    "source": cls.name,
                }
            )
        return canonicalize(pd.DataFrame.from_records(records))
