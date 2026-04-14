"""
Cloud storage service for managing content assets
Uses AWS S3 with async support via boto3
"""
import boto3
import asyncio
from pathlib import Path
from typing import Optional
from loguru import logger
from src.config import settings
import aiofiles
import io


class StorageService:
    """Manages cloud storage operations"""
    
    def __init__(self):
        self.s3_client = None
        self.bucket_name = settings.S3_BUCKET_NAME
        self._init_s3()
    
    def _init_s3(self):
        """Initialize S3 client"""
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            logger.info(f"S3 client initialized for bucket: {self.bucket_name}")
        else:
            logger.warning("S3 credentials not configured - storage operations will fail")
    
    async def upload_file(self, file_path: str, s3_key: str) -> Optional[str]:
        """Upload file to S3 asynchronously"""
        try:
            if not self.s3_client:
                logger.error("S3 client not initialized")
                return None
            
            # Determine content type
            content_type = self._get_content_type(file_path)
            
            # Read file asynchronously
            async with aiofiles.open(file_path, 'rb') as f:
                file_content = await f.read()
            
            # Upload in thread pool (boto3 is not async)
            await asyncio.to_thread(
                self.s3_client.put_object,
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type
            )
            
            url = f"{settings.S3_BUCKET_URL}/{s3_key}"
            logger.info(f"Uploaded {file_path} to {url}")
            return url
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            return None
    
    async def upload_bytes(self, content: bytes, s3_key: str, 
                          content_type: str = "application/octet-stream") -> Optional[str]:
        """Upload bytes to S3"""
        try:
            if not self.s3_client:
                logger.error("S3 client not initialized")
                return None
            
            await asyncio.to_thread(
                self.s3_client.put_object,
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=content,
                ContentType=content_type
            )
            
            url = f"{settings.S3_BUCKET_URL}/{s3_key}"
            logger.info(f"Uploaded {s3_key} ({len(content)} bytes)")
            return url
        except Exception as e:
            logger.error(f"Failed to upload bytes: {e}")
            return None
    
    async def download_file(self, s3_key: str, output_path: str) -> bool:
        """Download file from S3"""
        try:
            if not self.s3_client:
                logger.error("S3 client not initialized")
                return False
            
            # Download in thread pool
            response = await asyncio.to_thread(
                self.s3_client.get_object,
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            # Write to file asynchronously
            async with aiofiles.open(output_path, 'wb') as f:
                await f.write(response['Body'].read())
            
            logger.info(f"Downloaded {s3_key} to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            return False
    
    async def delete_file(self, s3_key: str) -> bool:
        """Delete file from S3"""
        try:
            if not self.s3_client:
                return False
            
            await asyncio.to_thread(
                self.s3_client.delete_object,
                Bucket=self.bucket_name,
                Key=s3_key
            )
            logger.info(f"Deleted {s3_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False
    
    async def list_files(self, prefix: str = "") -> list:
        """List files in S3 bucket"""
        try:
            if not self.s3_client:
                return []
            
            response = await asyncio.to_thread(
                self.s3_client.list_objects_v2,
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            return [obj['Key'] for obj in response.get('Contents', [])]
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    @staticmethod
    def _get_content_type(file_path: str) -> str:
        """Determine content type from file extension"""
        ext = Path(file_path).suffix.lower()
        content_types = {
            '.mp4': 'video/mp4',
            '.webm': 'video/webm',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.json': 'application/json'
        }
        return content_types.get(ext, 'application/octet-stream')


# Global storage service instance
storage_service = StorageService()
