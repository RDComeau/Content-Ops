#!/usr/bin/env python3
"""
Manual backup script for Content Ops
Usage: python backup_now.py [--upload] [--tables table1,table2]
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from content_ops.backup import DatabaseBackup


def main():
    parser = argparse.ArgumentParser(description='Manual database backup')
    parser.add_argument('--upload', action='store_true', help='Upload backup to R2')
    parser.add_argument('--tables', help='Comma-separated list of tables to backup')
    parser.add_argument('--cleanup', action='store_true', help='Cleanup old backups')
    
    args = parser.parse_args()
    
    backup = DatabaseBackup()
    
    # Parse tables if provided
    tables = None
    if args.tables:
        tables = [t.strip() for t in args.tables.split(',')]
    
    # Create backup
    print("Creating database backup...")
    backup_path = backup.create_backup(tables)
    
    if not backup_path:
        print("❌ Backup failed!")
        sys.exit(1)
    
    print(f"✅ Backup created: {backup_path}")
    
    # Upload if requested
    if args.upload:
        print("Uploading to R2 storage...")
        success = backup.upload_backup(backup_path)
        if success:
            print("✅ Backup uploaded successfully")
        else:
            print("❌ Upload failed!")
            sys.exit(1)
    
    # Cleanup if requested
    if args.cleanup:
        print("Cleaning up old backups...")
        backup.cleanup_old_backups()
        print("✅ Cleanup completed")
    
    print("🎉 Backup process completed successfully!")


if __name__ == "__main__":
    main()