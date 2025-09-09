"""
Database backup functionality for Content Ops
Handles MySQL database backups and uploads to Cloudflare R2
"""

import os
import datetime
import subprocess
import logging
import click
from pathlib import Path
from typing import Optional

from .r2_storage import R2Storage
from .config import get_config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DatabaseBackup:
    """Handles database backup operations"""
    
    def __init__(self):
        self.config = get_config()
        self.backup_dir = Path("/app/backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.r2_storage = R2Storage()
    
    def create_backup(self, tables: Optional[list] = None) -> str:
        """Create a MySQL database backup"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"content_ops_backup_{timestamp}.sql"
        backup_path = self.backup_dir / backup_filename
        
        # Build mysqldump command
        cmd = [
            "mysqldump",
            "-h", self.config["MYSQL_HOST"],
            "-u", self.config["MYSQL_USER"],
            f"-p{self.config['MYSQL_PASSWORD']}",
            "--single-transaction",
            "--routines",
            "--triggers",
            self.config["MYSQL_DATABASE"]
        ]
        
        # Add specific tables if provided
        if tables:
            cmd.extend(tables)
        
        try:
            logger.info(f"Creating database backup: {backup_filename}")
            
            with open(backup_path, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                logger.error(f"Backup failed: {result.stderr}")
                return None
            
            logger.info(f"Backup created successfully: {backup_path}")
            return str(backup_path)
            
        except subprocess.SubprocessError as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    def upload_backup(self, backup_path: str) -> bool:
        """Upload backup to Cloudflare R2"""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Upload to R2
            r2_key = f"backups/{backup_file.name}"
            success = self.r2_storage.upload_file(str(backup_file), r2_key)
            
            if success:
                logger.info(f"Backup uploaded to R2: {r2_key}")
                return True
            else:
                logger.error("Failed to upload backup to R2")
                return False
                
        except Exception as e:
            logger.error(f"Error uploading backup: {e}")
            return False
    
    def cleanup_old_backups(self, retention_days: int = 30):
        """Remove local backups older than retention_days"""
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)
            
            for backup_file in self.backup_dir.glob("*.sql"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    logger.info(f"Deleted old backup: {backup_file.name}")
                    
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
    
    def full_backup_process(self) -> bool:
        """Complete backup process: create, upload, cleanup"""
        try:
            # Create backup
            backup_path = self.create_backup()
            if not backup_path:
                return False
            
            # Upload to R2
            upload_success = self.upload_backup(backup_path)
            
            # Cleanup old backups
            retention_days = int(self.config.get("BACKUP_RETENTION_DAYS", 30))
            self.cleanup_old_backups(retention_days)
            
            return upload_success
            
        except Exception as e:
            logger.error(f"Error in full backup process: {e}")
            return False


@click.command()
@click.option('--tables', '-t', multiple=True, help='Specific tables to backup')
@click.option('--upload/--no-upload', default=True, help='Upload to R2 storage')
@click.option('--cleanup/--no-cleanup', default=True, help='Cleanup old backups')
def main(tables, upload, cleanup):
    """Run database backup process"""
    backup = DatabaseBackup()
    
    if tables:
        backup_path = backup.create_backup(list(tables))
    else:
        backup_path = backup.create_backup()
    
    if backup_path and upload:
        backup.upload_backup(backup_path)
    
    if cleanup:
        backup.cleanup_old_backups()


if __name__ == "__main__":
    main()