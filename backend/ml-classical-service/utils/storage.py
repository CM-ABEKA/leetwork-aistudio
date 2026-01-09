"""
MinIO storage utility for uploading/downloading models and datasets.
"""

from minio import Minio
from minio.error import S3Error
import os
from datetime import timedelta
from typing import Optional


class MinIOClient:
    """Client for interacting with MinIO object storage."""

    def __init__(self):
        """Initialize MinIO client with environment variables."""
        self.endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
        self.secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
        self.secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
        self.bucket = os.getenv("MINIO_BUCKET", "ml-platform")

        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure
        )

        self._ensure_bucket()

    def _ensure_bucket(self):
        """Create bucket if it doesn't exist."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
                print(f"Created bucket: {self.bucket}")
        except S3Error as e:
            print(f"Error ensuring bucket exists: {e}")

    def upload_model(self, local_path: str, project_id: str, model_id: str) -> str:
        """
        Upload model file to MinIO.

        Args:
            local_path: Path to local model file
            project_id: Project UUID
            model_id: Model UUID (usually job_id)

        Returns:
            MinIO object path
        """
        object_name = f"models/{project_id}/{model_id}/model.pkl"

        try:
            self.client.fput_object(
                self.bucket,
                object_name,
                local_path
            )
            print(f"Uploaded model to: {object_name}")
            return object_name
        except S3Error as e:
            print(f"Error uploading model: {e}")
            raise

    def get_download_url(self, object_path: str, expires_hours: int = 24) -> str:
        """
        Get presigned download URL for an object.

        Args:
            object_path: Path to object in MinIO
            expires_hours: URL expiration time in hours

        Returns:
            Presigned URL string
        """
        try:
            url = self.client.presigned_get_object(
                self.bucket,
                object_path,
                expires=timedelta(hours=expires_hours)
            )
            return url
        except S3Error as e:
            print(f"Error generating presigned URL: {e}")
            raise

    def download_model(self, object_path: str, local_path: str):
        """
        Download model from MinIO to local path.

        Args:
            object_path: Path to object in MinIO
            local_path: Local path to save to
        """
        try:
            self.client.fget_object(
                self.bucket,
                object_path,
                local_path
            )
            print(f"Downloaded model from: {object_path}")
        except S3Error as e:
            print(f"Error downloading model: {e}")
            raise

    def delete_model(self, object_path: str):
        """Delete model from MinIO."""
        try:
            self.client.remove_object(self.bucket, object_path)
            print(f"Deleted: {object_path}")
        except S3Error as e:
            print(f"Error deleting model: {e}")
            raise


# Singleton instance
_minio_client = None


def get_minio_client() -> MinIOClient:
    """Get or create MinIO client instance."""
    global _minio_client
    if _minio_client is None:
        _minio_client = MinIOClient()
    return _minio_client
