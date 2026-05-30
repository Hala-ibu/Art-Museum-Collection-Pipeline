
from __future__ import annotations

import logging
from collections.abc import Iterable

import pandas as pd

logger = logging.getLogger(__name__)

ID_COLUMNS = ("id", "artwork_id", "object_id", "objectID")
TITLE_COLUMNS = ("title", "artwork_title")
DATE_COLUMNS = ("date_display", "objectDate", "release_date")


def _first_existing(df: pd.DataFrame, columns: Iterable[str]) -> str | None:
    return next((column for column in columns if column in df.columns), None)


def drop_exact_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    cleaned = df.drop_duplicates(keep="first")
    logger.info("drop_exact_duplicates: removed %d rows", before - len(cleaned))
    return cleaned.reset_index(drop=True)


def drop_duplicate_ids(df: pd.DataFrame, id_col: str | None = None) -> pd.DataFrame:
    actual_col = id_col if id_col in df.columns else _first_existing(df, ID_COLUMNS)
    if actual_col is None:
        logger.warning("drop_duplicate_ids: no id column found, skipping")
        return df.reset_index(drop=True)

    before = len(df)
    cleaned = df.drop_duplicates(subset=[actual_col], keep="first")
    logger.info("drop_duplicate_ids (%s): removed %d rows", actual_col, before - len(cleaned))
    return cleaned.reset_index(drop=True)


def drop_duplicate_titles(df: pd.DataFrame) -> pd.DataFrame:
    title_col = _first_existing(df, TITLE_COLUMNS)
    if title_col is None:
        logger.warning("drop_duplicate_titles: no title column found, skipping")
        return df.reset_index(drop=True)

    date_col = _first_existing(df, DATE_COLUMNS)
    subset = [title_col, date_col] if date_col else [title_col]
    before = len(df)
    cleaned = df.drop_duplicates(subset=subset, keep="first")
    logger.info("drop_duplicate_titles: removed %d rows using %s", before - len(cleaned), subset)
    return cleaned.reset_index(drop=True)


def count_duplicates(df: pd.DataFrame, col: str = "id") -> int:
    if col not in df.columns:
        return 0
    return int(df.duplicated(subset=[col]).sum())