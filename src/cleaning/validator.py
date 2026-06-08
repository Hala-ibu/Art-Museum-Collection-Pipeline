
from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)

MIN_ART_YEAR = -50000
MAX_ART_YEAR = 2100


def validate_no_null_titles(df: pd.DataFrame, title_col: str = "title") -> None:
    if title_col not in df.columns:
        return
    assert df[title_col].notna().all(), f"Found {df[title_col].isna().sum()} null titles"
    assert (df[title_col].astype(str).str.strip() != "").all(), "Found rows with empty titles"
    logger.info("validate_no_null_titles: PASSED")


def validate_no_duplicate_ids(df: pd.DataFrame, id_col: str = "id") -> None:
    actual = id_col if id_col in df.columns else None
    if actual is None:
        for candidate in ("artwork_id", "object_id", "objectID"):
            if candidate in df.columns:
                actual = candidate
                break
    if actual is None:
        return
    dup_count = df.duplicated(subset=[actual]).sum()
    assert dup_count == 0, f"Found {dup_count} duplicate values in column {actual}"
    logger.info("validate_no_duplicate_ids (%s): PASSED", actual)


def validate_year_range(
    df: pd.DataFrame,
    column: str = "release_year",
    min_year: int = MIN_ART_YEAR,
    max_year: int = MAX_ART_YEAR,
) -> None:
    if column not in df.columns:
        return
    years = pd.to_numeric(df[column], errors="coerce").dropna()
    assert years.between(min_year, max_year).all(), f"{column} outside [{min_year}, {max_year}]"
    logger.info("validate_year_range (%s): PASSED", column)


def validate_language_codes(df: pd.DataFrame) -> None:
    for column in ("language", "original_language", "country_code"):
        if column in df.columns:
            values = df[column].dropna().astype(str)
            valid = values.str.match(r"^[a-z]{2}$")
            assert valid.all(), f"Found {(~valid).sum()} invalid codes in {column}"
            logger.info("validate_language_codes (%s): PASSED", column)


def validate_required_identifier(df: pd.DataFrame) -> None:
    identifiers = [column for column in ("id", "artwork_id", "object_id", "objectID") if column in df.columns]
    if not identifiers:
        return
    assert df[identifiers].notna().any(axis=1).all(), "Found rows without any identifier"
    logger.info("validate_required_identifier: PASSED")


def run_all_validations(df: pd.DataFrame) -> dict[str, int]:
    checks = [
        validate_required_identifier,
        validate_no_null_titles,
        validate_no_duplicate_ids,
        validate_year_range,
        validate_language_codes,
    ]
    for check in checks:
        check(df)
    logger.info("run_all_validations: %d checks passed", len(checks))
    return {"passed": len(checks), "failed": 0}
