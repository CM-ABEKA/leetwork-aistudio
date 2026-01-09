"""
Prediction router for making predictions with trained models.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
import pandas as pd
import pickle
import os
import io
from typing import Optional

router = APIRouter()


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

        # Load the trained model
        model_path = f"/tmp/training_jobs/{job_id}/model.pkl"

        if not os.path.exists(model_path):
            raise HTTPException(status_code=404, detail="Model not found. Please train the model first.")

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

        # Preprocess the input data (same as training)
        from core.training import preprocess_data

        # Create a dummy dataframe for preprocessing (we need train and test)
        # Use the input data as both train and test
        df_processed, _, _ = preprocess_data(df_original, df_original.copy())

        # Make predictions
        try:
            predictions = model.predict(df_processed)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Prediction failed. Ensure CSV has the same features as training data. Error: {str(e)}"
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

        # Load the trained model
        model_path = f"/tmp/training_jobs/{job_id}/model.pkl"

        if not os.path.exists(model_path):
            raise HTTPException(status_code=404, detail="Model not found")

        with open(model_path, 'rb') as f:
            model_bundle = pickle.load(f)

        model = model_bundle['model']
        metadata = model_bundle['metadata']

        # Convert features to DataFrame
        df = pd.DataFrame([feature_dict])

        # Preprocess
        from core.training import preprocess_data
        df_processed, _, _ = preprocess_data(df, df.copy())

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
