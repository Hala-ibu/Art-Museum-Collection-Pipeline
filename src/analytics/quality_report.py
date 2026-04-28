import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def full_quality_report(df: pd.DataFrame):
    issues = []
    missing = df.isna().sum()
    for col, count in missing.items():
        if count > 0:
            pct = (count / len(df)) * 100
            severity = "HIGH" if pct > 30 else "MEDIUM" if pct > 10 else "LOW"
            issues.append({"column": col, "issue": "Missing Values", "count": count, "pct": round(pct, 2), "severity": severity})
    
    num_cols = df.select_dtypes(include=['number'])
    Q1 = num_cols.quantile(0.25)
    Q3 = num_cols.quantile(0.75)
    IQR = Q3 - Q1
    outlier_counts = ((num_cols < (Q1 - 1.5 * IQR)) | (num_cols > (Q3 + 1.5 * IQR))).sum()
    
    for col, count in outlier_counts.items():
        if count > 0:
            issues.append({"column": col, "issue": "Outliers (IQR)", "count": count, "pct": round(count/len(df)*100, 2), "severity": "LOW"})

    return pd.DataFrame(issues)

def save_missing_heatmap(df: pd.DataFrame, path: str):
    plt.figure(figsize=(12, 6))
    sns.heatmap(df.isna(), cbar=False, cmap='viridis', yticklabels=False)
    plt.title("Data Quality: Missing Values Heatmap")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()