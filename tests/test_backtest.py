import numpy as np
import pandas as pd

from market_portfolio.backtest import walk_forward_backtest


def test_walk_forward_starts_after_training_window_and_charges_costs() -> None:
    dates = pd.date_range("2023-01-02", periods=180, freq="B")
    daily = np.tile([0.0004, 0.0003, 0.0002, 0.0005], (len(dates), 1))
    prices = pd.DataFrame(
        100 * np.cumprod(1 + daily, axis=0),
        index=dates,
        columns=["A", "B", "C", "D"],
    )
    mapper = {"A": "one", "B": "one", "C": "two", "D": "two"}

    result = walk_forward_backtest(
        prices,
        "equal_weight",
        mapper,
        training_window=100,
        rebalance_frequency=20,
        transaction_cost_bps=10,
        max_weight=0.30,
        sector_cap=0.60,
        risk_free_rate=0.0,
    )

    assert result.returns.index.min() == dates[100]
    assert result.metrics["observations"] == 80
    assert result.metrics["rebalance_count"] == 4
    assert result.turnover.iloc[0] == 1.0
    assert result.equity.index.equals(result.returns.index)
