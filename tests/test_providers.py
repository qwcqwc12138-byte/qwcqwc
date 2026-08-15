import pandas as pd
import pytest

from market_portfolio.providers.alpha_vantage import AlphaVantageProvider
from market_portfolio.providers.base import MarketDataError
from market_portfolio.providers.nasdaq_data_link import NasdaqDataLinkProvider
from market_portfolio.providers.yahoo import YahooFinanceProvider
from market_portfolio.schema import canonicalize


def test_alpha_vantage_daily_payload_is_normalized() -> None:
    payload = {
        "Time Series (Daily)": {
            "2026-08-13": {
                "1. open": "100.0",
                "2. high": "103.0",
                "3. low": "99.0",
                "4. close": "102.0",
                "5. volume": "12345",
            }
        }
    }

    result = AlphaVantageProvider._parse_payload(payload, "aapl")

    assert result.loc[0, "ticker"] == "AAPL"
    assert result.loc[0, "close"] == 102.0
    assert result.loc[0, "adjusted_close"] == 102.0
    assert result.loc[0, "volume"] == 12345


def test_alpha_vantage_rate_limit_message_becomes_error() -> None:
    with pytest.raises(MarketDataError, match="rate limit"):
        AlphaVantageProvider._parse_payload({"Note": "rate limit reached"}, "AAPL")


def test_nasdaq_sharadar_columns_are_normalized() -> None:
    raw = pd.DataFrame(
        {
            "ticker": ["AAPL"],
            "date": ["2026-08-13"],
            "open": [100.0],
            "high": [103.0],
            "low": [99.0],
            "close": [102.0],
            "closeadj": [101.5],
            "volume": [12345],
        }
    )

    result = NasdaqDataLinkProvider._normalize(raw, "AAPL")

    assert result.loc[0, "adjusted_close"] == 101.5
    assert result.loc[0, "source"] == "nasdaq_data_link"


def test_yahoo_timezone_and_actions_are_normalized() -> None:
    index = pd.DatetimeIndex(["2026-08-13 00:00:00"], tz="America/New_York")
    raw = pd.DataFrame(
        {
            "Open": [100.0],
            "High": [103.0],
            "Low": [99.0],
            "Close": [102.0],
            "Adj Close": [101.5],
            "Volume": [12345],
            "Dividends": [0.25],
            "Stock Splits": [0.0],
        },
        index=index,
    )

    result = canonicalize(YahooFinanceProvider._normalize(raw, "aapl"))

    assert result.loc[0, "date"] == pd.Timestamp("2026-08-13")
    assert result.loc[0, "ticker"] == "AAPL"
    assert result.loc[0, "dividend"] == 0.25
