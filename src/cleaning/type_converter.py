
from __future__ import annotations

import logging
from collections.abc import Iterable

import pandas as pd

logger = logging.getLogger(__name__)

DATE_COLUMNS = ("date_display", "objectDate", "release_date")
YEAR_COLUMNS = ("date_start", "date_end", "artist_begin_date", "artist_end_date", "accessionYear", "release_year")
INTEGER_COLUMNS = ("id", "artwork_id", "object_id", "objectID", *YEAR_COLUMNS)
FLOAT_COLUMNS = ("latitude", "longitude", "height", "width", "depth", "diameter")
CATEGORY_COLUMNS = (
    "department",
    "classification",
    "objectName",
    "culture",
    "place_of_origin",
    "country_code",
    "language",
    "original_language",
    "status",
)


def convert_dates(df: pd.DataFrame, columns: Iterable[str] = DATE_COLUMNS) -> pd.DataFrame:
    cleaned = df.copy()
    for column in columns:
        if column in cleaned.columns:
            parsed = pd.to_datetime(cleaned[column], errors="coerce")
            if parsed.notna().sum() > 0:
                cleaned[column] = parsed
                logger.info("convert_dates: %s -> datetime64 with %d NaT", column, parsed.isna().sum())
    return cleaned


def convert_numeric_columns(
    df: pd.DataFrame,
    float_cols: Iterable[str] = FLOAT_COLUMNS,
    int_cols: Iterable[str] = INTEGER_COLUMNS,
) -> pd.DataFrame:
    cleaned = df.copy()
    for column in float_cols:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce").astype("float32")
            logger.info("convert_numeric_columns: %s -> float32", column)

    for column in int_cols:
        if column in cleaned.columns:
            numeric_col = pd.to_numeric(cleaned[column], errors="coerce")
            cleaned[column] = numeric_col.round().astype("Int64")
            logger.info("convert_numeric_columns: %s -> Int64", column)
    return cleaned


def convert_category_columns(
    df: pd.DataFrame,
    columns: Iterable[str] = CATEGORY_COLUMNS,
    max_unique_ratio: float = 0.5,
) -> pd.DataFrame:
    cleaned = df.copy()
    for column in columns:
        if column in cleaned.columns:
            ratio = cleaned[column].nunique(dropna=True) / max(len(cleaned), 1)
            if ratio <= max_unique_ratio or column in CATEGORY_COLUMNS:
                cleaned[column] = cleaned[column].astype("category")
                logger.info("convert_category_columns: %s -> category", column)
    return cleaned


def optimise_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned = convert_dates(cleaned)
    cleaned = convert_numeric_columns(cleaned)
    cleaned = convert_category_columns(cleaned)
    return cleaned

def memory_report(df_before: pd.DataFrame, df_after: pd.DataFrame) -> pd.DataFrame:
    mb_before = df_before.memory_usage(deep=True).sum() / 1024**2
    mb_after = df_after.memory_usage(deep=True).sum() / 1024**2
    saved = mb_before - mb_after
    pct = (saved / mb_before * 100) if mb_before > 0 else 0
    report = pd.DataFrame(
        [
            {
                "memory_before_mb": round(mb_before, 4),
                "memory_after_mb": round(mb_after, 4),
                "memory_saved_mb": round(saved, 4),
                "memory_saved_pct": round(pct, 2),
            }
        ]
    )
    logger.info("memory_report: saved %.4f MB (%.2f%%)", saved, pct)
    return report


def memory_comparison(df_old: pd.DataFrame, df_new: pd.DataFrame) -> dict:
    old_mem = df_old.memory_usage(deep=True).sum()
    new_mem = df_new.memory_usage(deep=True).sum()
    reduction = ((old_mem - new_mem) / old_mem * 100) if old_mem > 0 else 0.0
    return {
        "old_memory_bytes": old_mem,
        "new_memory_bytes": new_mem,
        "reduction_pct": reduction,
    }