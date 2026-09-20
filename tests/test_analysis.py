import pandas as pd

from market_portfolio.analysis import (
    adjusted_price_matrix,
    asset_performance_summary,
    data_quality_summary,
)


def canonical_sample() -> pd.DataFrame:
    dates = pd.date_range("2025-01-01", periods=5, freq="B")
    records = []
    for ticker, prices in {"AAA": [100, 101, 102, 103, 104], "BBB": [50, 49, 51, 52, 53]}.items():
        for day, price in zip(dates, prices, strict=True):
            records.append(
                {
                    "date": day,
                    "ticker": ticker,
                    "close": price,
                    "adjusted_close": price,
                    "source": "test",
                }
            )
    return pd.DataFrame(records)


def test_price_matrix_and_quality_summary() -> None:
    frame = canonical_sample()

    prices = adjusted_price_matrix(frame)
    quality = data_quality_summary(frame)

    assert prices.shape == (5, 2)
    assert quality["panel_coverage"] == 1.0
    assert quality["duplicate_keys"] == 0
    assert quality["invalid_ohlc_rows"] == 0
    assert quality["extreme_adjusted_returns"] == 0


def test_asset_performance_summary_has_risk_metrics() -> None:
    result = asset_performance_summary(adjusted_price_matrix(canonical_sample()))

    assert set(result.columns) >= {
        "annual_return",
        "annual_volatility",
        "sharpe",
        "max_drawdown",
    }
    assert result["observations"].eq(4).all()
