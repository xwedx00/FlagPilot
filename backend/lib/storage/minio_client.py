"""
MinIO Storage Client for FlagPilot v7.0
=======================================
S3-compatible file storage for contracts, documents, and uploads.
"""

from typing import Optional, BinaryIO, Dict, Any
from io import BytesIO
import uuid
from datetime import datetime, timedelta
from loguru import logger
from minio import Minio
from minio.error import S3Error

from config import settings


class MinIOStorage:
    """Production MinIO client for file operations"""
    
    _instance: Optional["MinIOStorage"] = None
    _client: Optional[Minio] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is not None:
            return
        self._initialize()
    
    def _initialize(self):
        """Initialize MinIO client and ensure bucket exists"""
        try:
            self._client = Minio(
                endpoint=settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=settings.minio_secure,
            )
            logger.info(f"Connected to MinIO at {settings.minio_endpoint}")
            
            # Ensure bucket exists
            self._ensure_bucket()
            
        except Exception as e:
            logger.error(f"MinIO initialization failed: {e}")
            raise
    
    def _ensure_bucket(self):
        """Create bucket if it doesn't exist"""
        try:
            if not self._client.bucket_exists(settings.minio_bucket):
                self._client.make_bucket(settings.minio_bucket)
                logger.info(f"Created MinIO bucket: {settings.minio_bucket}")
            else:
                logger.debug(f"MinIO bucket '{settings.minio_bucket}' exists")
        except S3Error as e:
            logger.error(f"Failed to ensure bucket: {e}")
            raise
    
    @property
    def client(self) -> Minio:
        """Get raw MinIO client"""
        return self._client
    
    def upload_file(
        self,
        file_data: BinaryIO,
        file_name: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a file to MinIO.
        
        Args:
            file_data: File-like object or bytes
            file_name: Original filename
            content_type: MIME type
            metadata: Optional metadata dict
            user_id: Optional user ID for organizing
            
        Returns:
            Dict with object_name, bucket, etag, size, url
        """
        try:
            # Generate unique object name
            ext = file_name.rsplit(".", 1)[-1] if "." in file_name else ""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = uuid.uuid4().hex[:8]
            
            if user_id:
                object_name = f"{user_id}/{timestamp}_{unique_id}.{ext}"
            else:
                object_name = f"uploads/{timestamp}_{unique_id}.{ext}"
            
            # Get file size
            file_data.seek(0, 2)
            file_size = file_data.tell()
            file_data.seek(0)
            
            # Upload
            result = self._client.put_object(
                bucket_name=settings.minio_bucket,
                object_name=object_name,
                data=file_data,
                length=file_size,
                content_type=content_type,
                metadata=metadata or {},
            )
            
            logger.info(f"Uploaded file: {object_name} ({file_size} bytes)")
            
            return {
                "object_name": object_name,
                "bucket": settings.minio_bucket,
                "etag": result.etag,
                "size": file_size,
                "original_name": file_name,
                "content_type": content_type,
            }
            
        except S3Error as e:
            logger.error(f"Upload failed: {e}")
            raise
    
    def upload_bytes(
        self,
        data: bytes,
        file_name: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload bytes data to MinIO"""
        return self.upload_file(
            file_data=BytesIO(data),
            file_name=file_name,
            content_type=content_type,
            metadata=metadata,
            user_id=user_id,
        )
    
    def download_file(self, object_name: str) -> bytes:
        """Download a file from MinIO"""
        try:
            response = self._client.get_object(
                bucket_name=settings.minio_bucket,
                object_name=object_name,
            )
            data = response.read()
            response.close()
            response.release_conn()
            logger.debug(f"Downloaded file: {object_name}")
            return data
        except S3Error as e:
            logger.error(f"Download failed: {e}")
            raise
    
    def get_presigned_url(
        self,
        object_name: str,
        expires: int = 3600,
    ) -> str:
        """Get a presigned URL for file access"""
        try:
            url = self._client.presigned_get_object(
                bucket_name=settings.minio_bucket,
                object_name=object_name,
                expires=timedelta(seconds=expires),
            )
            return url
        except S3Error as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise
    
    def delete_file(self, object_name: str) -> bool:
        """Delete a file from MinIO"""
        try:
            self._client.remove_object(
                bucket_name=settings.minio_bucket,
                object_name=object_name,
            )
            logger.info(f"Deleted file: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"Delete failed: {e}")
            return False
    
    def list_files(
        self,
        prefix: str = "",
        recursive: bool = True,
    ) -> list:
        """List files in bucket"""
        try:
            objects = self._client.list_objects(
                bucket_name=settings.minio_bucket,
                prefix=prefix,
                recursive=recursive,
            )
            return [
                {
                    "name": obj.object_name,
                    "size": obj.size,
                    "modified": obj.last_modified,
                }
                for obj in objects
            ]
        except S3Error as e:
            logger.error(f"List failed: {e}")
            return []
    
    def file_exists(self, object_name: str) -> bool:
        """Check if file exists"""
        try:
            self._client.stat_object(
                bucket_name=settings.minio_bucket,
                object_name=object_name,
            )
            return True
        except S3Error:
            return False


# Singleton accessor
def get_minio_storage() -> MinIOStorage:
    """Get or create MinIOStorage singleton"""
    return MinIOStorage()
