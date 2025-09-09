# Content Ops

**Content Ops** is a unified workspace for managing all of Richard Comeau’s digital ventures—combining headless WordPress, static frontends, robust backup workflows, and automation/scheduling via Python. The architecture is built for easy orchestration, collaboration, and adaptability.

***

## Directory Structure Example

```plaintext
/my-headless-wordpress-projects/
│
├── personal-blog/
│    ├── wordpress/              # Docker configs, plugins, custom code, DB exports
│    └── rss-history/            # Dated RSS/XML snapshots, content archives
│         ├── 2025-09-01.xml
│         ├── 2025-09-08.xml
│         └── latest.xml         # Always contains newest feed for sync
│
├── fort-d-aeronautics/
│    ├── wordpress/
│    └── rss-history/
│
├── st-pauls-tentmakers/
│    ├── wordpress/
│    └── rss-history/
│
├── devshop/
│    ├── wordpress/
│    └── rss-history/
│
├── python-cron-jobs/
│    ├── backup_to_r2.py         # Example: scheduled R2 backup script
│    ├── update_feeds.py         # Example: scheduled RSS/feed tasks
│    ├── pyproject.toml          # Poetry dependency file
│    └── ...                     # More scripts, configs
│
└── shared-scripts-templates/
     ├── docker-compose-templates/ # Compose files for multi-project orchestration
     └── helpers/                  # Reusable Python/Bash/PowerShell utilities
```

***

## Organizations & Projects

### Person Blog
My personal, headless WordPress blog. Contains:
- Custom plugins and theme code.
- Dated RSS feed archives for robust content versioning.
- Optional static site-generated frontend (Next.js/Hugo) for blazing-fast publishing.

### Fort D Aeronautics
Home for my drone business and aviation-focused content.
- WordPress as the CMS backend; RSS history for archiving.
- Separate static frontend for marketing and updates.
- Automation scripts for backups and key business workflows.

### St Paul's Tentmakers
A project for ministry and outreach initiatives.
- WordPress for content management, with thorough content archiving and feeds.
- Static site generator for public-facing portal.
- Custom scripts for recurring updates or newsletters.

### Dev Shop
Workspace for my consulting/dev shop.
- WordPress with modern plugin and theme workflows.
- RSS/content archiving for business marketing and posts.
- Next.js or similar frontend for modern web presence.
- Place for technical automations/scripts.

### python-cron-jobs
All project automation—Python scripts managed with Poetry and triggered by scheduled jobs (cron, systemd, or container entrypoints).  
- Tasks: Backups to Cloudflare R2, feed aggregation, sync jobs, status checks, and more.
- Fully automated, tested, and maintained in repo.

### shared-scripts-templates
Reusable tools for infrastructure and automation.
- **docker-compose-templates/**: Templates for starting new project environments and orchestrating your whole stack.
- **helpers/**: Utility scripts, shared Bash/PowerShell/Python helpers for content, backup, or workflow reuse.

***

## Purpose

Centralize and automate digital management for all your ventures under one easy-to-scale, collaborative, and cloud-integrated project.

***

## Why This Approach?

- **Separation:** With clear directories, each brand and org remains modular and easy to maintain.
- **Automation:** All jobs and cron scripts are versioned and reproducible, supporting hands-off maintenance.
- **Backup-Friendly:** RSS and database exports ensure nothing is lost.
- **Cloud Ready:** Integration with R2 for S3-like storage keeps backups safe and migration simple.
- **Collaboration:** Repo is discussion-ready and documentation-focused for public and private partners.
- **Personal Branding:** Unified under one owner; clear provenance and control.
