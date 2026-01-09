"""
Data splitting module for train/test split operations
"""
import pandas as pd
from typing import Dict, Any, Optional
from sklearn.model_selection import train_test_split


def split_dataset(
    df: pd.DataFrame,
    train_ratio: float = 0.8,
    strategy: str = "random",
    random_seed: int = 42,
    target_column: Optional[str] = None
) -> Dict[str, Any]:
    """
    Split dataset into train and test sets

    Args:
        df: DataFrame to split
        train_ratio: Ratio of training data (0.0 to 1.0)
        strategy: Split strategy ('random' or 'stratified')
        random_seed: Random seed for reproducibility
        target_column: Target column for stratified split (required for stratified)

    Returns:
        Dictionary with train and test DataFrames and metadata

    Raises:
        ValueError: If parameters are invalid
    """
    # Validate train_ratio
    if not 0.0 < train_ratio < 1.0:
        raise ValueError("train_ratio must be between 0.0 and 1.0")

    # Validate dataset size
    if len(df) < 10:
        raise ValueError("Dataset is too small to split (minimum 10 rows required)")

    # Validate strategy
    if strategy not in ["random", "stratified"]:
        raise ValueError("strategy must be 'random' or 'stratified'")

    # Validate stratified split requirements
    if strategy == "stratified":
        if target_column is None:
            raise ValueError("target_column is required for stratified split")

        if target_column not in df.columns:
            raise ValueError(f"Column '{target_column}' not found in dataset")

        # Check if target column is suitable for stratification
        unique_values = df[target_column].nunique()
        if unique_values > len(df) * 0.5:
            raise ValueError(
                f"Target column '{target_column}' has too many unique values "
                f"({unique_values}) for stratified splitting. Try random split instead."
            )

        # Check if all classes have at least 2 samples
        value_counts = df[target_column].value_counts()
        if value_counts.min() < 2:
            raise ValueError(
                f"Target column '{target_column}' has classes with fewer than 2 samples. "
                "Cannot perform stratified split."
            )

    # Perform the split
    try:
        if strategy == "stratified":
            train_df, test_df = train_test_split(
                df,
                train_size=train_ratio,
                random_state=random_seed,
                stratify=df[target_column]
            )
        else:
            train_df, test_df = train_test_split(
                df,
                train_size=train_ratio,
                random_state=random_seed
            )
    except Exception as e:
        raise ValueError(f"Error during split: {str(e)}")

    # Calculate metadata
    result = {
        "train_df": train_df,
        "test_df": test_df,
        "train_shape": {
            "rows": int(train_df.shape[0]),
            "columns": int(train_df.shape[1])
        },
        "test_shape": {
            "rows": int(test_df.shape[0]),
            "columns": int(test_df.shape[1])
        },
        "split_config": {
            "train_ratio": train_ratio,
            "test_ratio": 1.0 - train_ratio,
            "strategy": strategy,
            "random_seed": random_seed,
            "target_column": target_column
        }
    }

    return result


def get_split_summary(df: pd.DataFrame, train_df: pd.DataFrame, test_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary statistics about the split

    Args:
        df: Original DataFrame
        train_df: Training DataFrame
        test_df: Test DataFrame

    Returns:
        Dictionary with summary statistics
    """
    return {
        "original_rows": int(len(df)),
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "train_percentage": round(len(train_df) / len(df) * 100, 2),
        "test_percentage": round(len(test_df) / len(df) * 100, 2),
        "columns": int(df.shape[1])
    }
