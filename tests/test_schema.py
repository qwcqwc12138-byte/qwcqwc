import pandas as pd
import pytest

from market_portfolio.schema import DataValidationError, canonicalize


def test_canonicalize_sorts_deduplicates_and_fills_adjusted_close() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2026-01-03", "2026-01-02", "2026-01-02"],
            "ticker": [" aapl ", "AAPL", "AAPL"],
            "close": [102, 100, 101],
            "volume": [30, 10, 20],
            "source": ["test", "test", "test"],
        }
    )

    result = canonicalize(frame)

    assert result["date"].dt.strftime("%Y-%m-%d").tolist() == ["2026-01-02", "2026-01-03"]
    assert result["close"].tolist() == [101, 102]
    assert result["adjusted_close"].tolist() == [101, 102]
    assert result["ticker"].tolist() == ["AAPL", "AAPL"]


def test_canonicalize_rejects_non_positive_close() -> None:
    frame = pd.DataFrame(
        {"date": ["2026-01-02"], "ticker": ["AAPL"], "close": [0], "source": ["test"]}
    )

    with pytest.raises(DataValidationError, match="positive"):
        canonicalize(frame)
