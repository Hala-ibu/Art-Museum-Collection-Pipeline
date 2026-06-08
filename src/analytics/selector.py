import pandas as pd


def complex_filter(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if "date_start" in df.columns:
        numeric_dates = pd.to_numeric(df["date_start"], errors="coerce")
        highlighted = df.loc[numeric_dates < 1900].copy()
    else:
        highlighted = df.copy()

    sample = df.head(5).copy()

    available_cols = list(df.columns)
    target_cols = [col for col in ["id", "title", "artist_display", "department", "classification"] if col in available_cols]
    
    subset = df[target_cols].copy() if target_cols else df.copy()

    return highlighted, sample, subset