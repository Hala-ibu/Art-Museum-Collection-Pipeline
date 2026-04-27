import numpy as np
import logging

logger = logging.getLogger(__name__)

def demonstrate_array_creation() -> dict:
    popularity = np.array([120.4, 95.7, 80.2, 63.1])
    zeros = np.zeros((2, 3))
    weights = np.ones(5)
    years = np.arange(2010, 2025, 5)
    score_buffer = np.linspace(0, 1, 10)
    
    arrays = {
        "popularity": popularity,
        "zeros": zeros,
        "weights": weights,
        "years": years,
        "score_buffer": score_buffer
    }
    
    for name, arr in arrays.items():
        print(f"Array: {name:<12} | Shape: {str(arr.shape):<10} | Dtype: {arr.dtype} | Ndim: {arr.ndim}")
    
    return arrays

def vectorized_operations(ratings: np.ndarray, counts: np.ndarray) -> dict:
    weighted_score = ratings * np.log1p(counts)
    normalised = (ratings - np.min(ratings)) / (np.max(ratings) - np.min(ratings))
    high_rated_mask = ratings > 8.0
    
    return {
        "weighted_score": weighted_score,
        "normalised": normalised,
        "high_rated": high_rated_mask,
        "stats": {
            "mean": float(np.mean(ratings)),
            "std": float(np.std(ratings)),
            "max": float(np.max(weighted_score))
        }
    }