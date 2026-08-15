from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import date

import pandas as pd


class MarketDataError(RuntimeError):
    """Readable error returned by a market data provider."""


class MarketDataProvider(ABC):
    name: str

    @abstractmethod
    def fetch(self, tickers: Sequence[str], start: date, end: date) -> pd.DataFrame:
        """Fetch and normalize daily market data for an inclusive date range."""
