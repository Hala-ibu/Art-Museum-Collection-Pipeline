import re
import pandas as pd


def perform_regex_analysis(df: pd.DataFrame):
    df = df.copy()
    
    if 'title' in df.columns:
        df['extracted_year'] = df['title'].str.extract(r'\((\d{4})\)')
        df['starts_with_the'] = df['title'].str.contains(r'^The\s', flags=re.IGNORECASE, na=False)
        
    if 'genres' in df.columns:
        df['genre_list'] = df['genres'].str.findall(r'"name":\s*"([^"]+)"')
        
    text_col = 'overview' if 'overview' in df.columns else 'description' if 'description' in df.columns else None
    if text_col:
        crime_count = df[text_col].str.contains(r'murder|crime|theft|heist', flags=re.IGNORECASE, na=False).sum()
    else:
        crime_count = 0
        
    return df, crime_count


def flag_invalid_date_formats(df: pd.DataFrame, column: str = 'date_display') -> pd.Series:
    if column not in df.columns:
        return pd.Series(False, index=df.index)
    pattern = r'(?<!\d)-?\d{1,4}(?!\d)'
    return ~df[column].astype('string').str.contains(pattern, regex=True, na=False)


def flag_invalid_language_codes(df: pd.DataFrame, column: str = 'language') -> pd.Series:
    if column not in df.columns:
        for candidate in ('original_language', 'country_code'):
            if candidate in df.columns:
                column = candidate
                break
        else:
            return pd.Series(False, index=df.index)
    values = df[column].astype('string')
    return values.notna() & ~values.str.match(r'^[a-z]{2}$', na=False)


def extract_numeric_values(text: pd.Series | pd.DataFrame, column: str | None = None) -> pd.Series:
    series = text[column] if isinstance(text, pd.DataFrame) and column else text
    extracted = series.astype('string').str.extract(r'(-?\d+(?:\.\d+)?)', expand=False)
    return pd.to_numeric(extracted, errors='coerce')


def flag_short_overviews(df: pd.DataFrame, column: str = 'description', min_words: int = 5) -> pd.Series:
    actual = column if column in df.columns else 'overview' if 'overview' in df.columns else None
    if actual is None:
        return pd.Series(False, index=df.index)
    word_counts = df[actual].astype('string').str.findall(r'\b\w+\b').str.len().fillna(0)
    return word_counts < min_words