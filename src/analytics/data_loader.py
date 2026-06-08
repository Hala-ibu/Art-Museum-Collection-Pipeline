import logging
from pathlib import Path
import pandas as pd
from pymongo import MongoClient

logger = logging.getLogger(__name__)


def load_from_mongodb(
    uri: str = "mongodb://localhost:27017/",
    db: str = "Art-Museum-Collection-Pipeline",
    collection: str = "art_museum_collection",
) -> pd.DataFrame:
    client = MongoClient(uri)
    try:
        db_conn = client[db]
        cursor = db_conn[collection].find({}, {"_id": 0})
        df = pd.DataFrame(list(cursor))
        logger.info("Retrieved %d raw art documents from MongoDB.", len(df))
        return df
    except Exception as e:
        logger.error("Failed to fetch documents from MongoDB: %s", e)
        return pd.DataFrame()
    finally:
        client.close()


def load_from_csv(path: str, low_memory: bool = False) -> pd.DataFrame:
    csv_path = Path(path)
    if not csv_path.exists():
        logger.error("Target analytics source CSV not found at: %s", csv_path)
        return pd.DataFrame()
    return pd.read_csv(csv_path, low_memory=low_memory)


def save_to_csv(df: pd.DataFrame, path: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("Persisted dataframe seamlessly to %s", output_path)


def chunked_stats(csv_path: str, chunk_size: int = 500) -> dict:
    total_sum, total_rows = 0, 0
    category_accumulator = {}

    for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
        if "date_start" in chunk.columns:
            valid_numeric = pd.to_numeric(chunk["date_start"], errors="coerce").dropna()
            total_sum += valid_numeric.sum()
            total_rows += len(valid_numeric)

        categorical_target = (
            "language" if "language" in chunk.columns else "department"
        )
        if categorical_target in chunk.columns:
            counts = chunk[categorical_target].value_counts().to_dict()
            for value, count in counts.items():
                category_accumulator[value] = (
                    category_accumulator.get(value, 0) + count
                )

    return {
        "global_mean": total_sum / total_rows if total_rows > 0 else 0,
        "total_rows": total_rows,
        "distribution": category_accumulator,
    }


def optimise_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    df_opt = df.copy()
    for col in df_opt.select_dtypes(include=["float"]).columns:
        df_opt[col] = pd.to_numeric(df_opt[col], downcast="float")
    for col in df_opt.select_dtypes(include=["integer"]).columns:
        df_opt[col] = pd.to_numeric(df_opt[col], downcast="integer")
    for col in df_opt.select_dtypes(include=["object"]).columns:
        # If the column cardinality is low enough (<50% unique elements), cast to category
        if len(df_opt) > 0 and (df_opt[col].nunique() / len(df_opt) < 0.5):
            df_opt[col] = df_opt[col].astype("category")
    return df_opt


def memory_comparison(df_old: pd.DataFrame, df_new: pd.DataFrame) -> dict:
    old_mem = df_old.memory_usage(deep=True).sum()
    new_mem = df_new.memory_usage(deep=True).sum()
    reduction = ((old_mem - new_mem) / old_mem * 100) if old_mem > 0 else 0.0

    return {
        "old_memory_bytes": old_mem,
        "new_memory_bytes": new_mem,
        "reduction_pct": reduction,
    }