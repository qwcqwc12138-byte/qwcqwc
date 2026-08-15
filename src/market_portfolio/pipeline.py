from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Sequence
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from market_portfolio.config import ProjectConfig
from market_portfolio.providers import (
    AlphaVantageProvider,
    NasdaqDataLinkProvider,
    YahooFinanceProvider,
)
from market_portfolio.providers.base import MarketDataProvider


def build_provider(source: str, config: ProjectConfig) -> MarketDataProvider:
    if source == "yahoo":
        return YahooFinanceProvider()
    if source == "alpha-vantage":
        options = config.providers.get("alpha_vantage", {})
        return AlphaVantageProvider(
            api_key=os.getenv("ALPHA_VANTAGE_API_KEY", ""),
            request_delay_seconds=float(options.get("request_delay_seconds", 12.5)),
            output_size=str(options.get("output_size", "full")),
        )
    if source == "nasdaq-data-link":
        options = config.providers.get("nasdaq_data_link", {})
        return NasdaqDataLinkProvider(
            api_key=os.getenv("NASDAQ_DATA_LINK_API_KEY", ""),
            table_code=str(options.get("table_code", "SHARADAR/SEP")),
        )
    raise ValueError(f"Unsupported source: {source}")


def fetch_market_data(
    source: str,
    config: ProjectConfig,
    tickers: Sequence[str],
    start: date,
    end: date,
) -> pd.DataFrame:
    if start > end:
        raise ValueError("Start date must be on or before end date.")
    provider = build_provider(source, config)
    return provider.fetch(tickers=tickers, start=start, end=end)


def save_dataset(
    frame: pd.DataFrame,
    source: str,
    tickers: Sequence[str],
    start: date,
    end: date,
    output: str | Path | None = None,
) -> tuple[Path, Path]:
    output_path = (
        Path(output)
        if output
        else Path(f"data/processed/{source}/prices_{start.isoformat()}_{end.isoformat()}.csv")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False, date_format="%Y-%m-%d")

    checksum = hashlib.sha256(output_path.read_bytes()).hexdigest()
    manifest: dict[str, Any] = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "source": source,
        "tickers_requested": list(tickers),
        "tickers_returned": sorted(frame["ticker"].unique().tolist()),
        "start": start.isoformat(),
        "end": end.isoformat(),
        "rows": len(frame),
        "sha256": checksum,
        "partial_failures": frame.attrs.get("failures", []),
    }
    manifest_path = output_path.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return output_path, manifest_path
