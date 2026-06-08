
from __future__ import annotations

import logging
import re
from collections.abc import Iterable

import pandas as pd

logger = logging.getLogger(__name__)

TITLE_COLUMNS = ("title", "artwork_title")
TEXT_COLUMNS = (
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
CODE_COLUMNS = ("country_code", "language", "original_language")
DATE_COLUMNS = ("date_display", "objectDate", "release_date")


def _clean_whitespace(series: pd.Series) -> pd.Series:
    return series.astype("string").str.replace(r"\s+", " ", regex=True).str.strip()


def clean_title(df: pd.DataFrame, title_col: str = "title") -> pd.DataFrame:
    cleaned = df.copy()
    if title_col not in cleaned.columns:
        logger.warning("clean_title: %s not found, skipping", title_col)
        return cleaned

    titles = _clean_whitespace(cleaned[title_col])
    uppercase_mask = titles.str.fullmatch(r"[^a-z]*[A-Z][^a-z]*", na=False)
    titles = titles.mask(uppercase_mask, titles.str.title())
    cleaned[title_col] = titles
    logger.info("clean_title: cleaned %s", title_col)
    return cleaned


def clean_text_columns(
    df: pd.DataFrame, columns: Iterable[str] = TEXT_COLUMNS
) -> pd.DataFrame:
    cleaned = df.copy()
    for column in columns:
        if column in cleaned.columns:
            cleaned[column] = _clean_whitespace(cleaned[column])
            logger.info("clean_text_columns: cleaned %s", column)
    return cleaned


def clean_overview_text(df: pd.DataFrame, overview_col: str = "description") -> pd.DataFrame:
    cleaned = df.copy()
    column = overview_col if overview_col in cleaned.columns else None
    if column is None and "overview" in cleaned.columns:
        column = "overview"
    if column is None:
        logger.warning("clean_overview_text: no overview/description column found")
        return cleaned

    cleaned[column] = (
        cleaned[column]
        .astype("string")
        .str.replace(r"<[^>]+>", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    logger.info("clean_overview_text: cleaned %s", column)
    return cleaned


def clean_language_code(df: pd.DataFrame, column: str = "language") -> pd.DataFrame:
    cleaned = df.copy()
    actual = column if column in cleaned.columns else None
    if actual is None:
        for candidate in CODE_COLUMNS:
            if candidate in cleaned.columns:
                actual = candidate
                break
    if actual is None:
        logger.warning("clean_language_code: no language/code column found")
        return cleaned

    cleaned[actual] = (
        cleaned[actual]
        .astype("string")
        .str.strip()
        .str.lower()
        .str.extract(r"^([a-z]{2})", expand=False)
    )
    logger.info("clean_language_code: cleaned %s", actual)
    return cleaned


def normalize_category_case(
    df: pd.DataFrame, columns: Iterable[str] = ("department", "classification", "objectName")
) -> pd.DataFrame:
    cleaned = df.copy()
    for column in columns:
        if column in cleaned.columns:
            cleaned[column] = _clean_whitespace(cleaned[column]).str.title()
            logger.info("normalize_category_case: cleaned %s", column)
    return cleaned


def extract_year_from_release_date(
    df: pd.DataFrame, source_col: str | None = None, target_col: str = "release_year"
) -> pd.DataFrame:
    cleaned = df.copy()
    if source_col is None:
        source_col = next((column for column in DATE_COLUMNS if column in cleaned.columns), None)
    if source_col is None:
        logger.warning("extract_year_from_release_date: no date column found")
        return cleaned

    extracted = cleaned[source_col].astype("string").str.extract(r"(\d{4})", expand=False)
    cleaned[target_col] = pd.to_numeric(extracted, errors="coerce").astype("Int64")
    logger.info("extract_year_from_release_date: extracted %s from %s", target_col, source_col)
    return cleaned


def clean_all_strings(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = clean_title(df)
    cleaned = clean_text_columns(cleaned)
    cleaned = clean_overview_text(cleaned)
    cleaned = clean_language_code(cleaned)
    cleaned = normalize_category_case(cleaned)
    return cleaned