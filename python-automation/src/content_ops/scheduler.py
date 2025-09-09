"""
Scheduler for Content Ops automation tasks
Manages scheduled jobs for backups, content sync, and maintenance
"""

import time
import logging
import schedule
from datetime import datetime

from .backup import DatabaseBackup
from .content_sync import ContentSync
from .r2_storage import R2Storage
from .config import get_config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutomationScheduler:
    """Manages scheduled automation tasks"""
    
    def __init__(self):
        self.config = get_config()
        self.backup = DatabaseBackup()
        self.content_sync = ContentSync()
        self.r2_storage = R2Storage()
        
        # Setup scheduled jobs
        self._setup_schedules()
    
    def _setup_schedules(self):
        """Configure scheduled jobs"""
        # Database backup - daily at 2 AM
        schedule.every().day.at("02:00").do(self._run_backup_job)
        
        # Content synchronization - every 6 hours
        schedule.every(6).hours.do(self._run_content_sync_job)
        
        # Cleanup old backups - weekly on Sunday at 3 AM
        schedule.every().sunday.at("03:00").do(self._run_cleanup_job)
        
        # Health check - every hour
        schedule.every().hour.do(self._run_health_check)
        
        logger.info("Scheduled jobs configured successfully")
    
    def _run_backup_job(self):
        """Execute database backup job"""
        try:
            logger.info("Starting scheduled database backup")
            success = self.backup.full_backup_process()
            
            if success:
                logger.info("Scheduled database backup completed successfully")
            else:
                logger.error("Scheduled database backup failed")
            
        except Exception as e:
            logger.error(f"Error in scheduled backup job: {e}")
    
    def _run_content_sync_job(self):
        """Execute content synchronization job"""
        try:
            logger.info("Starting scheduled content synchronization")
            success = self.content_sync.run_full_sync()
            
            if success:
                logger.info("Scheduled content synchronization completed successfully")
            else:
                logger.error("Scheduled content synchronization failed")
            
        except Exception as e:
            logger.error(f"Error in scheduled content sync job: {e}")
    
    def _run_cleanup_job(self):
        """Execute cleanup job for old backups"""
        try:
            logger.info("Starting scheduled cleanup job")
            
            # Cleanup local backups
            retention_days = int(self.config.get("BACKUP_RETENTION_DAYS", 30))
            self.backup.cleanup_old_backups(retention_days)
            
            # Cleanup R2 backups
            self.r2_storage.cleanup_old_backups(prefix="backups/", retention_days=retention_days)
            
            logger.info("Scheduled cleanup job completed successfully")
            
        except Exception as e:
            logger.error(f"Error in scheduled cleanup job: {e}")
    
    def _run_health_check(self):
        """Execute health check for all services"""
        try:
            logger.info("Running health check")
            
            # Check database connection
            db_healthy = self._check_database_health()
            
            # Check R2 connection
            r2_healthy = self._check_r2_health()
            
            # Log health status
            if db_healthy and r2_healthy:
                logger.info("Health check passed - all services healthy")
            else:
                logger.warning(f"Health check issues - DB: {db_healthy}, R2: {r2_healthy}")
            
        except Exception as e:
            logger.error(f"Error in health check: {e}")
    
    def _check_database_health(self) -> bool:
        """Check database connectivity"""
        try:
            conn = self.content_sync._get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def _check_r2_health(self) -> bool:
        """Check R2 storage connectivity"""
        try:
            # Try to list objects (lightweight operation)
            self.r2_storage.list_objects(max_keys=1)
            return True
        except Exception as e:
            logger.error(f"R2 health check failed: {e}")
            return False
    
    def run(self):
        """Start the scheduler"""
        logger.info("Starting automation scheduler")
        
        # Run initial health check
        self._run_health_check()
        
        # Main scheduler loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Continue after error
    
    def run_job_once(self, job_name: str) -> bool:
        """Run a specific job immediately"""
        job_map = {
            'backup': self._run_backup_job,
            'content_sync': self._run_content_sync_job,
            'cleanup': self._run_cleanup_job,
            'health_check': self._run_health_check
        }
        
        if job_name not in job_map:
            logger.error(f"Unknown job: {job_name}")
            return False
        
        try:
            logger.info(f"Running job immediately: {job_name}")
            job_map[job_name]()
            return True
        except Exception as e:
            logger.error(f"Error running job {job_name}: {e}")
            return False


def main():
    """Entry point for the scheduler"""
    import click
    
    @click.group()
    def cli():
        """Content Ops automation scheduler"""
        pass
    
    @cli.command()
    def start():
        """Start the scheduler daemon"""
        scheduler = AutomationScheduler()
        scheduler.run()
    
    @cli.command()
    @click.argument('job_name', type=click.Choice(['backup', 'content_sync', 'cleanup', 'health_check']))
    def run_job(job_name):
        """Run a specific job immediately"""
        scheduler = AutomationScheduler()
        success = scheduler.run_job_once(job_name)
        if success:
            click.echo(f"✓ Job '{job_name}' completed successfully")
        else:
            click.echo(f"✗ Job '{job_name}' failed")
    
    @cli.command()
    def status():
        """Show scheduler status and next run times"""
        click.echo("Scheduled jobs:")
        for job in schedule.jobs:
            click.echo(f"  {job}")
    
    cli()


if __name__ == "__main__":
    main()