from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from market_portfolio.plotting import configure_matplotlib_cache
from market_portfolio.schema import canonicalize

configure_matplotlib_cache()
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

TRADING_DAYS = 252


def load_market_csv(path: str | Path) -> pd.DataFrame:
    """Load and validate a canonical market-data CSV."""
    return canonicalize(pd.read_csv(path))


def adjusted_price_matrix(frame: pd.DataFrame) -> pd.DataFrame:
    """Create a complete date-by-ticker adjusted-close matrix."""
    canonical = canonicalize(frame)
    prices = canonical.pivot(index="date", columns="ticker", values="adjusted_close")
    prices = prices.sort_index().sort_index(axis=1)
    prices = prices.dropna(how="all").ffill().dropna(axis=0, how="any")
    if prices.empty or prices.shape[1] < 2:
        raise ValueError("At least two complete adjusted-price series are required.")
    return prices


def simple_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change(fill_method=None).dropna(how="any")


def log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return np.log(prices / prices.shift(1)).dropna(how="any")


def drawdown(equity: pd.Series | pd.DataFrame) -> pd.Series | pd.DataFrame:
    return equity.div(equity.cummax()).sub(1.0)


def asset_performance_summary(
    prices: pd.DataFrame,
    risk_free_rate: float = 0.0,
    frequency: int = TRADING_DAYS,
) -> pd.DataFrame:
    returns = simple_returns(prices)
    observations = returns.count()
    years = observations / frequency
    total_return = prices.iloc[-1].div(prices.iloc[0]).sub(1.0)
    annual_return = (1.0 + total_return).pow(1.0 / years).sub(1.0)
    annual_volatility = returns.std(ddof=1) * np.sqrt(frequency)
    sharpe = annual_return.sub(risk_free_rate).div(annual_volatility)
    maximum_drawdown = drawdown(prices).min()
    result = pd.DataFrame(
        {
            "total_return": total_return,
            "annual_return": annual_return,
            "annual_volatility": annual_volatility,
            "sharpe": sharpe,
            "max_drawdown": maximum_drawdown,
            "observations": observations,
        }
    )
    result.index.name = "ticker"
    return result.sort_values("sharpe", ascending=False)


def data_quality_summary(frame: pd.DataFrame) -> dict[str, object]:
    canonical = canonicalize(frame)
    expected_rows = canonical["date"].nunique() * canonical["ticker"].nunique()
    prices = adjusted_price_matrix(canonical)
    returns = simple_returns(prices)
    ohlc = canonical.dropna(subset=["open", "high", "low", "close"])
    invalid_ohlc = ohlc["high"].lt(ohlc[["open", "low", "close"]].max(axis=1)) | ohlc["low"].gt(
        ohlc[["open", "high", "close"]].min(axis=1)
    )
    return {
        "rows": len(canonical),
        "tickers": canonical["ticker"].nunique(),
        "first_date": canonical["date"].min().date().isoformat(),
        "last_date": canonical["date"].max().date().isoformat(),
        "missing_adjusted_close": int(canonical["adjusted_close"].isna().sum()),
        "duplicate_keys": int(canonical.duplicated(["date", "ticker", "source"]).sum()),
        "panel_coverage": len(canonical) / expected_rows if expected_rows else 0.0,
        "invalid_ohlc_rows": int(invalid_ohlc.sum()),
        "extreme_adjusted_returns": int(returns.abs().gt(0.25).sum().sum()),
        "dividend_events": int(canonical["dividend"].gt(0).sum()),
        "split_events": int(canonical["stock_split"].gt(0).sum()),
    }


def generate_eda_artifacts(
    frame: pd.DataFrame,
    output_dir: str | Path,
    risk_free_rate: float = 0.0,
    rolling_window: int = 63,
) -> dict[str, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    prices = adjusted_price_matrix(frame)
    returns = simple_returns(prices)
    metrics = asset_performance_summary(prices, risk_free_rate=risk_free_rate)
    correlation = returns.corr()

    paths = {
        "asset_metrics": output / "asset_metrics.csv",
        "correlation": output / "correlation.csv",
        "normalized_prices": output / "normalized_prices.png",
        "correlation_heatmap": output / "correlation_heatmap.png",
        "rolling_volatility": output / "rolling_volatility.png",
        "return_distribution": output / "return_distribution.png",
    }
    metrics.to_csv(paths["asset_metrics"])
    correlation.to_csv(paths["correlation"])

    _plot_normalized_prices(prices, paths["normalized_prices"])
    _plot_correlation(correlation, paths["correlation_heatmap"])
    _plot_rolling_volatility(returns, rolling_window, paths["rolling_volatility"])
    _plot_return_distribution(returns, paths["return_distribution"])
    return paths


def _plot_normalized_prices(prices: pd.DataFrame, path: Path) -> None:
    normalized = prices.div(prices.iloc[0]).mul(100.0)
    axis = normalized.plot(figsize=(13, 7), linewidth=1.3)
    axis.set(title="Normalized Adjusted Prices", ylabel="Initial value = 100", xlabel="Date")
    axis.grid(alpha=0.25)
    axis.legend(ncol=3, fontsize=8)
    axis.figure.tight_layout()
    axis.figure.savefig(path, dpi=160)
    plt.close(axis.figure)


def _plot_correlation(correlation: pd.DataFrame, path: Path) -> None:
    figure, axis = plt.subplots(figsize=(10, 8))
    image = axis.imshow(correlation, vmin=-1, vmax=1, cmap="RdBu_r")
    axis.set_xticks(range(len(correlation)), labels=correlation.columns, rotation=60, ha="right")
    axis.set_yticks(range(len(correlation)), labels=correlation.index)
    axis.set_title("Daily Return Correlation")
    figure.colorbar(image, ax=axis, shrink=0.8)
    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)


def _plot_rolling_volatility(returns: pd.DataFrame, window: int, path: Path) -> None:
    rolling = returns.rolling(window).std().mul(np.sqrt(TRADING_DAYS))
    axis = rolling.plot(figsize=(13, 7), linewidth=1.1)
    axis.set(
        title=f"Rolling Annualized Volatility ({window} trading days)",
        ylabel="Annualized volatility",
        xlabel="Date",
    )
    axis.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:.0%}"))
    axis.grid(alpha=0.25)
    axis.legend(ncol=3, fontsize=8)
    axis.figure.tight_layout()
    axis.figure.savefig(path, dpi=160)
    plt.close(axis.figure)


def _plot_return_distribution(returns: pd.DataFrame, path: Path) -> None:
    figure, axis = plt.subplots(figsize=(13, 7))
    axis.boxplot(
        [returns[column].dropna().to_numpy() for column in returns],
        tick_labels=returns.columns,
        showfliers=False,
    )
    axis.set(title="Daily Return Distribution", ylabel="Daily return", xlabel="Ticker")
    axis.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:.1%}"))
    axis.grid(axis="y", alpha=0.25)
    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)
