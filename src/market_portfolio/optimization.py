from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
from pypfopt import EfficientFrontier, base_optimizer, expected_returns, risk_models

PortfolioMethod = Literal["equal_weight", "min_volatility", "max_sharpe"]


@dataclass(frozen=True)
class PortfolioSolution:
    method: PortfolioMethod
    weights: pd.Series
    expected_return: float
    volatility: float
    sharpe: float
    sector_exposure: pd.Series


def sector_mapper_from_config(config) -> dict[str, str]:
    return {asset.ticker: asset.sector for asset in config.universe}


def estimate_moments(prices: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    if len(prices) < 60:
        raise ValueError("At least 60 price observations are required for optimization.")
    mu = expected_returns.mean_historical_return(prices, frequency=252, compounding=True)
    covariance = risk_models.CovarianceShrinkage(prices, frequency=252).ledoit_wolf()
    return mu, covariance


def optimize_portfolio(
    prices: pd.DataFrame,
    method: PortfolioMethod,
    sector_mapper: dict[str, str] | None = None,
    max_weight: float = 0.25,
    sector_cap: float = 0.45,
    risk_free_rate: float = 0.038,
) -> PortfolioSolution:
    if not 0 < max_weight <= 1:
        raise ValueError("max_weight must be in (0, 1].")
    if max_weight * prices.shape[1] < 1 - 1e-9:
        raise ValueError("max_weight is infeasible for the number of assets.")

    mu, covariance = estimate_moments(prices)
    tickers = prices.columns.tolist()
    mapper = {ticker: sector_mapper[ticker] for ticker in tickers} if sector_mapper else {}

    if method == "equal_weight":
        weights = pd.Series(1.0 / len(tickers), index=tickers, name=method)
    else:
        frontier = EfficientFrontier(mu, covariance, weight_bounds=(0.0, max_weight))
        if mapper:
            sectors = sorted(set(mapper.values()))
            frontier.add_sector_constraints(
                mapper,
                sector_lower={},
                sector_upper={sector: sector_cap for sector in sectors},
            )
        if method == "min_volatility":
            frontier.min_volatility()
        elif method == "max_sharpe":
            frontier.max_sharpe(risk_free_rate=risk_free_rate)
        else:
            raise ValueError(f"Unsupported portfolio method: {method}")
        weights = pd.Series(frontier.weights, index=tickers, name=method)
        weights[weights.abs() < 1e-10] = 0.0
        weights = weights.div(weights.sum())

    expected_return, volatility, sharpe = base_optimizer.portfolio_performance(
        weights.to_numpy(),
        mu,
        covariance,
        risk_free_rate=risk_free_rate,
    )
    sector_exposure = _sector_exposure(weights, mapper)
    _validate_solution(weights, sector_exposure, max_weight, sector_cap)
    return PortfolioSolution(
        method=method,
        weights=weights,
        expected_return=float(expected_return),
        volatility=float(volatility),
        sharpe=float(sharpe),
        sector_exposure=sector_exposure,
    )


def optimize_all(
    prices: pd.DataFrame,
    sector_mapper: dict[str, str],
    max_weight: float = 0.25,
    sector_cap: float = 0.45,
    risk_free_rate: float = 0.038,
) -> dict[PortfolioMethod, PortfolioSolution]:
    methods: tuple[PortfolioMethod, ...] = ("equal_weight", "min_volatility", "max_sharpe")
    return {
        method: optimize_portfolio(
            prices,
            method,
            sector_mapper=sector_mapper,
            max_weight=max_weight,
            sector_cap=sector_cap,
            risk_free_rate=risk_free_rate,
        )
        for method in methods
    }


def solution_tables(
    solutions: dict[PortfolioMethod, PortfolioSolution],
    sector_mapper: dict[str, str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    weight_records = []
    metric_records = []
    sector_records = []
    for method, solution in solutions.items():
        for ticker, weight in solution.weights.items():
            weight_records.append(
                {
                    "method": method,
                    "ticker": ticker,
                    "sector": sector_mapper.get(ticker, "Unknown"),
                    "weight": weight,
                }
            )
        metric_records.append(
            {
                "method": method,
                "expected_return": solution.expected_return,
                "volatility": solution.volatility,
                "sharpe": solution.sharpe,
                "max_weight": solution.weights.max(),
            }
        )
        for sector, weight in solution.sector_exposure.items():
            sector_records.append({"method": method, "sector": sector, "weight": weight})
    return (
        pd.DataFrame(weight_records),
        pd.DataFrame(metric_records).set_index("method"),
        pd.DataFrame(sector_records),
    )


def save_solution_tables(
    solutions: dict[PortfolioMethod, PortfolioSolution],
    sector_mapper: dict[str, str],
    output_dir: str | Path,
) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    weights, metrics, sectors = solution_tables(solutions, sector_mapper)
    paths = {
        "weights": output / "portfolio_weights.csv",
        "metrics": output / "portfolio_metrics.csv",
        "sectors": output / "sector_exposures.csv",
    }
    weights.to_csv(paths["weights"], index=False)
    metrics.to_csv(paths["metrics"])
    sectors.to_csv(paths["sectors"], index=False)
    return paths


def run_sensitivity(
    prices: pd.DataFrame,
    sector_mapper: dict[str, str],
    risk_free_rate: float = 0.038,
    lookbacks: tuple[int, ...] = (126, 252, 504),
    end_offsets: tuple[int, ...] = (0, 63),
    max_weights: tuple[float, ...] = (0.20, 0.25, 0.35),
    sector_cap: float = 0.45,
) -> pd.DataFrame:
    records = []
    for end_offset in end_offsets:
        available = prices.iloc[: len(prices) - end_offset] if end_offset else prices
        for lookback in lookbacks:
            sample = available.tail(min(lookback, len(available)))
            for max_weight in max_weights:
                solution = optimize_portfolio(
                    sample,
                    "max_sharpe",
                    sector_mapper=sector_mapper,
                    max_weight=max_weight,
                    sector_cap=sector_cap,
                    risk_free_rate=risk_free_rate,
                )
                records.append(
                    {
                        "start_date": sample.index.min().date().isoformat(),
                        "end_date": sample.index.max().date().isoformat(),
                        "end_offset": end_offset,
                        "lookback": lookback,
                        "observations_used": len(sample),
                        "max_weight_constraint": max_weight,
                        "expected_return": solution.expected_return,
                        "volatility": solution.volatility,
                        "sharpe": solution.sharpe,
                        "largest_weight": solution.weights.max(),
                    }
                )
    return pd.DataFrame(records)


def _sector_exposure(weights: pd.Series, mapper: dict[str, str]) -> pd.Series:
    if not mapper:
        return pd.Series(dtype=float, name="weight")
    frame = pd.DataFrame(
        {"weight": weights, "sector": [mapper[ticker] for ticker in weights.index]},
        index=weights.index,
    )
    exposure = frame.groupby("sector")["weight"].sum().sort_index()
    exposure.name = "weight"
    return exposure


def _validate_solution(
    weights: pd.Series,
    sector_exposure: pd.Series,
    max_weight: float,
    sector_cap: float,
) -> None:
    tolerance = 1e-5
    if not np.isclose(weights.sum(), 1.0, atol=tolerance):
        raise ValueError("Portfolio weights do not sum to one.")
    if weights.min() < -tolerance:
        raise ValueError("Long-only portfolio contains a negative weight.")
    if weights.max() > max_weight + tolerance:
        raise ValueError("Portfolio violates the single-asset weight cap.")
    if not sector_exposure.empty and sector_exposure.max() > sector_cap + tolerance:
        raise ValueError("Portfolio violates the sector weight cap.")
