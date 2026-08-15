import numpy as np
import pandas as pd

from market_portfolio.optimization import optimize_portfolio


def synthetic_prices() -> pd.DataFrame:
    generator = np.random.default_rng(42)
    dates = pd.date_range("2024-01-01", periods=300, freq="B")
    daily_means = np.array([0.0007, 0.0005, 0.0004, 0.0006, 0.0003, 0.00045])
    shocks = generator.normal(daily_means, 0.012, size=(len(dates), len(daily_means)))
    return pd.DataFrame(
        100 * np.exp(np.cumsum(shocks, axis=0)), index=dates, columns=list("ABCDEF")
    )


def test_min_volatility_respects_asset_and_sector_caps() -> None:
    prices = synthetic_prices()
    mapper = {ticker: "one" if ticker in "ABC" else "two" for ticker in prices}

    solution = optimize_portfolio(
        prices,
        "min_volatility",
        sector_mapper=mapper,
        max_weight=0.30,
        sector_cap=0.60,
        risk_free_rate=0.03,
    )

    assert np.isclose(solution.weights.sum(), 1.0)
    assert solution.weights.max() <= 0.30001
    assert solution.sector_exposure.max() <= 0.60001
    assert solution.volatility > 0


def test_equal_weight_is_an_explicit_baseline() -> None:
    prices = synthetic_prices()
    solution = optimize_portfolio(prices, "equal_weight", risk_free_rate=0.03)

    assert np.allclose(solution.weights, np.repeat(1 / 6, 6))
