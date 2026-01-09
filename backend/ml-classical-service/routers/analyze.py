from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict, Any
import pandas as pd
import io
import json
from pydantic import BaseModel

from core.data_analysis import analyze_dataset
from core.data_cleaning import clean_dataset
from core.data_splitting import split_dataset

router = APIRouter()


class CleaningOperation(BaseModel):
    type: str
    strategy: str | None = None
    columns: List[str] | None = None
    method: str | None = None
    subset: List[str] | None = None
    type_map: Dict[str, str] | None = None


class CleaningRequest(BaseModel):
    operations: List[CleaningOperation]


class SplitRequest(BaseModel):
    train_ratio: float = 0.8
    strategy: str = "random"
    random_seed: int = 42
    target_column: str | None = None


@router.get("/")
def analyze_info():
    return {
        "service": "Data Analysis API",
        "endpoints": {
            "POST /dataset": "Upload and analyze a CSV dataset",
            "POST /clean": "Apply cleaning operations to dataset"
        },
        "status": "active",
    }


@router.post("/dataset")
async def analyze_uploaded_dataset(file: UploadFile = File(...)):
    """
    Upload and analyze a dataset

    Accepts CSV files and returns analysis results including:
    - Dataset shape
    - Column information
    - Detected issues (missing values, duplicates, outliers, etc.)
    - Summary statistics
    """
    try:
        # Check file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are supported currently"
            )

        # Read the CSV file
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        # Analyze the dataset
        analysis_results = analyze_dataset(df)

        # Add file metadata
        analysis_results["file_info"] = {
            "filename": file.filename,
            "size_bytes": len(contents),
            "content_type": file.content_type
        }

        # Return as dict (FastAPI will handle JSON serialization)
        return analysis_results

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="The uploaded file is empty")
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Error parsing CSV: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing dataset: {str(e)}")


@router.post("/clean")
async def clean_uploaded_dataset(
    file: UploadFile = File(...),
    cleaning_request: str | None = None
):
    """
    Upload a dataset and apply cleaning operations

    Returns the cleaned dataset as CSV
    """
    try:
        # Check file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are supported currently"
            )

        # Read the CSV file
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        # Apply default cleaning operations if none provided
        operations = []
        if cleaning_request:
            import json
            request_data = json.loads(cleaning_request)
            operations = request_data.get("operations", [])
        else:
            # Default cleaning: remove duplicates and handle missing values
            operations = [
                {"type": "remove_duplicates"},
                {"type": "handle_missing", "strategy": "median"},
            ]

        # Clean the dataset
        df_clean = clean_dataset(df, operations)

        # Convert back to CSV
        output = io.StringIO()
        df_clean.to_csv(output, index=False)
        csv_data = output.getvalue()

        return {
            "success": True,
            "original_shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
            "cleaned_shape": {"rows": int(df_clean.shape[0]), "columns": int(df_clean.shape[1])},
            "operations_applied": len(operations),
            "csv_data": csv_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning dataset: {str(e)}")


@router.post("/split")
async def split_uploaded_dataset(
    file: UploadFile = File(...),
    split_request: str | None = None
):
    """
    Upload a dataset and split into train/test sets

    Returns both datasets as CSV strings with metadata
    """
    try:
        # Check file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are supported currently"
            )

        # Read the CSV file
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        # Parse split request
        split_config = {}
        if split_request:
            request_data = json.loads(split_request)
            split_config = {
                "train_ratio": request_data.get("train_ratio", 0.8),
                "strategy": request_data.get("strategy", "random"),
                "random_seed": request_data.get("random_seed", 42),
                "target_column": request_data.get("target_column")
            }
        else:
            # Default split configuration
            split_config = {
                "train_ratio": 0.8,
                "strategy": "random",
                "random_seed": 42,
                "target_column": None
            }

        # Perform the split
        result = split_dataset(df, **split_config)

        # Convert DataFrames to CSV strings
        train_output = io.StringIO()
        result["train_df"].to_csv(train_output, index=False)
        train_csv = train_output.getvalue()

        test_output = io.StringIO()
        result["test_df"].to_csv(test_output, index=False)
        test_csv = test_output.getvalue()

        return {
            "success": True,
            "train_csv": train_csv,
            "test_csv": test_csv,
            "train_shape": result["train_shape"],
            "test_shape": result["test_shape"],
            "split_config": result["split_config"]
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error splitting dataset: {str(e)}")


@router.get("/preview")
def get_preview_info():
    """Get information about the preview endpoint"""
    return {
        "message": "Use POST /dataset to analyze a file and get a preview",
        "supported_formats": ["csv"]
    }
