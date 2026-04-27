import re
import pandas as pd

def perform_regex_analysis(df: pd.DataFrame):
    df = df.copy()
    
    if 'title' in df.columns:
        df['extracted_year'] = df['title'].str.extract(r'\((\d{4})\)')
        df['starts_with_the'] = df['title'].str.contains(r'^The\s', flags=re.IGNORECASE)
        
    if 'genres' in df.columns:
        df['genre_list'] = df['genres'].str.findall(r'"name":\s*"([^"]+)"')
        
    if 'overview' in df.columns:
        crime_count = df['overview'].str.contains(r'murder|crime|theft|heist', flags=re.IGNORECASE, na=False).sum()
    else:
        crime_count = 0
        
    return df, crime_count