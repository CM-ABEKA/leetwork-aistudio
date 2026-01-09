"""
Data cleaning module for applying transformations to datasets
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional


def clean_dataset(df: pd.DataFrame, operations: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Apply cleaning operations to a dataset

    Args:
        df: pandas DataFrame to clean
        operations: List of cleaning operations to apply

    Returns:
        Cleaned DataFrame
    """
    df_clean = df.copy()

    for op in operations:
        op_type = op.get("type")

        if op_type == "handle_missing":
            df_clean = handle_missing_values(df_clean, op.get("strategy", "median"), op.get("columns"))

        elif op_type == "remove_duplicates":
            df_clean = remove_duplicates(df_clean, op.get("subset"))

        elif op_type == "handle_outliers":
            df_clean = handle_outliers(df_clean, op.get("method", "cap"), op.get("columns"))

        elif op_type == "normalize_types":
            df_clean = normalize_types(df_clean, op.get("type_map", {}))

        elif op_type == "standardize_columns":
            df_clean = standardize_column_names(df_clean)

        elif op_type == "scale_features":
            df_clean = scale_features(df_clean, op.get("method", "standard"), op.get("columns"))

    return df_clean


def handle_missing_values(
    df: pd.DataFrame,
    strategy: str = "median",
    columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Handle missing values in the dataset

    Args:
        df: DataFrame to process
        strategy: Strategy to use ('median', 'mean', 'mode', 'drop', 'forward_fill')
        columns: Specific columns to process (None for all)

    Returns:
        DataFrame with missing values handled
    """
    df_clean = df.copy()
    cols_to_process = columns if columns else df.columns

    for col in cols_to_process:
        if col not in df_clean.columns:
            continue

        if strategy == "drop":
            df_clean = df_clean.dropna(subset=[col])

        elif strategy == "median" and pd.api.types.is_numeric_dtype(df_clean[col]):
            df_clean[col].fillna(df_clean[col].median(), inplace=True)

        elif strategy == "mean" and pd.api.types.is_numeric_dtype(df_clean[col]):
            df_clean[col].fillna(df_clean[col].mean(), inplace=True)

        elif strategy == "mode":
            mode_value = df_clean[col].mode()
            if len(mode_value) > 0:
                df_clean[col].fillna(mode_value[0], inplace=True)

        elif strategy == "forward_fill":
            df_clean[col] = df_clean[col].ffill()

        elif strategy == "zero":
            df_clean[col].fillna(0, inplace=True)

    return df_clean


def remove_duplicates(
    df: pd.DataFrame,
    subset: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Remove duplicate rows from the dataset

    Args:
        df: DataFrame to process
        subset: Columns to consider for identifying duplicates

    Returns:
        DataFrame with duplicates removed
    """
    return df.drop_duplicates(subset=subset, keep='first').reset_index(drop=True)


def handle_outliers(
    df: pd.DataFrame,
    method: str = "cap",
    columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Handle outliers in numeric columns

    Args:
        df: DataFrame to process
        method: Method to use ('cap', 'remove', 'winsorize')
        columns: Specific columns to process (None for all numeric)

    Returns:
        DataFrame with outliers handled
    """
    df_clean = df.copy()

    # Get numeric columns
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    cols_to_process = [c for c in (columns if columns else numeric_cols) if c in numeric_cols]

    for col in cols_to_process:
        Q1 = df_clean[col].quantile(0.25)
        Q3 = df_clean[col].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        if method == "cap":
            # Cap outliers at bounds
            df_clean[col] = df_clean[col].clip(lower=lower_bound, upper=upper_bound)

        elif method == "remove":
            # Remove rows with outliers
            mask = (df_clean[col] >= lower_bound) & (df_clean[col] <= upper_bound)
            df_clean = df_clean[mask]

        elif method == "winsorize":
            # Winsorize at 1st and 99th percentiles
            p01 = df_clean[col].quantile(0.01)
            p99 = df_clean[col].quantile(0.99)
            df_clean[col] = df_clean[col].clip(lower=p01, upper=p99)

    return df_clean.reset_index(drop=True)


def normalize_types(df: pd.DataFrame, type_map: Dict[str, str]) -> pd.DataFrame:
    """
    Normalize column types

    Args:
        df: DataFrame to process
        type_map: Dictionary mapping column names to desired types

    Returns:
        DataFrame with normalized types
    """
    df_clean = df.copy()

    for col, dtype in type_map.items():
        if col not in df_clean.columns:
            continue

        try:
            if dtype == "int":
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').astype('Int64')
            elif dtype == "float":
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            elif dtype == "string":
                df_clean[col] = df_clean[col].astype(str)
            elif dtype == "datetime":
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
            elif dtype == "bool":
                df_clean[col] = df_clean[col].astype(bool)
        except Exception as e:
            print(f"Warning: Could not convert {col} to {dtype}: {e}")

    return df_clean


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names (lowercase, remove spaces, etc.)

    Args:
        df: DataFrame to process

    Returns:
        DataFrame with standardized column names
    """
    df_clean = df.copy()

    # Convert to lowercase and replace spaces/special chars with underscores
    df_clean.columns = (
        df_clean.columns
        .str.lower()
        .str.replace(' ', '_')
        .str.replace('[^a-z0-9_]', '', regex=True)
        .str.strip('_')
    )

    return df_clean


def scale_features(
    df: pd.DataFrame,
    method: str = "standard",
    columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Scale numeric features

    Args:
        df: DataFrame to process
        method: Scaling method ('standard', 'minmax', 'robust')
        columns: Specific columns to scale (None for all numeric)

    Returns:
        DataFrame with scaled features
    """
    from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

    df_clean = df.copy()

    # Get numeric columns
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    cols_to_scale = [c for c in (columns if columns else numeric_cols) if c in numeric_cols]

    if not cols_to_scale:
        return df_clean

    # Select scaler
    if method == "standard":
        scaler = StandardScaler()
    elif method == "minmax":
        scaler = MinMaxScaler()
    elif method == "robust":
        scaler = RobustScaler()
    else:
        return df_clean

    # Apply scaling
    df_clean[cols_to_scale] = scaler.fit_transform(df_clean[cols_to_scale])

    return df_clean
