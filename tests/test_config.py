from market_portfolio.config import load_config


def test_default_universe_is_diversified_and_unique() -> None:
    config = load_config()

    assert len(config.universe) == 15
    assert len(config.tickers) == len(set(config.tickers))
    assert {asset.sector for asset in config.universe} == {
        "Technology",
        "Financials",
        "Consumer",
    }
