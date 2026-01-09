"""
Core training pipeline for AutoML.
Handles data preprocessing, model training, evaluation, and persistence.
"""

import pandas as pd
import numpy as np
import pickle
import os
from typing import Dict, Any, Callable
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, mean_absolute_error, r2_score,
    confusion_matrix, classification_report
)

# Import algorithm modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from algorithms.classification import (
    get_random_forest_classifier,
    get_gradient_boosting_classifier,
    get_logistic_regression,
    get_svm_classifier
)
from algorithms.regression import (
    get_random_forest_regressor,
    get_gradient_boosting_regressor,
    get_linear_regression,
    get_ridge_regression
)


# Algorithm mapping
ALGORITHM_MAP = {
    'random_forest': {
        'classification': get_random_forest_classifier,
        'regression': get_random_forest_regressor
    },
    'gradient_boosting': {
        'classification': get_gradient_boosting_classifier,
        'regression': get_gradient_boosting_regressor
    },
    'logistic_regression': {
        'classification': get_logistic_regression,
        'regression': None
    },
    'linear_regression': {
        'classification': None,
        'regression': get_linear_regression
    },
    'svm': {
        'classification': get_svm_classifier,
        'regression': None
    },
    'ridge': {
        'classification': None,
        'regression': get_ridge_regression
    }
}


def detect_problem_type(y_series: pd.Series) -> str:
    """
    Auto-detect if the problem is classification or regression.

    Args:
        y_series: Target variable series

    Returns:
        'classification' or 'regression'
    """
    # Check if target is numeric
    if pd.api.types.is_numeric_dtype(y_series):
        # Check number of unique values
        n_unique = y_series.nunique()
        n_samples = len(y_series)

        # If less than 20 unique values or less than 5% unique, likely classification
        if n_unique < 20 or (n_unique / n_samples) < 0.05:
            return 'classification'
        else:
            return 'regression'
    else:
        # Non-numeric target is classification
        return 'classification'


def preprocess_data(X_train: pd.DataFrame, X_test: pd.DataFrame):
    """
    Preprocess training and test data.
    Handles missing values, categorical encoding, and scaling.

    Args:
        X_train: Training features
        X_test: Test features

    Returns:
        Tuple of (X_train_processed, X_test_processed, preprocessing_info)
    """
    X_train = X_train.copy()
    X_test = X_test.copy()
    preprocessing_info = {}

    # Identify column types
    numeric_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = X_train.select_dtypes(include=['object', 'category']).columns.tolist()

    preprocessing_info['numeric_cols'] = numeric_cols
    preprocessing_info['categorical_cols'] = categorical_cols

    # Handle missing values in numeric columns
    if numeric_cols:
        imputer = SimpleImputer(strategy='median')
        X_train[numeric_cols] = imputer.fit_transform(X_train[numeric_cols])
        X_test[numeric_cols] = imputer.transform(X_test[numeric_cols])

    # Encode categorical columns
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        # Fit on combined data to handle unseen categories
        combined = pd.concat([X_train[col].astype(str), X_test[col].astype(str)])
        le.fit(combined)
        X_train[col] = le.transform(X_train[col].astype(str))
        X_test[col] = le.transform(X_test[col].astype(str))
        label_encoders[col] = le

    preprocessing_info['label_encoders'] = label_encoders

    # Scale numeric features
    if numeric_cols:
        scaler = StandardScaler()
        X_train[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
        X_test[numeric_cols] = scaler.transform(X_test[numeric_cols])
        preprocessing_info['scaler'] = scaler

    return X_train, X_test, preprocessing_info


def get_model_for_algorithm(algorithm: str, problem_type: str):
    """
    Get model instance based on algorithm name and problem type.

    Args:
        algorithm: Algorithm name (e.g., 'random_forest', 'gradient_boosting')
        problem_type: 'classification' or 'regression'

    Returns:
        Instantiated model
    """
    if algorithm not in ALGORITHM_MAP:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    model_func = ALGORITHM_MAP[algorithm].get(problem_type)
    if model_func is None:
        raise ValueError(f"{algorithm} not applicable for {problem_type}")

    return model_func()


def evaluate_model(model, X_test, y_test, problem_type: str, detailed: bool = True) -> Dict[str, Any]:
    """
    Evaluate model and calculate appropriate metrics.

    Args:
        model: Trained model
        X_test: Test features
        y_test: Test labels
        problem_type: 'classification' or 'regression'
        detailed: Whether to include detailed metrics

    Returns:
        Dictionary of metrics
    """
    y_pred = model.predict(X_test)
    metrics = {}

    if problem_type == 'classification':
        metrics['accuracy'] = float(accuracy_score(y_test, y_pred))

        # Handle binary vs multiclass
        try:
            metrics['precision'] = float(precision_score(y_test, y_pred, average='weighted', zero_division=0))
            metrics['recall'] = float(recall_score(y_test, y_pred, average='weighted', zero_division=0))
            metrics['f1_score'] = float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
        except:
            metrics['precision'] = None
            metrics['recall'] = None
            metrics['f1_score'] = None

        if detailed:
            metrics['confusion_matrix'] = confusion_matrix(y_test, y_pred).tolist()

    else:  # regression
        metrics['rmse'] = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        metrics['mae'] = float(mean_absolute_error(y_test, y_pred))
        metrics['r2_score'] = float(r2_score(y_test, y_pred))
        metrics['accuracy'] = None
        metrics['precision'] = None
        metrics['recall'] = None
        metrics['f1_score'] = None

    return metrics


def save_model_pickle(model, path: str, metadata: Dict[str, Any]):
    """
    Save model and metadata as pickle file.

    Args:
        model: Trained model
        path: File path to save to
        metadata: Additional metadata to save with model
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)

    model_bundle = {
        'model': model,
        'metadata': metadata
    }

    with open(path, 'wb') as f:
        pickle.dump(model_bundle, f)


def train_model_with_algorithm(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    target_column: str,
    algorithm: str,
    job_id: str,
    progress_callback: Callable[[int, str], None]
) -> Dict[str, Any]:
    """
    Main training function - orchestrates the entire training pipeline.

    Args:
        train_df: Training dataframe with target column
        test_df: Test dataframe with target column
        target_column: Name of target column
        algorithm: Algorithm to use
        job_id: Unique job identifier
        progress_callback: Function to report progress (percentage, stage)

    Returns:
        Dictionary with training results and paths
    """
    try:
        # Stage 1: Validate data (10%)
        progress_callback(10, "Validating data")

        if target_column not in train_df.columns:
            raise ValueError(f"Target column '{target_column}' not found in training data")
        if target_column not in test_df.columns:
            raise ValueError(f"Target column '{target_column}' not found in test data")

        # Separate features and target
        X_train = train_df.drop(columns=[target_column])
        y_train = train_df[target_column]
        X_test = test_df.drop(columns=[target_column])
        y_test = test_df[target_column]

        # Stage 2: Detect problem type (20%)
        progress_callback(20, "Detecting problem type")
        problem_type = detect_problem_type(y_train)

        # Stage 3: Preprocess data (30%)
        progress_callback(30, "Preprocessing data")
        X_train_processed, X_test_processed, preprocessing_info = preprocess_data(X_train, X_test)

        # Stage 4: Get model (40%)
        progress_callback(40, f"Initializing {algorithm}")
        model = get_model_for_algorithm(algorithm, problem_type)

        # Stage 5: Train model (50-80%)
        progress_callback(50, f"Training {algorithm}")
        model.fit(X_train_processed, y_train)
        progress_callback(80, "Training complete")

        # Stage 6: Evaluate (90%)
        progress_callback(90, "Evaluating model")
        metrics = evaluate_model(model, X_test_processed, y_test, problem_type, detailed=True)

        # Stage 7: Save model (95%)
        progress_callback(95, "Saving model")
        model_path = f"/tmp/training_jobs/{job_id}/model.pkl"

        metadata = {
            'algorithm': algorithm,
            'problem_type': problem_type,
            'target_column': target_column,
            'training_samples': len(train_df),
            'test_samples': len(test_df),
            'features': X_train.columns.tolist(),
            'preprocessing': {
                'numeric_cols': preprocessing_info.get('numeric_cols', []),
                'categorical_cols': preprocessing_info.get('categorical_cols', [])
            }
        }

        save_model_pickle(model, model_path, metadata)
        progress_callback(100, "Complete")

        # Return results
        return {
            'success': True,
            'algorithm': algorithm,
            'problem_type': problem_type,
            'model_path': model_path,
            'metrics': metrics,
            'training_samples': len(train_df),
            'test_samples': len(test_df),
            'feature_count': len(X_train.columns)
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'algorithm': algorithm
        }
