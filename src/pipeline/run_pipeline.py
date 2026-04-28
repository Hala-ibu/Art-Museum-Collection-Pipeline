import sys
import os
import logging
from pathlib import Path
import pandas as pd
import numpy as np

from analytics.numpy_ops import demonstrate_array_creation, vectorized_operations
from analytics.data_loader import load_from_mongodb, save_to_csv, chunked_stats, optimise_dtypes
from analytics.selector import complex_filter
from analytics.regex_ops import perform_regex_analysis
from analytics.quality_report import full_quality_report, save_missing_heatmap
from analytics.explorer import plot_distributions

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_analytics_pipeline():
    PROCESSED_DIR = Path("data/processed/analytics")
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    RAW_CSV = PROCESSED_DIR / "raw_art_data.csv"
    
    logger.info("Stage 1: NumPy Foundations")
    arrays = demonstrate_array_creation()
    v_results = vectorized_operations(arrays['popularity'], np.random.randint(100, 1000, 4))
    logger.info(f"Vectorized Mean: {v_results['stats']['mean']}")

    logger.info("Stage 2: Data Ingestion")
    df = load_from_mongodb()
    
    if df is None or df.empty:
        logger.error("No data found in MongoDB. Pipeline aborted.")
        return

    save_to_csv(df, str(RAW_CSV))
    
    logger.info("Stage 3: Memory Optimization & Chunking")
    df_opt = optimise_dtypes(df)
    c_stats = chunked_stats(str(RAW_CSV))
    logger.info(f"Global mean from chunks: {c_stats['global_mean']}")

    logger.info("Stage 4: Selection & Filtering")
    acclaimed, sample, subset = complex_filter(df_opt)
    logger.info(f"Filtered subset size: {len(subset)}")

    logger.info("Stage 5: Regex Analysis")
    df_regex, crime_count = perform_regex_analysis(df_opt)
    logger.info(f"Crime related items found: {crime_count}")

    logger.info("Stage 6: Quality Reporting & Visualization")
    quality_df = full_quality_report(df_opt)
    quality_df.to_csv(PROCESSED_DIR / "quality_audit.csv", index=False)
    
    save_missing_heatmap(df_opt, str(PROCESSED_DIR / "missing_heatmap.png"))
    plot_distributions(df_opt, str(PROCESSED_DIR / "distributions.png"))

    logger.info("Pipeline Execution Successful")

if __name__ == "__main__":
    run_analytics_pipeline()