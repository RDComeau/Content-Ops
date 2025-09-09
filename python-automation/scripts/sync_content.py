#!/usr/bin/env python3
"""
Content synchronization script for Content Ops
Usage: python sync_content.py [--full] [--source site1] [--target site2]
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from content_ops.content_sync import ContentSync


def main():
    parser = argparse.ArgumentParser(description='Content synchronization')
    parser.add_argument('--full', action='store_true', help='Run full synchronization')
    parser.add_argument('--source', help='Source site (site1 or site2)')
    parser.add_argument('--target', help='Target site (site1 or site2)')
    parser.add_argument('--cleanup-revisions', action='store_true', help='Cleanup old revisions')
    parser.add_argument('--days', type=int, default=30, help='Days to retain revisions')
    
    args = parser.parse_args()
    
    sync = ContentSync()
    
    if args.full:
        print("Running full content synchronization...")
        success = sync.run_full_sync()
        if success:
            print("✅ Full synchronization completed successfully")
        else:
            print("❌ Full synchronization failed!")
            sys.exit(1)
    
    elif args.source and args.target:
        print(f"Syncing featured content from {args.source} to {args.target}...")
        success = sync.sync_featured_content(args.source, args.target)
        if success:
            print("✅ Featured content synchronized successfully")
        else:
            print("❌ Featured content synchronization failed!")
            sys.exit(1)
    
    elif args.cleanup_revisions:
        print("Cleaning up old revisions...")
        success1 = sync.cleanup_old_revisions('site1_', args.days)
        success2 = sync.cleanup_old_revisions('site2_', args.days)
        
        if success1 and success2:
            print("✅ Revision cleanup completed successfully")
        else:
            print("❌ Revision cleanup failed!")
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)
    
    print("🎉 Content synchronization completed!")


if __name__ == "__main__":
    main()