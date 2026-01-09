"""
Data analysis module for detecting issues in datasets
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from scipy import stats


def analyze_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze a dataset and detect common data quality issues

    Args:
        df: pandas DataFrame to analyze

    Returns:
        Dictionary containing analysis results with detected issues
    """
    analysis = {
        "shape": {
            "rows": int(df.shape[0]),
            "columns": int(df.shape[1])
        },
        "columns": [],
        "issues": [],
        "summary": {}
    }

    # Analyze each column
    for col in df.columns:
        col_info = analyze_column(df[col], col)
        analysis["columns"].append(col_info)

    # Detect dataset-level issues
    analysis["issues"] = detect_issues(df, analysis["columns"])

    # Generate summary statistics
    analysis["summary"] = generate_summary(df, analysis["issues"])

    return analysis


def analyze_column(series: pd.Series, col_name: str) -> Dict[str, Any]:
    """Analyze a single column"""
    col_info = {
        "name": col_name,
        "dtype": str(series.dtype),
        "missing_count": int(series.isnull().sum()),
        "missing_percent": round(float(series.isnull().sum() / len(series) * 100), 2),
        "unique_count": int(series.nunique()),
        "unique_percent": round(float(series.nunique() / len(series) * 100), 2)
    }

    # Add numeric-specific stats
    if pd.api.types.is_numeric_dtype(series):
        col_info["numeric_stats"] = {
            "mean": float(series.mean()) if not series.isnull().all() else None,
            "median": float(series.median()) if not series.isnull().all() else None,
            "std": float(series.std()) if not series.isnull().all() else None,
            "min": float(series.min()) if not series.isnull().all() else None,
            "max": float(series.max()) if not series.isnull().all() else None,
            "q25": float(series.quantile(0.25)) if not series.isnull().all() else None,
            "q75": float(series.quantile(0.75)) if not series.isnull().all() else None
        }

        # Detect outliers using IQR method
        if not series.isnull().all():
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((series < (Q1 - 1.5 * IQR)) | (series > (Q3 + 1.5 * IQR))).sum()
            col_info["outliers_count"] = int(outliers)
            col_info["outliers_percent"] = round(float(outliers / len(series) * 100), 2)

    # Add categorical-specific stats
    elif pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series):
        value_counts = series.value_counts().head(10)
        col_info["top_values"] = {
            str(k): int(v) for k, v in value_counts.items()
        }
        col_info["is_categorical"] = col_info["unique_count"] < len(series) * 0.5

    return col_info


def detect_issues(df: pd.DataFrame, columns_info: List[Dict]) -> List[Dict[str, Any]]:
    """Detect data quality issues"""
    issues = []

    # Missing values
    total_missing = sum(col["missing_count"] for col in columns_info)
    if total_missing > 0:
        missing_percent = round(total_missing / (df.shape[0] * df.shape[1]) * 100, 2)
        missing_cols = [col["name"] for col in columns_info if col["missing_count"] > 0]
        col_names = ", ".join(missing_cols[:3])
        if len(missing_cols) > 3:
            col_names += f", and {len(missing_cols) - 3} more"

        # Get sample rows with missing values and preview of fixes
        sample_rows = []
        rows_with_missing = df[df.isnull().any(axis=1)]
        if len(rows_with_missing) > 0:
            sample_df = rows_with_missing.head(5)
            for idx, row in sample_df.iterrows():
                # Calculate what the fixed values would be
                fixed_data = {}
                for col in df.columns:
                    if pd.isna(row[col]):
                        # Show what would be filled in
                        if pd.api.types.is_numeric_dtype(df[col]):
                            fixed_data[col] = f"→ {df[col].median():.2f}"
                        else:
                            mode_val = df[col].mode()
                            fixed_data[col] = f"→ {mode_val[0] if len(mode_val) > 0 else 'N/A'}"
                    else:
                        fixed_data[col] = str(row[col])[:50]

                sample_rows.append({
                    "row_number": int(idx) + 1,
                    "data": {col: None if pd.isna(row[col]) else str(row[col])[:50]
                            for col in df.columns},
                    "fixed_data": fixed_data
                })

        issues.append({
            "type": "missing_values",
            "severity": "high" if missing_percent > 10 else "medium" if missing_percent > 5 else "low",
            "issue": "Missing Data (Empty Cells)",
            "count": f"{missing_percent}%",
            "description": f"Found {total_missing} empty cells in columns: {col_names}",
            "technical": "Missing values can cause errors in analysis and reduce prediction accuracy",
            "plain": "Some cells are empty. Like a form with blank fields - we need to fill them in or remove those rows.",
            "action": "Fill empty cells with typical values",
            "action_technical": "Impute with median (numbers) or mode (categories)",
            "sample_data": sample_rows[:5]
        })

    # Duplicate rows
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        dup_percent = round(duplicates / len(df) * 100, 2)

        # Get sample duplicate rows
        sample_rows = []
        dup_mask = df.duplicated(keep=False)
        duplicate_rows = df[dup_mask].head(10)
        for idx, row in duplicate_rows.iterrows():
            is_duplicate = df.duplicated().iloc[idx]
            sample_rows.append({
                "row_number": int(idx) + 1,
                "data": {col: str(row[col])[:50] for col in df.columns},
                "will_be_removed": is_duplicate,
                "fixed_data": {"status": "REMOVED" if is_duplicate else "KEPT"}
            })

        issues.append({
            "type": "duplicates",
            "severity": "medium" if dup_percent > 5 else "low",
            "issue": "Duplicate Rows (Same Data Repeated)",
            "count": f"{dup_percent}% ({duplicates} rows)",
            "description": f"Found {duplicates} rows that are exact copies of other rows",
            "technical": "Duplicate records can bias analysis and inflate metrics",
            "plain": "Some rows appear more than once - like having the same person on a list twice. This can skew your results.",
            "action": "Remove duplicate rows",
            "action_technical": "Keep first occurrence, drop subsequent duplicates",
            "sample_data": sample_rows[:5]
        })

    # Mixed types in columns
    mixed_type_cols = []
    for col in df.columns:
        if df[col].dtype == object:
            # Check if column has mixed types
            types = df[col].dropna().apply(type).unique()
            if len(types) > 1:
                mixed_type_cols.append(col)

    if mixed_type_cols:
        issues.append({
            "type": "mixed_types",
            "severity": "high",
            "issue": "Mixed Data Types (Numbers & Text Together)",
            "count": f"{len(mixed_type_cols)} columns",
            "description": f"Columns with mixed types: {', '.join(mixed_type_cols)}",
            "technical": "Columns contain both numeric and text values, causing type ambiguity",
            "plain": "Some columns have both numbers and text mixed together - like '123' and 'hello' in the same column. This confuses analysis tools.",
            "action": "Convert all values to one consistent type",
            "action_technical": "Normalize to string or convert to numeric where possible"
        })

    # Outliers
    outlier_cols = [col for col in columns_info
                    if "outliers_count" in col and col["outliers_count"] > 0]
    if outlier_cols:
        total_outliers = sum(col["outliers_count"] for col in outlier_cols)
        outlier_percent = round(total_outliers / (df.shape[0] * len(outlier_cols)) * 100, 2)
        col_names = ", ".join([col["name"] for col in outlier_cols[:3]])
        if len(outlier_cols) > 3:
            col_names += f", and {len(outlier_cols) - 3} more"

        # Get sample outlier rows
        sample_rows = []
        for col_info in outlier_cols[:2]:  # Show outliers from first 2 columns
            col_name = col_info["name"]
            if pd.api.types.is_numeric_dtype(df[col_name]):
                Q1 = df[col_name].quantile(0.25)
                Q3 = df[col_name].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR

                outlier_mask = (df[col_name] < lower) | (df[col_name] > upper)
                outlier_rows = df[outlier_mask].head(3)

                for idx, row in outlier_rows.iterrows():
                    original_value = float(row[col_name]) if pd.notna(row[col_name]) else None
                    # Calculate capped value at P99
                    p99 = df[col_name].quantile(0.99)
                    p01 = df[col_name].quantile(0.01)
                    if original_value:
                        capped_value = min(max(original_value, p01), p99)
                    else:
                        capped_value = None

                    # Build fixed data
                    fixed_data = {}
                    for col in df.columns:
                        if col == col_name and original_value:
                            fixed_data[col] = f"→ {capped_value:.2f}"
                        else:
                            fixed_data[col] = str(row[col])[:50]

                    sample_rows.append({
                        "row_number": int(idx) + 1,
                        "column": col_name,
                        "value": original_value,
                        "range": f"{Q1:.2f} - {Q3:.2f}",
                        "data": {col: str(row[col])[:50] for col in df.columns},
                        "fixed_data": fixed_data
                    })

        issues.append({
            "type": "outliers",
            "severity": "medium",
            "issue": "Unusual Values (Outliers)",
            "count": f"{outlier_percent}% in {len(outlier_cols)} columns",
            "description": f"Found {total_outliers} extreme values in columns: {col_names}",
            "technical": "Using IQR (Interquartile Range) method to detect statistical outliers",
            "plain": "Some numbers are way too high or too low compared to the rest. These extreme values can throw off predictions.",
            "action": "Limit extreme values to reasonable range",
            "action_technical": "Cap at 99th percentile (P99) or remove outliers",
            "sample_data": sample_rows[:5]
        })

    # High cardinality
    high_card_cols = [col for col in columns_info
                      if col["unique_percent"] > 90 and col["dtype"] == "object"]
    if high_card_cols:
        issues.append({
            "type": "high_cardinality",
            "severity": "low",
            "issue": "High cardinality",
            "count": f"{len(high_card_cols)} columns",
            "description": "Columns with too many unique values may need encoding",
            "action": "Consider target encoding or dimensionality reduction"
        })

    return issues


def generate_summary(df: pd.DataFrame, issues: List[Dict]) -> Dict[str, Any]:
    """Generate overall summary"""
    return {
        "total_cells": int(df.shape[0] * df.shape[1]),
        "total_issues": len(issues),
        "severity_breakdown": {
            "high": len([i for i in issues if i["severity"] == "high"]),
            "medium": len([i for i in issues if i["severity"] == "medium"]),
            "low": len([i for i in issues if i["severity"] == "low"])
        },
        "recommended_actions": [issue["action"] for issue in issues if issue["severity"] in ["high", "medium"]]
    }
