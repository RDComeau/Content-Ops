"""
Cloudflare R2 storage integration for Content Ops
Handles file uploads and management with R2 storage
"""

import os
import boto3
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError

from .config import get_config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/r2_storage.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class R2Storage:
    """Cloudflare R2 storage client"""
    
    def __init__(self):
        self.config = get_config()
        self.client = self._initialize_client()
        self.bucket_name = self.config["R2_BUCKET_NAME"]
    
    def _initialize_client(self):
        """Initialize R2 client with credentials"""
        try:
            client = boto3.client(
                's3',
                endpoint_url=self.config["R2_ENDPOINT"],
                aws_access_key_id=self.config["R2_ACCESS_KEY_ID"],
                aws_secret_access_key=self.config["R2_SECRET_ACCESS_KEY"],
                region_name='auto'
            )
            
            # Test connection
            client.head_bucket(Bucket=self.bucket_name)
            logger.info("R2 client initialized successfully")
            return client
            
        except NoCredentialsError:
            logger.error("R2 credentials not found")
            raise
        except ClientError as e:
            logger.error(f"Error initializing R2 client: {e}")
            raise
    
    def upload_file(self, local_path: str, r2_key: str, metadata: Optional[Dict[str, str]] = None) -> bool:
        """Upload a file to R2 storage"""
        try:
            local_file = Path(local_path)
            if not local_file.exists():
                logger.error(f"Local file not found: {local_path}")
                return False
            
            # Prepare upload parameters
            upload_params = {
                'Bucket': self.bucket_name,
                'Key': r2_key,
                'Filename': str(local_file)
            }
            
            # Add metadata if provided
            if metadata:
                upload_params['ExtraArgs'] = {'Metadata': metadata}
            
            # Upload file
            self.client.upload_file(**upload_params)
            logger.info(f"File uploaded successfully: {r2_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Error uploading file {local_path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error uploading file {local_path}: {e}")
            return False
    
    def download_file(self, r2_key: str, local_path: str) -> bool:
        """Download a file from R2 storage"""
        try:
            local_file = Path(local_path)
            local_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.client.download_file(
                Bucket=self.bucket_name,
                Key=r2_key,
                Filename=str(local_file)
            )
            
            logger.info(f"File downloaded successfully: {local_path}")
            return True
            
        except ClientError as e:
            logger.error(f"Error downloading file {r2_key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading file {r2_key}: {e}")
            return False
    
    def list_objects(self, prefix: str = "", max_keys: int = 1000) -> list:
        """List objects in R2 bucket with optional prefix filter"""
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            objects = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    objects.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'etag': obj['ETag']
                    })
            
            logger.info(f"Listed {len(objects)} objects with prefix '{prefix}'")
            return objects
            
        except ClientError as e:
            logger.error(f"Error listing objects: {e}")
            return []
    
    def delete_object(self, r2_key: str) -> bool:
        """Delete an object from R2 storage"""
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=r2_key
            )
            
            logger.info(f"Object deleted successfully: {r2_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Error deleting object {r2_key}: {e}")
            return False
    
    def object_exists(self, r2_key: str) -> bool:
        """Check if an object exists in R2 storage"""
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=r2_key
            )
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(f"Error checking object existence {r2_key}: {e}")
                return False
    
    def get_object_metadata(self, r2_key: str) -> Optional[Dict[str, Any]]:
        """Get metadata for an object in R2 storage"""
        try:
            response = self.client.head_object(
                Bucket=self.bucket_name,
                Key=r2_key
            )
            
            return {
                'content_length': response.get('ContentLength'),
                'content_type': response.get('ContentType'),
                'last_modified': response.get('LastModified'),
                'etag': response.get('ETag'),
                'metadata': response.get('Metadata', {})
            }
            
        except ClientError as e:
            logger.error(f"Error getting object metadata {r2_key}: {e}")
            return None
    
    def cleanup_old_backups(self, prefix: str = "backups/", retention_days: int = 30):
        """Delete backup objects older than retention_days"""
        try:
            import datetime
            cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=retention_days)
            
            objects = self.list_objects(prefix=prefix)
            deleted_count = 0
            
            for obj in objects:
                if obj['last_modified'] < cutoff_date:
                    if self.delete_object(obj['key']):
                        deleted_count += 1
            
            logger.info(f"Deleted {deleted_count} old backup objects")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
            return 0


def main():
    """CLI entry point for R2 storage operations"""
    import click
    
    @click.group()
    def cli():
        """Cloudflare R2 storage operations"""
        pass
    
    @cli.command()
    @click.argument('local_path')
    @click.argument('r2_key')
    def upload(local_path, r2_key):
        """Upload a file to R2 storage"""
        r2 = R2Storage()
        success = r2.upload_file(local_path, r2_key)
        if success:
            click.echo(f"✓ Uploaded {local_path} to {r2_key}")
        else:
            click.echo(f"✗ Failed to upload {local_path}")
    
    @cli.command()
    @click.argument('r2_key')
    @click.argument('local_path')
    def download(r2_key, local_path):
        """Download a file from R2 storage"""
        r2 = R2Storage()
        success = r2.download_file(r2_key, local_path)
        if success:
            click.echo(f"✓ Downloaded {r2_key} to {local_path}")
        else:
            click.echo(f"✗ Failed to download {r2_key}")
    
    @cli.command()
    @click.option('--prefix', default='', help='Object prefix filter')
    def list(prefix):
        """List objects in R2 storage"""
        r2 = R2Storage()
        objects = r2.list_objects(prefix=prefix)
        
        if objects:
            click.echo(f"Objects in bucket (prefix: '{prefix}'):")
            for obj in objects:
                click.echo(f"  {obj['key']} ({obj['size']} bytes)")
        else:
            click.echo("No objects found")
    
    cli()


if __name__ == "__main__":
    main()