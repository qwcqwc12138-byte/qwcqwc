from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from market_portfolio.analysis import (
    adjusted_price_matrix,
    data_quality_summary,
    generate_eda_artifacts,
    load_market_csv,
)
from market_portfolio.backtest import BacktestResult, run_backtests, save_backtest_artifacts
from market_portfolio.config import ProjectConfig
from market_portfolio.optimization import (
    PortfolioMethod,
    PortfolioSolution,
    optimize_all,
    run_sensitivity,
    save_solution_tables,
    sector_mapper_from_config,
)

DEFAULT_RISK_FREE_RATE = 0.038
RISK_FREE_RATE_DATE = "2026-08-14"
RISK_FREE_RATE_SOURCE = (
    "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
    "TextView?field_tdr_date_value=2026&type=daily_treasury_bill_rates"
)


@dataclass(frozen=True)
class ResearchResult:
    quality: dict[str, object]
    solutions: dict[PortfolioMethod, PortfolioSolution]
    backtests: dict[PortfolioMethod, BacktestResult]
    sensitivity: pd.DataFrame
    artifacts: dict[str, Path]


def run_full_research(
    data_path: str | Path,
    config: ProjectConfig,
    output_dir: str | Path = "artifacts",
    risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
    training_window: int = 252,
    rebalance_frequency: int = 21,
    transaction_cost_bps: float = 10.0,
    max_weight: float = 0.25,
    sector_cap: float = 0.45,
) -> ResearchResult:
    output = Path(output_dir)
    frame = load_market_csv(data_path)
    prices = adjusted_price_matrix(frame)
    mapper = sector_mapper_from_config(config)
    mapper = {ticker: mapper[ticker] for ticker in prices.columns}

    eda_artifacts = generate_eda_artifacts(
        frame,
        output / "eda",
        risk_free_rate=risk_free_rate,
    )
    artifacts = {f"eda_{name}": path for name, path in eda_artifacts.items()}
    solutions = optimize_all(
        prices,
        mapper,
        max_weight=max_weight,
        sector_cap=sector_cap,
        risk_free_rate=risk_free_rate,
    )
    optimization_artifacts = save_solution_tables(solutions, mapper, output / "optimization")
    artifacts.update(
        {f"optimization_{name}": path for name, path in optimization_artifacts.items()}
    )
    sensitivity = run_sensitivity(
        prices,
        mapper,
        risk_free_rate=risk_free_rate,
        sector_cap=sector_cap,
    )
    sensitivity_path = output / "optimization" / "sensitivity.csv"
    sensitivity.to_csv(sensitivity_path, index=False)
    artifacts["sensitivity"] = sensitivity_path

    backtests = run_backtests(
        prices,
        mapper,
        training_window=training_window,
        rebalance_frequency=rebalance_frequency,
        transaction_cost_bps=transaction_cost_bps,
        max_weight=max_weight,
        sector_cap=sector_cap,
        risk_free_rate=risk_free_rate,
    )
    backtest_artifacts = save_backtest_artifacts(backtests, output / "backtest")
    artifacts.update({f"backtest_{name}": path for name, path in backtest_artifacts.items()})
    return ResearchResult(
        quality=data_quality_summary(frame),
        solutions=solutions,
        backtests=backtests,
        sensitivity=sensitivity,
        artifacts=artifacts,
    )
