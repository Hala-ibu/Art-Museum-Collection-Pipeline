import pandas as pd
import logging

logger = logging.getLogger(__name__)

def complex_filter(df: pd.DataFrame):
    acclaimed = df.loc[df['vote_average'] >= 8.5, ['title', 'vote_average', 'popularity']]
    
    sample = df.iloc[::20]
    
    mask = (
        df['original_language'].isin(['en', 'fr', 'it']) & 
        df['vote_average'].between(7.0, 9.0) &
        (df['popularity'] > 10.0)
    )
    filtered_subset = df[mask]
    
    return acclaimed, sample, filtered_subset