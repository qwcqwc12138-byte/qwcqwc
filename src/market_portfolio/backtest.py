from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from market_portfolio.analysis import TRADING_DAYS, drawdown, simple_returns
from market_portfolio.optimization import PortfolioMethod, optimize_portfolio
from market_portfolio.plotting import configure_matplotlib_cache

configure_matplotlib_cache()
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


@dataclass(frozen=True)
class BacktestResult:
    method: PortfolioMethod
    returns: pd.Series
    equity: pd.Series
    rebalance_weights: pd.DataFrame
    turnover: pd.Series
    metrics: dict[str, float | int | str]


def walk_forward_backtest(
    prices: pd.DataFrame,
    method: PortfolioMethod,
    sector_mapper: dict[str, str],
    training_window: int = 252,
    rebalance_frequency: int = 21,
    transaction_cost_bps: float = 10.0,
    max_weight: float = 0.25,
    sector_cap: float = 0.45,
    risk_free_rate: float = 0.038,
) -> BacktestResult:
    if training_window < 60 or training_window >= len(prices):
        raise ValueError("training_window must be at least 60 and shorter than the price history.")
    if rebalance_frequency < 1:
        raise ValueError("rebalance_frequency must be positive.")

    asset_returns = simple_returns(prices).reindex(prices.index)
    portfolio_segments: list[pd.Series] = []
    weight_records: list[pd.Series] = []
    turnover_records: dict[pd.Timestamp, float] = {}
    prior_ending_weights: pd.Series | None = None
    cost_rate = transaction_cost_bps / 10_000.0

    for start_position in range(training_window, len(prices), rebalance_frequency):
        end_position = min(start_position + rebalance_frequency, len(prices))
        training_prices = prices.iloc[start_position - training_window : start_position]
        solution = optimize_portfolio(
            training_prices,
            method,
            sector_mapper=sector_mapper,
            max_weight=max_weight,
            sector_cap=sector_cap,
            risk_free_rate=risk_free_rate,
        )
        weights = solution.weights.reindex(prices.columns).fillna(0.0)
        rebalance_date = prices.index[start_position]
        weights.name = rebalance_date
        weight_records.append(weights)

        if prior_ending_weights is None:
            turnover = 1.0
        else:
            turnover = float(weights.sub(prior_ending_weights).abs().sum() / 2.0)
        turnover_records[rebalance_date] = turnover

        period_returns = asset_returns.iloc[start_position:end_position].fillna(0.0)
        cumulative_relatives = period_returns.add(1.0).cumprod()
        period_equity = cumulative_relatives.mul(weights, axis=1).sum(axis=1)
        segment_returns = period_equity.pct_change(fill_method=None)
        segment_returns.iloc[0] = float(period_returns.iloc[0].dot(weights))
        segment_returns.iloc[0] -= turnover * cost_rate
        portfolio_segments.append(segment_returns)

        ending_values = weights * cumulative_relatives.iloc[-1]
        prior_ending_weights = ending_values.div(ending_values.sum())

    portfolio_returns = pd.concat(portfolio_segments).sort_index()
    portfolio_returns.name = method
    equity = portfolio_returns.add(1.0).cumprod()
    equity.name = method
    weights_frame = pd.DataFrame(weight_records)
    weights_frame.index.name = "rebalance_date"
    turnover_series = pd.Series(turnover_records, name=method)
    turnover_series.index.name = "rebalance_date"
    metrics = backtest_metrics(
        portfolio_returns,
        turnover_series,
        risk_free_rate=risk_free_rate,
        transaction_cost_bps=transaction_cost_bps,
    )
    return BacktestResult(
        method=method,
        returns=portfolio_returns,
        equity=equity,
        rebalance_weights=weights_frame,
        turnover=turnover_series,
        metrics=metrics,
    )


def backtest_metrics(
    returns: pd.Series,
    turnover: pd.Series,
    risk_free_rate: float,
    transaction_cost_bps: float,
) -> dict[str, float | int | str]:
    equity = returns.add(1.0).cumprod()
    years = len(returns) / TRADING_DAYS
    annual_return = float(equity.iloc[-1] ** (1.0 / years) - 1.0)
    annual_volatility = float(returns.std(ddof=1) * np.sqrt(TRADING_DAYS))
    sharpe = (annual_return - risk_free_rate) / annual_volatility
    return {
        "start": returns.index.min().date().isoformat(),
        "end": returns.index.max().date().isoformat(),
        "observations": len(returns),
        "total_return": float(equity.iloc[-1] - 1.0),
        "annual_return": annual_return,
        "annual_volatility": annual_volatility,
        "sharpe": float(sharpe),
        "max_drawdown": float(drawdown(equity).min()),
        "total_turnover": float(turnover.sum()),
        "rebalance_count": len(turnover),
        "transaction_cost_bps": transaction_cost_bps,
    }


def run_backtests(
    prices: pd.DataFrame,
    sector_mapper: dict[str, str],
    training_window: int = 252,
    rebalance_frequency: int = 21,
    transaction_cost_bps: float = 10.0,
    max_weight: float = 0.25,
    sector_cap: float = 0.45,
    risk_free_rate: float = 0.038,
) -> dict[PortfolioMethod, BacktestResult]:
    methods: tuple[PortfolioMethod, ...] = ("equal_weight", "min_volatility", "max_sharpe")
    return {
        method: walk_forward_backtest(
            prices,
            method,
            sector_mapper=sector_mapper,
            training_window=training_window,
            rebalance_frequency=rebalance_frequency,
            transaction_cost_bps=transaction_cost_bps,
            max_weight=max_weight,
            sector_cap=sector_cap,
            risk_free_rate=risk_free_rate,
        )
        for method in methods
    }


def save_backtest_artifacts(
    results: dict[PortfolioMethod, BacktestResult],
    output_dir: str | Path,
) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    returns = pd.concat([result.returns for result in results.values()], axis=1)
    equity = pd.concat([result.equity for result in results.values()], axis=1)
    metrics = pd.DataFrame({method: result.metrics for method, result in results.items()}).T
    metrics.index.name = "method"
    turnovers = pd.concat([result.turnover for result in results.values()], axis=1)
    weights = pd.concat(
        [result.rebalance_weights.assign(method=method) for method, result in results.items()]
    )

    paths = {
        "returns": output / "backtest_returns.csv",
        "equity": output / "backtest_equity.csv",
        "metrics": output / "backtest_metrics.csv",
        "turnover": output / "backtest_turnover.csv",
        "weights": output / "backtest_weights.csv",
        "chart": output / "backtest_equity.png",
    }
    returns.to_csv(paths["returns"])
    equity.to_csv(paths["equity"])
    metrics.to_csv(paths["metrics"])
    turnovers.to_csv(paths["turnover"])
    weights.to_csv(paths["weights"])

    axis = equity.plot(figsize=(12, 7), linewidth=1.8)
    axis.set(title="Walk-forward Out-of-sample Backtest", ylabel="Growth of $1", xlabel="Date")
    axis.grid(alpha=0.25)
    axis.figure.tight_layout()
    axis.figure.savefig(paths["chart"], dpi=160)
    plt.close(axis.figure)
    return paths
