
from __future__ import annotations

import logging
from collections.abc import Iterable

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

CRITICAL_IDENTIFIER_COLUMNS = ("id", "artwork_id", "object_id", "objectID")
DESCRIPTIVE_TEXT_COLUMNS = (
    "title",
    "artist_display",
    "artistDisplayName",
    "place_of_origin",
    "medium_display",
    "medium",
    "dimensions",
    "classification",
    "department",
    "objectName",
    "culture",
    "description",
    "provenance_text",
)
NUMERIC_MEASURE_COLUMNS = (
    "date_start",
    "date_end",
    "artist_begin_date",
    "artist_end_date",
    "accessionYear",
)
ZERO_AS_MISSING_COLUMNS = (
    "date_start",
    "date_end",
    "artist_begin_date",
    "artist_end_date",
    "accessionYear",
)


def existing_columns(df: pd.DataFrame, columns: Iterable[str]) -> list[str]:
    return [column for column in columns if column in df.columns]


def report_missing(df: pd.DataFrame) -> pd.DataFrame:
    missing_count = df.isna().sum()
    missing_pct = (df.isna().mean() * 100).round(2)
    report = pd.DataFrame(
        {
            "missing_count": missing_count,
            "missing_pct": missing_pct,
            "dtype": df.dtypes.astype(str),
        }
    )
    report = report[report["missing_count"] > 0].sort_values(
        "missing_pct", ascending=False
    )
    logger.info("Missing value report generated for %d columns", len(report))
    return report


def drop_rows_missing_identifiers(
    df: pd.DataFrame, identifier_columns: Iterable[str] = CRITICAL_IDENTIFIER_COLUMNS
) -> pd.DataFrame:
    columns = existing_columns(df, identifier_columns)
    if not columns:
        logger.warning("drop_rows_missing_identifiers: no identifier columns found")
        return df.reset_index(drop=True)

    before = len(df)
    cleaned = df.dropna(subset=columns, how="all").copy()
    for column in columns:
        if pd.api.types.is_string_dtype(cleaned[column]) or cleaned[column].dtype == object:
            cleaned = cleaned[cleaned[column].astype(str).str.strip() != ""]
    logger.info(
        "drop_rows_missing_identifiers: dropped %d rows using %s",
        before - len(cleaned),
        columns,
    )
    return cleaned.reset_index(drop=True)


def drop_rows_missing_title(df: pd.DataFrame, title_col: str = "title") -> pd.DataFrame:
    if title_col not in df.columns:
        logger.warning("drop_rows_missing_title: %s not found, skipping", title_col)
        return df.reset_index(drop=True)

    before = len(df)
    cleaned = df.dropna(subset=[title_col]).copy()
    cleaned = cleaned[cleaned[title_col].astype(str).str.strip() != ""]
    logger.info("drop_rows_missing_title: dropped %d rows", before - len(cleaned))
    return cleaned.reset_index(drop=True)


def fill_missing_text(
    df: pd.DataFrame,
    columns: Iterable[str] = DESCRIPTIVE_TEXT_COLUMNS,
    placeholder: str = "Unknown",
) -> pd.DataFrame:
    cleaned = df.copy()
    for column in existing_columns(cleaned, columns):
        missing = cleaned[column].isna().sum()
        cleaned[column] = cleaned[column].fillna(placeholder)
        logger.info("fill_missing_text: %s -> filled %d rows", column, missing)
    return cleaned


def replace_zero_with_nan(
    df: pd.DataFrame, columns: Iterable[str] = ZERO_AS_MISSING_COLUMNS
) -> pd.DataFrame:
    cleaned = df.copy()
    for column in existing_columns(cleaned, columns):
        numeric = pd.to_numeric(cleaned[column], errors="coerce")
        zeros = numeric.eq(0).sum()
        cleaned[column] = cleaned[column].mask(numeric.eq(0), np.nan)
        logger.info("replace_zero_with_nan: %s -> replaced %d zeros", column, zeros)
    return cleaned


def fill_numeric_with_median(
    df: pd.DataFrame, columns: Iterable[str] = NUMERIC_MEASURE_COLUMNS
) -> pd.DataFrame:
    cleaned = df.copy()
    for column in existing_columns(cleaned, columns):
        numeric = pd.to_numeric(cleaned[column], errors="coerce")
        median_val = numeric.median()
        filled = numeric.isna().sum()
        if pd.isna(median_val):
            logger.warning("fill_numeric_with_median: %s has no median, skipping", column)
            cleaned[column] = numeric
            continue
        cleaned[column] = numeric.fillna(median_val)
        logger.info(
            "fill_numeric_with_median: %s -> filled %d with %.2f",
            column,
            filled,
            median_val,
        )
    return cleaned


def drop_high_missingness_columns(
    df: pd.DataFrame, threshold: float = 0.6
) -> pd.DataFrame:
    miss_ratio = df.isna().mean()
    to_drop = miss_ratio[miss_ratio > threshold].index.tolist()
    if to_drop:
        logger.info("drop_high_missingness_columns: dropped %s", to_drop)
        return df.drop(columns=to_drop)
    logger.info("drop_high_missingness_columns: no columns exceeded %.2f", threshold)
    return df