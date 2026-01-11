"""
Training router for AutoML model training.
Provides endpoints for starting training, checking status, getting results, and downloading models.
"""

from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from typing import Optional
import pandas as pd
import os
import uuid
import json
import traceback
from datetime import datetime

# Import training functions
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.training import train_model_with_algorithm
from utils.storage import get_minio_client

router = APIRouter()

# Job tracking with file persistence
JOBS_FILE = "/tmp/training_jobs_metadata.json"

def load_training_jobs():
    """Load training jobs from disk."""
    if os.path.exists(JOBS_FILE):
        try:
            with open(JOBS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load training jobs from disk: {e}")
    return {}

def save_training_jobs(jobs):
    """Save training jobs to disk."""
    try:
        with open(JOBS_FILE, 'w') as f:
            json.dump(jobs, f, indent=2)
    except Exception as e:
        print(f"Failed to save training jobs to disk: {e}")

# Load existing jobs on startup
training_jobs = load_training_jobs()
print(f"Loaded {len(training_jobs)} training jobs from disk")


@router.post("/automl")
async def start_training(
    background_tasks: BackgroundTasks,
    training_file: UploadFile = File(...),
    test_file: UploadFile = File(...),
    prediction_sample_file: UploadFile = File(None),  # Optional
    model_name: str = Form(...),
    target_column: str = Form(...),
    algorithm: str = Form(...),
    project_id: str = Form(...)
):
    """
    Start AutoML training job.

    Args:
        training_file: Training dataset CSV file
        test_file: Test dataset CSV file
        prediction_sample_file: Optional sample of prediction data (to determine available features)
        model_name: Name for the trained model
        target_column: Name of the target column in datasets
        algorithm: Algorithm to use (random_forest, gradient_boosting, etc.)
        project_id: Project UUID

    Returns:
        Job ID and initial status
    """
    # Generate unique job ID
    job_id = str(uuid.uuid4())

    try:
        # Create temp directory for this job
        temp_dir = f"/tmp/training_jobs/{job_id}"
        os.makedirs(temp_dir, exist_ok=True)

        # Save uploaded files
        train_path = os.path.join(temp_dir, "train.csv")
        test_path = os.path.join(temp_dir, "test.csv")
        prediction_sample_path = None

        # Write files to disk
        with open(train_path, "wb") as f:
            content = await training_file.read()
            f.write(content)

        with open(test_path, "wb") as f:
            content = await test_file.read()
            f.write(content)

        # Save prediction sample if provided
        if prediction_sample_file:
            prediction_sample_path = os.path.join(temp_dir, "prediction_sample.csv")
            with open(prediction_sample_path, "wb") as f:
                content = await prediction_sample_file.read()
                f.write(content)

        # Initialize job status
        training_jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "progress": 0,
            "stage": "initializing",
            "result": None,
            "error": None,
            "config": {
                "model_name": model_name,
                "target_column": target_column,
                "algorithm": algorithm,
                "project_id": project_id
            },
            "created_at": datetime.utcnow().isoformat()
        }
        save_training_jobs(training_jobs)

        # Start training in background
        background_tasks.add_task(
            run_training_background,
            job_id,
            train_path,
            test_path,
            prediction_sample_path,
            model_name,
            target_column,
            algorithm,
            project_id
        )

        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Training job started successfully"
        }

    except Exception as e:
        # Clean up on error
        if job_id in training_jobs:
            del training_jobs[job_id]
        raise HTTPException(status_code=500, detail=f"Failed to start training: {str(e)}")


@router.get("/status/{job_id}")
async def get_training_status(job_id: str):
    """
    Get current training status.

    Args:
        job_id: Training job UUID

    Returns:
        Current status, progress, and stage
    """
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")

    job = training_jobs[job_id]

    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "stage": job["stage"],
        "error": job.get("error"),
        "created_at": job.get("created_at")
    }


@router.get("/result/{job_id}")
async def get_training_result(job_id: str):
    """
    Get final training results.

    Args:
        job_id: Training job UUID

    Returns:
        Training metrics, model path, and download URL
    """
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")

    job = training_jobs[job_id]

    if job["status"] not in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Training not yet completed")

    if job["status"] == "failed":
        raise HTTPException(status_code=500, detail=job.get("error", "Training failed"))

    return {
        "job_id": job_id,
        "status": job["status"],
        "result": job["result"],
        "config": job["config"]
    }


@router.get("/download/{job_id}")
async def download_model(job_id: str):
    """
    Download trained model as .pkl file.

    Args:
        job_id: Training job UUID

    Returns:
        Model file download
    """
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")

    job = training_jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Training not completed")

    model_path = job["result"]["model_path"]

    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="Model file not found")

    model_name = job["config"]["model_name"].replace(" ", "_")
    filename = f"{model_name}_{job_id[:8]}.pkl"

    return FileResponse(
        model_path,
        media_type="application/octet-stream",
        filename=filename
    )


async def run_training_background(
    job_id: str,
    train_path: str,
    test_path: str,
    prediction_sample_path: Optional[str],
    model_name: str,
    target_column: str,
    algorithm: str,
    project_id: str
):
    """
    Background task for running training.

    Args:
        job_id: Training job UUID
        train_path: Path to training CSV
        test_path: Path to test CSV
        prediction_sample_path: Optional path to prediction sample CSV
        model_name: Model name
        target_column: Target column name
        algorithm: Algorithm to use
        project_id: Project UUID
    """
    try:
        # Update status to running
        training_jobs[job_id]["status"] = "running"
        training_jobs[job_id]["stage"] = "loading data"
        training_jobs[job_id]["progress"] = 5

        # Load data
        train_df = pd.read_csv(train_path)
        test_df = pd.read_csv(test_path)

        # If prediction sample provided, only use common features
        if prediction_sample_path:
            prediction_sample_df = pd.read_csv(prediction_sample_path)

            # Find common columns (excluding target column)
            # Only use features that will be available in prediction data
            train_cols = set(train_df.columns) - {target_column}
            test_cols = set(test_df.columns) - {target_column}
            pred_cols = set(prediction_sample_df.columns) - {target_column}

            # Common columns across all three datasets
            common_cols = list(train_cols & test_cols & pred_cols)

            if not common_cols:
                raise ValueError("No common columns found across training, test, and prediction samples")

            # Filter datasets to only use common columns + target
            train_df = train_df[common_cols + [target_column]]
            test_df = test_df[common_cols + [target_column]]

            print(f"Using {len(common_cols)} common features for training (fixture-compatible mode)")
        else:
            print(f"Using all {len(train_df.columns) - 1} features for training (full accuracy mode)")

        # Progress callback
        def update_progress(progress: int, stage: str):
            training_jobs[job_id]["progress"] = progress
            training_jobs[job_id]["stage"] = stage
            save_training_jobs(training_jobs)

        # Train model
        result = train_model_with_algorithm(
            train_df,
            test_df,
            target_column,
            algorithm,
            job_id,
            update_progress
        )

        # Check if training succeeded
        if not result.get('success', False):
            training_jobs[job_id]["status"] = "failed"
            training_jobs[job_id]["error"] = result.get('error', 'Unknown error')
            save_training_jobs(training_jobs)
            return

        # Upload model to MinIO (optional, can fail gracefully)
        minio_path = None
        download_url = None

        try:
            minio_client = get_minio_client()
            minio_path = minio_client.upload_model(
                result["model_path"],
                project_id,
                job_id
            )
            download_url = minio_client.get_download_url(minio_path, expires_hours=24)
        except Exception as minio_error:
            print(f"MinIO upload failed (non-fatal): {minio_error}")
            # Continue without MinIO - model still available locally

        # Update job with results
        training_jobs[job_id]["status"] = "completed"
        training_jobs[job_id]["progress"] = 100
        training_jobs[job_id]["stage"] = "complete"
        training_jobs[job_id]["result"] = {
            "algorithm": result["algorithm"],
            "problem_type": result["problem_type"],
            "model_path": result["model_path"],
            "minio_path": minio_path,
            "download_url": download_url,
            "metrics": result["metrics"],
            "training_samples": result["training_samples"],
            "test_samples": result["test_samples"],
            "feature_count": result["feature_count"]
        }
        training_jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
        save_training_jobs(training_jobs)

    except Exception as e:
        # Handle unexpected errors
        training_jobs[job_id]["status"] = "failed"
        training_jobs[job_id]["error"] = str(e)
        training_jobs[job_id]["logs"] = traceback.format_exc()
        save_training_jobs(training_jobs)
        print(f"Training job {job_id} failed: {e}")
        print(traceback.format_exc())


@router.get("/jobs")
async def list_training_jobs():
    """List all training jobs (for debugging)."""
    return {
        "jobs": list(training_jobs.values()),
        "count": len(training_jobs)
    }


@router.delete("/jobs/{job_id}")
async def delete_training_job(job_id: str):
    """Delete a training job and clean up files."""
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")

    # Clean up temp directory
    temp_dir = f"/tmp/training_jobs/{job_id}"
    if os.path.exists(temp_dir):
        import shutil
        shutil.rmtree(temp_dir)

    # Remove from tracking
    del training_jobs[job_id]
    save_training_jobs(training_jobs)

    return {"message": "Training job deleted", "job_id": job_id}
