"""
Configuration management for Content Ops
Handles environment variables and settings
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv


def get_config() -> Dict[str, Any]:
    """Load and return configuration from environment variables"""
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    config = {
        # Database configuration
        'MYSQL_HOST': os.getenv('MYSQL_HOST', 'mysql'),
        'MYSQL_DATABASE': os.getenv('MYSQL_DATABASE', 'content_ops'),
        'MYSQL_USER': os.getenv('MYSQL_USER', 'content_user'),
        'MYSQL_PASSWORD': os.getenv('MYSQL_PASSWORD', ''),
        
        # Redis configuration
        'REDIS_HOST': os.getenv('REDIS_HOST', 'redis'),
        'REDIS_PASSWORD': os.getenv('REDIS_PASSWORD', ''),
        'REDIS_PORT': int(os.getenv('REDIS_PORT', 6379)),
        
        # Cloudflare R2 configuration
        'R2_ACCOUNT_ID': os.getenv('R2_ACCOUNT_ID', ''),
        'R2_ACCESS_KEY_ID': os.getenv('R2_ACCESS_KEY_ID', ''),
        'R2_SECRET_ACCESS_KEY': os.getenv('R2_SECRET_ACCESS_KEY', ''),
        'R2_BUCKET_NAME': os.getenv('R2_BUCKET_NAME', 'content-ops-backups'),
        'R2_ENDPOINT': os.getenv('R2_ENDPOINT', ''),
        
        # WordPress sites configuration
        'SITE1_DOMAIN': os.getenv('SITE1_DOMAIN', 'site1.localhost'),
        'SITE2_DOMAIN': os.getenv('SITE2_DOMAIN', 'site2.localhost'),
        
        # Backup configuration
        'BACKUP_RETENTION_DAYS': int(os.getenv('BACKUP_RETENTION_DAYS', 30)),
        
        # Timezone
        'TZ': os.getenv('TZ', 'UTC'),
    }
    
    # Validate required configuration
    required_keys = [
        'MYSQL_PASSWORD',
        'REDIS_PASSWORD',
        'R2_ACCESS_KEY_ID',
        'R2_SECRET_ACCESS_KEY',
        'R2_ENDPOINT'
    ]
    
    missing_keys = [key for key in required_keys if not config.get(key)]
    if missing_keys:
        raise ValueError(f"Missing required configuration: {', '.join(missing_keys)}")
    
    return config