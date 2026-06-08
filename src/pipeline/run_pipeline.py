#!/usr/bin/env python3
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# =====================================================================
# SYSTEM PATH TRACKING (Prevents ModuleNotFoundError for project modules)
# =====================================================================
CURRENT_SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_SCRIPT_DIR.parents[1]
SRC_DIR = PROJECT_ROOT / "src"

# Prioritize the explicit 'src' directory so internal package lookups clear immediately
for import_path in (SRC_DIR, PROJECT_ROOT):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

# =====================================================================
# PIPELINE IMPORTS (Direct Module Resolution)
# =====================================================================
from analytics.data_loader import (  # noqa: E402
    chunked_stats,
    load_from_csv,
    load_from_mongodb,
    memory_comparison,
    optimise_dtypes,
    save_to_csv,
)
from analytics.explorer import plot_distributions  # noqa: E402
from analytics.numpy_ops import demonstrate_array_creation, vectorized_operations  # noqa: E402
from analytics.quality_report import full_quality_report, save_missing_heatmap  # noqa: E402
from analytics.regex_ops import perform_regex_analysis  # noqa: E402
from analytics.selector import complex_filter  # noqa: E402
from cleaning.clean_pipeline import run_cleaning_pipeline  # noqa: E402

# =====================================================================
# GLOBAL UNIFIED LOGGING INFRASTRUCTURE
# =====================================================================
LOG_FILE_PATH = PROJECT_ROOT / "pipeline.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("MasterPipeline")

# =====================================================================
# PROJECT PATHS
# =====================================================================
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
ANALYTICS_DIR = PROCESSED_DIR / "analytics"
CLEANED_DIR = PROCESSED_DIR / "cleaned"
LAB_CLEANED_DIR = PROJECT_ROOT / "processed" / "cleaned"
RAW_ANALYTICS_CSV = ANALYTICS_DIR / "raw_art_data.csv"
CLEANED_CSV = CLEANED_DIR / "art_collection_clean.csv"


# =====================================================================
# STAGE ACTIONS & SUB-PIPELINES
# =====================================================================
def ensure_output_dirs() -> None:
    """Create all output folders used by the master orchestration script."""
    for folder in (ANALYTICS_DIR, CLEANED_DIR, LAB_CLEANED_DIR):
        folder.mkdir(parents=True, exist_ok=True)


def find_existing_csv() -> Path | None:
    """Locate a usable CSV source when MongoDB is unavailable."""
    candidates = [
        RAW_ANALYTICS_CSV,
        PROJECT_ROOT / "processed" / "raw_data.csv",
        LAB_CLEANED_DIR / "cleaned_data.csv",
        LAB_CLEANED_DIR / "clean.csv",
    ]
    return next((path for path in candidates if path.exists()), None)


def build_demo_art_frame() -> pd.DataFrame:
    """Small fallback frame so the pipeline remains demonstrable without MongoDB."""
    return pd.DataFrame(
        {
            "id": [1, 2, 2, 3],
            "title": ["  MONA    LISA ", "Starry Night", "Starry Night", "The Kiss"],
            "artist_display": [" Leonardo  da Vinci ", "Vincent van Gogh", "Vincent van Gogh", "Gustav Klimt"],
            "description": ["<p>Famous portrait painting</p>", None, None, "Gold leaf portrait scene"],
            "date_display": ["1503", "1889", "1889", "1908"],
            "date_start": [1503, 0, 1889, 1908],
            "department": [" paintings ", "PAINTINGS", "PAINTINGS", "paintings"],
            "classification": [" painting ", "painting", "painting", "painting"],
            "language": [" EN ", "fr", "fr", "DE"],
        }
    )


def run_ingestion_stage() -> pd.DataFrame:
    """Stage 1: Load art collection data from MongoDB, CSV fallback, or demo data."""
    logger.info("=== Stage 1: Data Ingestion ===")
    ensure_output_dirs()

    try:
        df = load_from_mongodb()
        if df is not None and not df.empty:
            save_to_csv(df, str(RAW_ANALYTICS_CSV))
            logger.info("MongoDB ingestion succeeded with %d records", len(df))
            return df
        logger.warning("MongoDB returned no records; checking CSV fallbacks")
    except Exception as exc:
        logger.warning("MongoDB ingestion skipped: %s", exc)

    fallback_csv = find_existing_csv()
    if fallback_csv is not None:
        df = load_from_csv(str(fallback_csv), low_memory=False)
        save_to_csv(df, str(RAW_ANALYTICS_CSV))
        logger.info("CSV fallback ingestion succeeded from %s", fallback_csv)
        return df

    logger.warning("No MongoDB or CSV source found; using built-in demo art frame")
    df = build_demo_art_frame()
    save_to_csv(df, str(RAW_ANALYTICS_CSV))
    return df


def run_document_parsing_stage() -> None:
    """Stage 2: Parse optional local PDF, Word, and Excel artifacts when present."""
    logger.info("=== Stage 2: Optional Document Parsing ===")
    raw_pdf_dir = RAW_DIR / "pdf"
    raw_word_dir = RAW_DIR / "word"
    raw_excel_dir = RAW_DIR / "excel"

    if not any(path.exists() for path in (raw_pdf_dir, raw_word_dir, raw_excel_dir)):
        logger.info("No document input folders found; document parsing skipped")
        return

    try:
        from parsing.parsers import extract_data_from_excel, extract_text_from_pdf, extract_text_from_word
    except Exception as exc:
        logger.warning("Document parser dependencies are unavailable; stage skipped: %s", exc)
        return

    parsed_dir = PROCESSED_DIR / "parsed"
    parsed_dir.mkdir(parents=True, exist_ok=True)

    for pdf_path in (raw_pdf_dir.glob("*.pdf") if raw_pdf_dir.exists() else []):
        try:
            (parsed_dir / f"{pdf_path.stem}.txt").write_text(extract_text_from_pdf(str(pdf_path)), encoding="utf-8")
            logger.info("Parsed PDF: %s", pdf_path.name)
        except Exception as exc:
            logger.error("PDF parsing failed for %s: %s", pdf_path.name, exc)

    for docx_path in (raw_word_dir.glob("*.docx") if raw_word_dir.exists() else []):
        try:
            (parsed_dir / f"{docx_path.stem}.txt").write_text(extract_text_from_word(str(docx_path)), encoding="utf-8")
            logger.info("Parsed Word document: %s", docx_path.name)
        except Exception as exc:
            logger.error("Word parsing failed for %s: %s", docx_path.name, exc)

    for excel_path in (raw_excel_dir.glob("*.xlsx") if raw_excel_dir.exists() else []):
        try:
            pd.DataFrame(extract_data_from_excel(str(excel_path))).to_csv(parsed_dir / f"{excel_path.stem}.csv", index=False)
            logger.info("Parsed Excel workbook: %s", excel_path.name)
        except Exception as exc:
            logger.error("Excel parsing failed for %s: %s", excel_path.name, exc)


def run_media_stage() -> None:
    """Stage 3: Process optional local image/audio/video folders when dependencies exist."""
    logger.info("=== Stage 3: Optional Media Processing ===")
    media_dirs = [RAW_DIR / "images", RAW_DIR / "audio", RAW_DIR / "video"]
    if not any(path.exists() for path in media_dirs):
        logger.info("No media input folders found; media processing skipped")
        return

    if (RAW_DIR / "images").exists():
        try:
            from storage.mongo import process_images_and_save_metadata

            image_paths = [
                str(path)
                for path in (RAW_DIR / "images").glob("*")
                if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
            ]
            if image_paths:
                # Swapped movie_id tracking to match art pipeline domains smoothly
                process_images_and_save_metadata(image_paths, artwork_id="art_collection")
                logger.info("Processed %d image metadata records", len(image_paths))
        except Exception as exc:
            logger.warning("Image metadata processing skipped: %s", exc)

    logger.info("Audio/video processing hooks are configured; add files to data/raw/audio or data/raw/video to extend this stage")


def run_exploratory_analytics_stage(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Stage 4: Run Lab 8-style array, filtering, regex, and quality reporting."""
    logger.info("=== Stage 4: Exploratory Analytics ===")
    arrays = demonstrate_array_creation()
    counts = np.random.randint(100, 1000, len(arrays["popularity"]))
    vector_results = vectorized_operations(arrays["popularity"], counts)
    logger.info("Vectorized mean: %.4f", vector_results["stats"]["mean"])

    df_optimised = optimise_dtypes(df_raw)
    logger.info("Memory comparison after optimisation: %s", memory_comparison(df_raw, df_optimised))

    chunk_stats = chunked_stats(str(RAW_ANALYTICS_CSV))
    logger.info("Chunked stats: %s", chunk_stats)

    highlighted, sample, subset = complex_filter(df_optimised)
    highlighted.to_csv(ANALYTICS_DIR / "highlighted_records.csv", index=False)
    sample.to_csv(ANALYTICS_DIR / "sample_records.csv", index=False)
    subset.to_csv(ANALYTICS_DIR / "filtered_subset.csv", index=False)
    logger.info("Selection outputs saved: highlighted=%d sample=%d subset=%d", len(highlighted), len(sample), len(subset))

    df_regex, text_match_count = perform_regex_analysis(df_optimised)
    df_regex.to_csv(ANALYTICS_DIR / "regex_features.csv", index=False)
    logger.info("Regex text match count: %d", text_match_count)

    quality_df = full_quality_report(df_optimised)
    quality_df.to_csv(ANALYTICS_DIR / "quality_audit.csv", index=False)
    save_missing_heatmap(df_optimised, str(ANALYTICS_DIR / "missing_heatmap.png"))
    plot_distributions(df_optimised, str(ANALYTICS_DIR / "distributions.png"))
    return df_optimised


def run_cleaning_stage(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Stage 5: Execute Lab 9 cleaning constraints and persist cleaned datasets."""
    logger.info("=== Stage 5: Data Cleaning ===")
    CLEANED_DIR.mkdir(parents=True, exist_ok=True)
    df_clean = run_cleaning_pipeline(df_raw, save=True, output_path=str(CLEANED_CSV))
    logger.info("Data cleaning complete with %d records; output=%s", len(df_clean), CLEANED_CSV)
    return df_clean


def run_reporting_stage(df_clean: pd.DataFrame) -> None:
    """Stage 6: Save a compact final reporting summary for dashboard/report use."""
    logger.info("=== Stage 6: Final Reporting ===")
    report_path = CLEANED_DIR / "cleaned_summary.csv"
    summary_rows = [
        {"metric": "row_count", "value": len(df_clean)},
        {"metric": "column_count", "value": len(df_clean.columns)},
        {"metric": "duplicate_id_count", "value": int(df_clean.duplicated(subset=['id']).sum()) if 'id' in df_clean.columns else 0},
    ]
    pd.DataFrame(summary_rows).to_csv(report_path, index=False)
    logger.info("Saved cleaned summary report to %s", report_path)


def print_dashboard_banner() -> None:
    """Stage 7: Print local completion instructions."""
    print("\n" + "=" * 60)
    print("🚀 ART MUSEUM COLLECTION PIPELINE COMPLETE")
    print("=" * 60)
    print(f" Raw analytics CSV: {RAW_ANALYTICS_CSV}")
    print(f" Cleaned CSV:       {CLEANED_CSV}")
    print(f" Pipeline log:      {LOG_FILE_PATH}")
    print("=" * 60 + "\n")


# =====================================================================
# PROJECT MASTER RUNTIME CONTROL
# =====================================================================
def main() -> None:
    logger.info("!!! MASTER PIPELINE STARTED: log=%s !!!", LOG_FILE_PATH)
    ensure_output_dirs()

    df_raw = run_ingestion_stage()
    run_document_parsing_stage()
    run_media_stage()
    run_exploratory_analytics_stage(df_raw)
    df_clean = run_cleaning_stage(df_raw)
    run_reporting_stage(df_clean)
    print_dashboard_banner()

    logger.info("!!! MASTER PIPELINE COMPLETED SUCCESSFULLY !!!")


# Backward-compatible name used by older coursework instructions/tests.
def run_analytics_pipeline() -> None:
    main()


if __name__ == "__main__":
    main()