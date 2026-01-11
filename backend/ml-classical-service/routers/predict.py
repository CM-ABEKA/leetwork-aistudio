"""
Prediction router for making predictions with trained models.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import pandas as pd
import numpy as np
import pickle
import os
import io
from typing import Optional, Dict, Any
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.storage import get_minio_client

router = APIRouter()


def get_model_path(job_id: str, project_id: Optional[str] = None) -> str:
    """
    Get model path, downloading from MinIO if not available locally.

    Args:
        job_id: Training job ID
        project_id: Optional project ID (tries to infer if not provided)

    Returns:
        Path to local model file

    Raises:
        HTTPException: If model not found locally or in MinIO
    """
    # Try local path first
    local_path = f"/tmp/training_jobs/{job_id}/model.pkl"

    if os.path.exists(local_path):
        return local_path

    # Model not found locally, try to download from MinIO
    print(f"Model not found locally for job {job_id}, attempting MinIO download...")

    try:
        minio_client = get_minio_client()

        # If project_id not provided, we need to search for the model
        # Try common pattern: models/{project_id}/{job_id}/model.pkl
        # For now, we'll list objects and find the matching job_id

        from minio.error import S3Error

        bucket = minio_client.bucket
        prefix = "models/"

        # Search for model in MinIO
        found_object = None
        try:
            objects = minio_client.client.list_objects(bucket, prefix=prefix, recursive=True)
            for obj in objects:
                if f"/{job_id}/model.pkl" in obj.object_name:
                    found_object = obj.object_name
                    break
        except S3Error as e:
            print(f"Error searching MinIO: {e}")

        if not found_object:
            raise HTTPException(
                status_code=404,
                detail=f"Model not found. The model may have been deleted or not uploaded to storage. Job ID: {job_id}"
            )

        # Download model from MinIO
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        minio_client.download_model(found_object, local_path)

        print(f"Successfully downloaded model from MinIO: {found_object}")
        return local_path

    except HTTPException:
        raise
    except Exception as e:
        print(f"Failed to retrieve model from MinIO: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Model not found locally or in storage. Please retrain the model. Job ID: {job_id}"
        )


def preprocess_prediction_data(df: pd.DataFrame, preprocessing_info: Dict[str, Any]) -> pd.DataFrame:
    """
    Preprocess new data for prediction using saved preprocessing transformers.
    Model was trained only on features available in the prediction sample, so all features should be present.

    Args:
        df: Input dataframe to preprocess
        preprocessing_info: Dictionary containing preprocessing transformers and column info

    Returns:
        Preprocessed dataframe ready for model prediction
    """
    df = df.copy()

    # Get saved preprocessing info
    numeric_cols = preprocessing_info.get('numeric_cols', [])
    categorical_cols = preprocessing_info.get('categorical_cols', [])
    training_columns = preprocessing_info.get('training_columns', [])
    label_encoders = preprocessing_info.get('label_encoders', {})
    scaler = preprocessing_info.get('scaler')
    imputer = preprocessing_info.get('imputer')

    # Check for missing columns - should not happen if model was trained correctly with prediction sample
    missing_cols = [col for col in training_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Prediction data is missing required columns: {missing_cols}. "
            f"Model was trained with these features based on your prediction sample."
        )

    # Remove extra columns not present in training
    extra_cols = [col for col in df.columns if col not in training_columns]
    if extra_cols:
        df = df.drop(columns=extra_cols)

    # Ensure column order matches training
    df = df[training_columns]

    # Encode categorical columns using saved encoders
    for col in categorical_cols:
        if col in df.columns and col in label_encoders:
            le = label_encoders[col]
            # Handle unseen categories by replacing with first known category
            df[col] = df[col].astype(str)
            df[col] = df[col].apply(lambda x: x if x in le.classes_ else le.classes_[0])
            df[col] = le.transform(df[col])

    # Handle missing values using saved imputer
    if numeric_cols and imputer:
        df[numeric_cols] = imputer.transform(df[numeric_cols])

    # Scale numeric features using saved scaler
    if numeric_cols and scaler:
        df[numeric_cols] = scaler.transform(df[numeric_cols])

    return df


@router.get("/features/{job_id}")
async def get_model_features(job_id: str):
    """
    Get the feature names and types for a trained model.

    Args:
        job_id: Training job ID

    Returns:
        Feature information including names, types, and target column
    """
    try:
        # Load the trained model (from local or MinIO)
        model_path = get_model_path(job_id)

        with open(model_path, 'rb') as f:
            model_bundle = pickle.load(f)

        metadata = model_bundle['metadata']

        return {
            "features": metadata['features'],
            "target_column": metadata['target_column'],
            "problem_type": metadata['problem_type'],
            "numeric_cols": metadata.get('preprocessing', {}).get('numeric_cols', []),
            "categorical_cols": metadata.get('preprocessing', {}).get('categorical_cols', [])
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model features: {str(e)}")


@router.post("/batch")
async def predict_batch(
    prediction_file: UploadFile = File(...),
    job_id: str = Form(...)
):
    """
    Make batch predictions on a CSV file using a trained model.

    Args:
        prediction_file: CSV file with features (no target column)
        job_id: Training job ID (used to locate the model)

    Returns:
        CSV file with predictions added
    """
    try:
        # Validate file type
        if not prediction_file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")

        # Load the uploaded CSV
        contents = await prediction_file.read()
        try:
            df = pd.read_csv(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")

        # Load the trained model (from local or MinIO)
        model_path = get_model_path(job_id)

        try:
            with open(model_path, 'rb') as f:
                model_bundle = pickle.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")

        model = model_bundle['model']
        metadata = model_bundle['metadata']
        target_column = metadata['target_column']

        # Check if target column already exists (if so, we'll overwrite)
        if target_column in df.columns:
            df_original = df.drop(columns=[target_column])
            had_target = True
        else:
            df_original = df.copy()
            had_target = False

        # Preprocess the input data using saved preprocessing transformers
        preprocessing_info = metadata.get('preprocessing', {})

        try:
            df_processed = preprocess_prediction_data(df_original, preprocessing_info)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Preprocessing failed: {str(e)}"
            )

        # Make predictions
        try:
            predictions = model.predict(df_processed)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Prediction failed: {str(e)}"
            )

        # Add predictions to the original dataframe
        df_result = df_original.copy()
        df_result[target_column] = predictions

        # Convert to CSV
        output = io.StringIO()
        df_result.to_csv(output, index=False)
        output.seek(0)

        # Return as downloadable CSV
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=predictions_{job_id[:8]}.csv"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/single")
async def predict_single(
    job_id: str = Form(...),
    features: str = Form(...)  # JSON string of features
):
    """
    Make a single prediction using a trained model.

    Args:
        job_id: Training job ID
        features: JSON string with feature values

    Returns:
        Prediction value
    """
    try:
        import json

        # Parse features
        try:
            feature_dict = json.loads(features)
        except:
            raise HTTPException(status_code=400, detail="Invalid JSON for features")

        # Load the trained model (from local or MinIO)
        model_path = get_model_path(job_id)

        with open(model_path, 'rb') as f:
            model_bundle = pickle.load(f)

        model = model_bundle['model']
        metadata = model_bundle['metadata']

        # Convert features to DataFrame
        df = pd.DataFrame([feature_dict])

        # Preprocess using saved preprocessing transformers
        preprocessing_info = metadata.get('preprocessing', {})
        df_processed = preprocess_prediction_data(df, preprocessing_info)

        # Predict
        prediction = model.predict(df_processed)[0]

        # For classification, also get probabilities if available
        probabilities = None
        if hasattr(model, 'predict_proba'):
            try:
                proba = model.predict_proba(df_processed)[0]
                probabilities = proba.tolist()
            except:
                pass

        return {
            "prediction": float(prediction) if isinstance(prediction, (int, float)) else str(prediction),
            "probabilities": probabilities,
            "target_column": metadata['target_column']
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
