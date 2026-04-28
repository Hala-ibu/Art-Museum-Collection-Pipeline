import matplotlib.pyplot as plt
import pandas as pd

def plot_distributions(df: pd.DataFrame, save_path: str):
    df.hist(bins=30, figsize=(15, 10))
    plt.tight_layout()
    plt.savefig(save_path)