
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from .deduplicator import drop_duplicate_ids, drop_duplicate_titles, drop_exact_duplicates
from .missing_handler import (
    drop_high_missingness_columns,
    drop_rows_missing_identifiers,
    drop_rows_missing_title,
    fill_missing_text,
    fill_numeric_with_median,
    replace_zero_with_nan,
    report_missing,
)
from .string_cleaner import clean_all_strings, extract_year_from_release_date
from .type_converter import convert_category_columns, convert_dates, convert_numeric_columns
from .validator import run_all_validations

logger = logging.getLogger(__name__)
OUTPUT_DIR = Path("processed/cleaned")
OUTPUT_PATH = OUTPUT_DIR / "cleaned_data.csv"
LEGACY_OUTPUT_PATH = OUTPUT_DIR / "clean.csv"
MISSING_REPORT_PATH = OUTPUT_DIR / "missing_report.csv"


def run_cleaning_pipeline(
    df_raw: pd.DataFrame,
    save: bool = True,
    output_path: str | Path = OUTPUT_PATH,
) -> pd.DataFrame:
    """Clean raw art collection data and optionally persist CSV outputs."""
    logger.info("=== Starting cleaning pipeline: %d rows ===", len(df_raw))
    df = df_raw.copy()

    logger.info("Step 1: write missing-value report")
    missing_report = report_missing(df)

    logger.info("Step 2: remove rows missing critical identifiers and titles")
    df = drop_rows_missing_identifiers(df)
    df = drop_rows_missing_title(df)

    logger.info("Step 3: drop columns with excessive missingness")
    df = drop_high_missingness_columns(df, threshold=0.6)

    logger.info("Step 4: replace unrealistic zero year values with missing values")
    df = replace_zero_with_nan(df)

    logger.info("Step 5: normalize text fields")
    df = clean_all_strings(df)
    df = extract_year_from_release_date(df)

    logger.info("Step 6: fill descriptive and numeric missing values")
    df = fill_missing_text(df)
    df = fill_numeric_with_median(df)

    logger.info("Step 7: remove exact, identifier, and title/date duplicates")
    df = drop_exact_duplicates(df)
    df = drop_duplicate_ids(df)
    df = drop_duplicate_titles(df)

    logger.info("Step 8: convert data types")
    df = convert_dates(df)
    df = convert_numeric_columns(df)
    df = convert_category_columns(df)

    logger.info("Step 9: validate cleaned data")
    run_all_validations(df)

    if save:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        if output_path != LEGACY_OUTPUT_PATH:
            df.to_csv(LEGACY_OUTPUT_PATH, index=False)
        missing_report.to_csv(MISSING_REPORT_PATH)
        logger.info("Saved clean dataset to %s (%d rows)", output_path, len(df))
        logger.info("Saved compatibility clean dataset to %s", LEGACY_OUTPUT_PATH)
        logger.info("Saved missing report to %s", MISSING_REPORT_PATH)

    logger.info("=== Cleaning pipeline complete: %d rows remain ===", len(df))
    return df