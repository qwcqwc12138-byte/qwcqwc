from __future__ import annotations

import argparse
from collections.abc import Sequence
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from market_portfolio.config import load_config
from market_portfolio.pipeline import fetch_market_data, save_dataset
from market_portfolio.providers.base import MarketDataError
from market_portfolio.research import DEFAULT_RISK_FREE_RATE, run_full_research
from market_portfolio.schema import DataValidationError, canonicalize


def _iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use ISO date format YYYY-MM-DD.") from exc


def build_parser() -> argparse.ArgumentParser:
    today = date.today()
    parser = argparse.ArgumentParser(description="Market data acquisition for the portfolio lab")
    parser.add_argument("--config", default="config/universe.yaml", help="YAML project config")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch = subparsers.add_parser("fetch", help="Fetch and normalize daily market data")
    fetch.add_argument(
        "--source",
        choices=["yahoo", "alpha-vantage", "nasdaq-data-link"],
        default="yahoo",
    )
    fetch.add_argument("--start", type=_iso_date, default=today - timedelta(days=365 * 3))
    fetch.add_argument("--end", type=_iso_date, default=today)
    fetch.add_argument("--tickers", nargs="+", help="Override configured stock universe")
    fetch.add_argument("--output", help="Override output CSV path")

    validate = subparsers.add_parser("validate", help="Validate a previously saved CSV")
    validate.add_argument("path", type=Path)

    subparsers.add_parser("list-universe", help="Print the configured stock universe")

    research = subparsers.add_parser(
        "run-all", help="Run EDA, optimization, sensitivity analysis, and backtests"
    )
    research.add_argument("path", type=Path, help="Canonical market-data CSV")
    research.add_argument("--output-dir", type=Path, default=Path("artifacts"))
    research.add_argument("--risk-free-rate", type=float, default=DEFAULT_RISK_FREE_RATE)
    research.add_argument("--training-window", type=int, default=252)
    research.add_argument("--rebalance-frequency", type=int, default=21)
    research.add_argument("--transaction-cost-bps", type=float, default=10.0)
    research.add_argument("--max-weight", type=float, default=0.25)
    research.add_argument("--sector-cap", type=float, default=0.45)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return _execute(args)
    except (DataValidationError, FileNotFoundError, MarketDataError, ValueError) as exc:
        parser.exit(2, f"error: {exc}\n")


def _execute(args: argparse.Namespace) -> int:
    config = load_config(args.config)

    if args.command == "list-universe":
        for asset in config.universe:
            print(f"{asset.ticker:<6} {asset.sector:<12} {asset.company}")
        return 0

    if args.command == "validate":
        frame = pd.read_csv(args.path)
        validated = canonicalize(frame)
        print(
            f"Valid: {args.path} | rows={len(validated)} | tickers={validated['ticker'].nunique()}"
        )
        return 0

    if args.command == "run-all":
        result = run_full_research(
            data_path=args.path,
            config=config,
            output_dir=args.output_dir,
            risk_free_rate=args.risk_free_rate,
            training_window=args.training_window,
            rebalance_frequency=args.rebalance_frequency,
            transaction_cost_bps=args.transaction_cost_bps,
            max_weight=args.max_weight,
            sector_cap=args.sector_cap,
        )
        print(
            f"Research complete: rows={result.quality['rows']} | "
            f"tickers={result.quality['tickers']} | artifacts={args.output_dir}"
        )
        for method, backtest in result.backtests.items():
            metrics = backtest.metrics
            print(
                f"  {method:<15} annual_return={metrics['annual_return']:.2%} "
                f"volatility={metrics['annual_volatility']:.2%} "
                f"sharpe={metrics['sharpe']:.2f} "
                f"max_drawdown={metrics['max_drawdown']:.2%}"
            )
        return 0

    tickers = [ticker.strip().upper() for ticker in (args.tickers or config.tickers)]
    frame = fetch_market_data(
        source=args.source,
        config=config,
        tickers=tickers,
        start=args.start,
        end=args.end,
    )
    output_path, manifest_path = save_dataset(
        frame=frame,
        source=args.source,
        tickers=tickers,
        start=args.start,
        end=args.end,
        output=args.output,
    )
    returned = frame["ticker"].nunique()
    print(f"Saved {len(frame)} rows for {returned}/{len(tickers)} tickers to {output_path}")
    print(f"Manifest: {manifest_path}")
    failures = frame.attrs.get("failures", [])
    if failures:
        print("Partial failures:")
        for failure in failures:
            print(f"  - {failure}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
