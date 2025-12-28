"""
Storage Module for FlagPilot v7.0
=================================
MinIO S3-compatible file storage.
"""

from lib.storage.minio_client import MinIOStorage, get_minio_storage

__all__ = ["MinIOStorage", "get_minio_storage"]
