from __future__ import annotations

import pandas as pd

CANONICAL_COLUMNS = [
    "date",
    "ticker",
    "open",
    "high",
    "low",
    "close",
    "adjusted_close",
    "volume",
    "dividend",
    "stock_split",
    "source",
]

NUMERIC_COLUMNS = [
    "open",
    "high",
    "low",
    "close",
    "adjusted_close",
    "volume",
    "dividend",
    "stock_split",
]


class DataValidationError(ValueError):
    """Raised when market data cannot satisfy the canonical schema."""


def canonicalize(frame: pd.DataFrame) -> pd.DataFrame:
    """Coerce provider output into a sorted, de-duplicated canonical data frame."""
    if frame.empty:
        return pd.DataFrame(columns=CANONICAL_COLUMNS)

    result = frame.copy()
    missing_required = {"date", "ticker", "close", "source"} - set(result.columns)
    if missing_required:
        missing = ", ".join(sorted(missing_required))
        raise DataValidationError(f"Missing required columns: {missing}")

    for column in CANONICAL_COLUMNS:
        if column not in result:
            result[column] = pd.NA

    parsed_dates = pd.to_datetime(result["date"], errors="coerce", utc=True)
    result["date"] = parsed_dates.dt.tz_convert(None).dt.normalize()
    result["ticker"] = result["ticker"].astype("string").str.strip().str.upper()
    result["source"] = result["source"].astype("string").str.strip()

    for column in NUMERIC_COLUMNS:
        result[column] = pd.to_numeric(result[column], errors="coerce")

    result["adjusted_close"] = result["adjusted_close"].fillna(result["close"])
    result["dividend"] = result["dividend"].fillna(0.0)
    result["stock_split"] = result["stock_split"].fillna(0.0)

    result = result[CANONICAL_COLUMNS]
    result = result.drop_duplicates(subset=["date", "ticker", "source"], keep="last")
    result = result.sort_values(["ticker", "date", "source"], kind="stable").reset_index(drop=True)
    validate(result)
    return result


def validate(frame: pd.DataFrame) -> None:
    """Validate a canonical data frame and raise a readable error if invalid."""
    missing_columns = set(CANONICAL_COLUMNS) - set(frame.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise DataValidationError(f"Missing canonical columns: {missing}")

    required = ["date", "ticker", "close", "source"]
    null_counts = frame[required].isna().sum()
    if (null_counts > 0).any():
        details = ", ".join(f"{name}={count}" for name, count in null_counts.items() if count)
        raise DataValidationError(f"Null required values: {details}")

    if (frame["ticker"].astype("string").str.len() == 0).any():
        raise DataValidationError("Ticker values cannot be blank.")
    if (frame["source"].astype("string").str.len() == 0).any():
        raise DataValidationError("Source values cannot be blank.")
    if (frame["close"] <= 0).any():
        raise DataValidationError("Close prices must be positive.")
    if frame["volume"].dropna().lt(0).any():
        raise DataValidationError("Volume cannot be negative.")
    if frame.duplicated(["date", "ticker", "source"]).any():
        raise DataValidationError("Duplicate date/ticker/source rows detected.")
