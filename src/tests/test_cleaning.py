from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

# Import functions from your custom packages
from src.cleaning.deduplicator import (
    count_duplicates,
    drop_duplicate_ids,
    drop_duplicate_titles,
    drop_exact_duplicates,
)
from src.cleaning.missing_handler import (
    drop_high_missingness_columns,
    drop_rows_missing_identifiers,
    drop_rows_missing_title,
    fill_missing_text,
    fill_numeric_with_median,
    replace_zero_with_nan,
    report_missing,
)
from src.cleaning.string_cleaner import (
    clean_all_strings,
    clean_language_code,
    clean_text_columns,
    clean_title,
    extract_year_from_release_date,
    normalize_category_case,
)
from src.cleaning.type_converter import (
    convert_category_columns,
    convert_dates,
    convert_numeric_columns,
    memory_report,
)
from src.cleaning.validator import (
    run_all_validations,
    validate_language_codes,
    validate_no_duplicate_ids,
    validate_no_null_titles,
    validate_year_range,
)


@pytest.fixture
def mock_raw_artwork_df() -> pd.DataFrame:
    return pd.DataFrame({
        "id": [101, 102, 102, np.nan, 104, 105],
        "title": ["  STARRY NIGHT  ", "The Scream", "The Scream", "Guernica", "  ", "Mona Lisa"],
        "artist_display": ["Vincent van Gogh", "Edvard Munch", "Edvard Munch", "Pablo Picasso", "Unknown", None],
        "date_start": [1889, 1893, 1893, 1937, 0, 1503],
        "date_display": ["1889", "1893", "1893", "1937", "c. 1950", "1503"],
        "department": ["PAINTING", "Prints", "Prints", "painting", "Modern", "PAINTING"],
        "language": ["EN ", "no", "no", "ES-ES", "fr_FR", None]
    })


def test_report_missing(mock_raw_artwork_df):
    report = report_missing(mock_raw_artwork_df)
    assert isinstance(report, pd.DataFrame)
    assert "missing_count" in report.columns
    assert "missing_pct" in report.columns
    assert report.loc["id", "missing_count"] == 1


def test_drop_rows_missing_identifiers(mock_raw_artwork_df):
    cleaned = drop_rows_missing_identifiers(mock_raw_artwork_df)
    assert len(cleaned) == 5
    assert cleaned["id"].isna().sum() == 0


def test_drop_rows_missing_title(mock_raw_artwork_df):
    cleaned = drop_rows_missing_title(mock_raw_artwork_df)
    assert len(cleaned) == 5
    assert not (cleaned["title"].astype(str).str.strip() == "").any()


def test_fill_missing_text(mock_raw_artwork_df):
    cleaned = fill_missing_text(mock_raw_artwork_df, placeholder="Unknown Asset")
    assert cleaned.iloc[5]["artist_display"] == "Unknown Asset"


def test_replace_zero_with_nan(mock_raw_artwork_df):
    cleaned = replace_zero_with_nan(mock_raw_artwork_df, columns=["date_start"])
    assert pd.isna(cleaned.iloc[4]["date_start"])


def test_fill_numeric_with_median(mock_raw_artwork_df):
    df = pd.DataFrame({"date_start": [1800, 1900, np.nan, 2000]})
    cleaned = fill_numeric_with_median(df, columns=["date_start"])
    assert cleaned.iloc[2]["date_start"] == 1900


def test_drop_high_missingness_columns():
    df = pd.DataFrame({
        "good_col": [1, 2, 3, 4],
        "bad_col": [1, np.nan, np.nan, np.nan] # 75% missing
    })
    cleaned = drop_high_missingness_columns(df, threshold=0.6)
    assert "bad_col" not in cleaned.columns
    assert "good_col" in cleaned.columns

def test_drop_exact_duplicates(mock_raw_artwork_df):
    cleaned = drop_exact_duplicates(mock_raw_artwork_df)
    assert len(cleaned) == len(mock_raw_artwork_df) - 1


def test_drop_duplicate_ids(mock_raw_artwork_df):
    cleaned = drop_duplicate_ids(mock_raw_artwork_df)
    assert cleaned["id"].duplicated().sum() == 0


def test_drop_duplicate_titles(mock_raw_artwork_df):
    cleaned = drop_duplicate_titles(mock_raw_artwork_df)
    assert cleaned.duplicated(subset=["title", "date_display"]).sum() == 0


def test_count_duplicates(mock_raw_artwork_df):
    count = count_duplicates(mock_raw_artwork_df, col="id")
    assert count == 1

def test_clean_title(mock_raw_artwork_df):
    cleaned = clean_title(mock_raw_artwork_df)
    assert cleaned.iloc[0]["title"] == "Starry Night"


def test_clean_language_code(mock_raw_artwork_df):
    cleaned = clean_language_code(mock_raw_artwork_df)
    assert cleaned.iloc[0]["language"] == "en" # "EN " -> stripped and lowercased
    assert cleaned.iloc[3]["language"] == "es" # "ES-ES" -> extracted first 2 letters


def test_normalize_category_case(mock_raw_artwork_df):
    cleaned = normalize_category_case(mock_raw_artwork_df, columns=["department"])
    assert cleaned.iloc[0]["department"] == "Painting"
    assert cleaned.iloc[3]["department"] == "Painting"


def test_extract_year_from_release_date():
    df = pd.DataFrame({"release_date": ["1995-05-12", "Circa 2004", "1203 AD", "No Date"]})
    cleaned = extract_year_from_release_date(df, source_col="release_date", target_col="release_year")
    assert cleaned.iloc[0]["release_year"] == 1995
    assert cleaned.iloc[1]["release_year"] == 2004
    assert cleaned.iloc[2]["release_year"] == 1203
    assert pd.isna(cleaned.iloc[3]["release_year"])

def test_convert_dates():
    df = pd.DataFrame({"date_display": ["2023-01-01", "2026-12-31"]})
    cleaned = convert_dates(df, columns=["date_display"])
    assert pd.api.types.is_datetime64_any_dtype(cleaned["date_display"])


def test_convert_numeric_columns(mock_raw_artwork_df):
    cleaned = convert_numeric_columns(mock_raw_artwork_df, float_cols=[], int_cols=["id"])
    assert cleaned["id"].dtype == "Int64"


def test_convert_category_columns(mock_raw_artwork_df):
    cleaned = convert_category_columns(mock_raw_artwork_df, columns=["department"])
    assert isinstance(cleaned["department"].dtype, pd.CategoricalDtype)


def test_memory_report(mock_raw_artwork_df):
    report = memory_report(mock_raw_artwork_df, mock_raw_artwork_df)
    assert "memory_before_mb" in report.columns
    assert report.iloc[0]["memory_saved_mb"] == 0.0

def test_validate_no_null_titles_raises_error():
    df = pd.DataFrame({"title": ["Valid Title", None]})
    with pytest.raises(AssertionError):
        validate_no_null_titles(df)


def test_validate_no_duplicate_ids_raises_error():
    df = pd.DataFrame({"id": [1, 1, 2]})
    with pytest.raises(AssertionError):
        validate_no_duplicate_ids(df)


def test_validate_year_range_raises_error():
    df = pd.DataFrame({"release_year": [1995, 3500]}) # 3500 is out of bounds
    with pytest.raises(AssertionError):
        validate_year_range(df, column="release_year")


def test_validate_language_codes_raises_error():
    df = pd.DataFrame({"language": ["eng", "US", "e1"]}) # 'eng' has 3 letters, 'e1' contains numbers
    with pytest.raises(AssertionError):
        validate_language_codes(df)


def test_run_all_validations_success():
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "title": ["Title A", "Title B", "Title C"],
        "release_year": [1999, 2005, 2021],
        "language": ["en", "fr", "es"]
    })
    result = run_all_validations(df)
    assert result["passed"] == 5
    assert result["failed"] == 0