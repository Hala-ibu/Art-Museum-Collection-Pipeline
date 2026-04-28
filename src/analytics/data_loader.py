import pandas as pd
import logging
from pymongo import MongoClient
from pathlib import Path

logger = logging.getLogger(__name__)

def load_from_mongodb(uri="mongodb://localhost:27017/", db="Art-Museum-Collection-Pipeline", collection="art_museum_collection"):
    client = MongoClient(uri)
    try:
        db_conn = client[db]
        cursor = db_conn[collection].find({}, {"_id": 0})
        df = pd.DataFrame(list(cursor))
        return df
    finally:
        client.close()

def save_to_csv(df: pd.DataFrame, path: str):
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

def chunked_stats(csv_path: str, chunk_size: int = 500):
    total_sum, total_rows = 0, 0
    lang_accumulator = {}

    for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
        if 'vote_average' in chunk.columns:
            valid = chunk['vote_average'].dropna()
            total_sum += valid.sum()
            total_rows += len(valid)
        
        if 'original_language' in chunk.columns:
            counts = chunk['original_language'].value_counts().to_dict()
            for lang, count in counts.items():
                lang_accumulator[lang] = lang_accumulator.get(lang, 0) + count

    return {
        "global_mean": total_sum / total_rows if total_rows > 0 else 0,
        "total_rows": total_rows,
        "distribution": lang_accumulator
    }

def optimise_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    df_opt = df.copy()
    for col in df_opt.select_dtypes(include=['float']).columns:
        df_opt[col] = pd.to_numeric(df_opt[col], downcast='float')
    for col in df_opt.select_dtypes(include=['integer']).columns:
        df_opt[col] = pd.to_numeric(df_opt[col], downcast='integer')
    for col in df_opt.select_dtypes(include=['object']).columns:
        if df_opt[col].nunique() / len(df_opt) < 0.5:
            df_opt[col] = df_opt[col].astype('category')
    return df_opt