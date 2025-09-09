"""
Content synchronization functionality for Content Ops
Handles content updates and synchronization between WordPress sites
"""

import os
import logging
import requests
import mysql.connector
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .config import get_config


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/content_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ContentSync:
    """Handles content synchronization between WordPress sites"""
    
    def __init__(self):
        self.config = get_config()
        self.db_connection = None
    
    def _get_db_connection(self):
        """Get database connection"""
        if not self.db_connection:
            try:
                self.db_connection = mysql.connector.connect(
                    host=self.config['MYSQL_HOST'],
                    database=self.config['MYSQL_DATABASE'],
                    user=self.config['MYSQL_USER'],
                    password=self.config['MYSQL_PASSWORD']
                )
                logger.info("Database connection established")
            except mysql.connector.Error as e:
                logger.error(f"Error connecting to database: {e}")
                raise
        
        return self.db_connection
    
    def get_recent_posts(self, site_prefix: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get posts updated in the last N hours for a specific site"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Calculate cutoff time
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            query = f"""
                SELECT ID, post_title, post_content, post_excerpt, post_status,
                       post_modified, post_type, guid
                FROM {site_prefix}posts 
                WHERE post_modified >= %s 
                AND post_status = 'publish'
                AND post_type IN ('post', 'page')
                ORDER BY post_modified DESC
            """
            
            cursor.execute(query, (cutoff_time,))
            posts = cursor.fetchall()
            
            logger.info(f"Found {len(posts)} recent posts for {site_prefix}")
            return posts
            
        except mysql.connector.Error as e:
            logger.error(f"Error fetching recent posts: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def sync_featured_content(self, source_site: str, target_site: str) -> bool:
        """Sync featured content between sites"""
        try:
            # Get recent posts from source site
            source_posts = self.get_recent_posts(f"{source_site}_", hours=24)
            
            if not source_posts:
                logger.info(f"No recent posts found in {source_site}")
                return True
            
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            synced_count = 0
            
            for post in source_posts:
                # Check if post already exists in target site
                check_query = f"""
                    SELECT ID FROM {target_site}_posts 
                    WHERE post_title = %s AND post_type = 'featured_content'
                """
                
                cursor.execute(check_query, (post['post_title'],))
                existing_post = cursor.fetchone()
                
                if not existing_post:
                    # Insert as featured content in target site
                    insert_query = f"""
                        INSERT INTO {target_site}_posts 
                        (post_author, post_date, post_date_gmt, post_content, 
                         post_title, post_excerpt, post_status, post_type, 
                         post_modified, post_modified_gmt, guid)
                        VALUES (1, NOW(), UTC_TIMESTAMP(), %s, %s, %s, 
                               'publish', 'featured_content', NOW(), UTC_TIMESTAMP(), %s)
                    """
                    
                    cursor.execute(insert_query, (
                        post['post_content'],
                        f"[Featured] {post['post_title']}",
                        post['post_excerpt'],
                        f"featured-{post['ID']}-{target_site}"
                    ))
                    
                    synced_count += 1
                    logger.info(f"Synced post: {post['post_title']}")
            
            conn.commit()
            logger.info(f"Synced {synced_count} posts from {source_site} to {target_site}")
            return True
            
        except mysql.connector.Error as e:
            logger.error(f"Error syncing content: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
    
    def update_cross_site_links(self, site1_prefix: str, site2_prefix: str) -> bool:
        """Update cross-site links in content"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Update links from site1 to site2
            site1_domain = self.config['SITE1_DOMAIN']
            site2_domain = self.config['SITE2_DOMAIN']
            
            # Update site1 posts to link to site2
            update_query1 = f"""
                UPDATE {site1_prefix}posts 
                SET post_content = REPLACE(post_content, 'CROSS_LINK_SITE2', 'http://{site2_domain}')
                WHERE post_content LIKE '%CROSS_LINK_SITE2%'
            """
            
            # Update site2 posts to link to site1
            update_query2 = f"""
                UPDATE {site2_prefix}posts 
                SET post_content = REPLACE(post_content, 'CROSS_LINK_SITE1', 'http://{site1_domain}')
                WHERE post_content LIKE '%CROSS_LINK_SITE1%'
            """
            
            cursor.execute(update_query1)
            affected1 = cursor.rowcount
            
            cursor.execute(update_query2)
            affected2 = cursor.rowcount
            
            conn.commit()
            
            logger.info(f"Updated cross-site links: {affected1 + affected2} posts affected")
            return True
            
        except mysql.connector.Error as e:
            logger.error(f"Error updating cross-site links: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
    
    def sync_user_data(self, source_site: str, target_site: str) -> bool:
        """Sync user registration data between sites"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Get users from source site (registered in last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            query = f"""
                SELECT user_login, user_email, user_registered, display_name
                FROM {source_site}_users 
                WHERE user_registered >= %s
            """
            
            cursor.execute(query, (cutoff_time,))
            new_users = cursor.fetchall()
            
            synced_count = 0
            
            for user in new_users:
                # Check if user already exists in target site
                check_query = f"""
                    SELECT ID FROM {target_site}_users 
                    WHERE user_email = %s
                """
                
                cursor.execute(check_query, (user['user_email'],))
                existing_user = cursor.fetchone()
                
                if not existing_user:
                    # Insert user into target site
                    insert_query = f"""
                        INSERT INTO {target_site}_users 
                        (user_login, user_email, user_registered, display_name, user_status)
                        VALUES (%s, %s, %s, %s, 0)
                    """
                    
                    cursor.execute(insert_query, (
                        user['user_login'],
                        user['user_email'],
                        user['user_registered'],
                        user['display_name']
                    ))
                    
                    synced_count += 1
                    logger.info(f"Synced user: {user['user_email']}")
            
            conn.commit()
            logger.info(f"Synced {synced_count} users from {source_site} to {target_site}")
            return True
            
        except mysql.connector.Error as e:
            logger.error(f"Error syncing user data: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
    
    def cleanup_old_revisions(self, site_prefix: str, days: int = 30) -> bool:
        """Clean up old post revisions to optimize database"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Delete old revisions
            delete_query = f"""
                DELETE FROM {site_prefix}posts 
                WHERE post_type = 'revision' 
                AND post_modified < %s
            """
            
            cursor.execute(delete_query, (cutoff_date,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            
            logger.info(f"Deleted {deleted_count} old revisions from {site_prefix}")
            return True
            
        except mysql.connector.Error as e:
            logger.error(f"Error cleaning up revisions: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
    
    def run_full_sync(self) -> bool:
        """Run complete content synchronization process"""
        try:
            logger.info("Starting full content synchronization")
            
            # Sync featured content between sites
            self.sync_featured_content('site1', 'site2')
            self.sync_featured_content('site2', 'site1')
            
            # Update cross-site links
            self.update_cross_site_links('site1', 'site2')
            
            # Sync user data
            self.sync_user_data('site1', 'site2')
            self.sync_user_data('site2', 'site1')
            
            # Cleanup old revisions
            self.cleanup_old_revisions('site1')
            self.cleanup_old_revisions('site2')
            
            logger.info("Full content synchronization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error in full sync process: {e}")
            return False
        finally:
            if self.db_connection:
                self.db_connection.close()
                self.db_connection = None


def main():
    """CLI entry point for content synchronization"""
    import click
    
    @click.group()
    def cli():
        """Content synchronization operations"""
        pass
    
    @cli.command()
    def full_sync():
        """Run complete content synchronization"""
        sync = ContentSync()
        success = sync.run_full_sync()
        if success:
            click.echo("✓ Full synchronization completed successfully")
        else:
            click.echo("✗ Synchronization failed")
    
    @cli.command()
    @click.argument('source_site')
    @click.argument('target_site')
    def sync_featured(source_site, target_site):
        """Sync featured content between specific sites"""
        sync = ContentSync()
        success = sync.sync_featured_content(source_site, target_site)
        if success:
            click.echo(f"✓ Featured content synced from {source_site} to {target_site}")
        else:
            click.echo("✗ Featured content sync failed")
    
    @cli.command()
    @click.argument('site_prefix')
    @click.option('--days', default=30, help='Days to retain revisions')
    def cleanup_revisions(site_prefix, days):
        """Clean up old post revisions"""
        sync = ContentSync()
        success = sync.cleanup_old_revisions(site_prefix, days)
        if success:
            click.echo(f"✓ Cleaned up revisions older than {days} days")
        else:
            click.echo("✗ Revision cleanup failed")
    
    cli()


if __name__ == "__main__":
    main()