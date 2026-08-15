from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Asset:
    ticker: str
    company: str
    sector: str


@dataclass(frozen=True)
class ProjectConfig:
    universe: tuple[Asset, ...]
    providers: dict[str, dict[str, Any]]

    @property
    def tickers(self) -> list[str]:
        return [asset.ticker for asset in self.universe]


def load_config(path: str | Path = "config/universe.yaml") -> ProjectConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with config_path.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    entries = raw.get("universe") or []
    if not entries:
        raise ValueError("The configured universe is empty.")

    assets = tuple(
        Asset(
            ticker=str(entry["ticker"]).strip().upper(),
            company=str(entry["company"]).strip(),
            sector=str(entry["sector"]).strip(),
        )
        for entry in entries
    )
    tickers = [asset.ticker for asset in assets]
    if len(tickers) != len(set(tickers)):
        raise ValueError("The configured universe contains duplicate tickers.")

    providers = raw.get("providers") or {}
    return ProjectConfig(universe=assets, providers=providers)
