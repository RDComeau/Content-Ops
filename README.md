# Content Operations - Unified Content Management Platform

A comprehensive Docker-based solution for managing multiple WordPress sites with automated backups, content synchronization, and cloud storage integration.

## 🚀 Features

- **Multi-Site WordPress Management**: Deploy and manage multiple WordPress sites with shared infrastructure
- **Automated Database Backups**: Scheduled backups with Cloudflare R2 storage integration
- **Content Synchronization**: Automated content sync between WordPress sites
- **Redis Caching**: High-performance caching layer for all WordPress sites
- **Nginx Reverse Proxy**: Load balancing and SSL termination
- **Python Automation**: Comprehensive automation scripts with Poetry dependency management
- **Scheduled Jobs**: Cron-based automation for maintenance and content operations
- **Health Monitoring**: Built-in health checks and logging
- **Easy Collaboration**: Docker Compose orchestration for team development

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │────│   WordPress 1   │
│                 │    │                 │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          │            ┌─────────┬───────┐
          │            │   WordPress 2   │
          │            │                 │
          │            └─────────┬───────┘
          │                      │
    ┌─────┴───────┐    ┌─────────┴───────┐
    │    Redis    │    │      MySQL      │
    │   Cache     │    │    Database     │
    └─────────────┘    └─────────────────┘
          │                      │
    ┌─────┴─────────────────────┴───────┐
    │       Python Automation          │
    │   ┌─────────┐ ┌─────────────────┐ │
    │   │ Backups │ │ Content Sync    │ │
    │   └─────────┘ └─────────────────┘ │
    └───────────┬───────────────────────┘
                │
        ┌───────┴────────┐
        │ Cloudflare R2  │
        │    Storage     │
        └────────────────┘
```

## 🛠️ Quick Start

### Prerequisites

- Docker & Docker Compose
- Git
- Poetry (optional, for local Python development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/RDComeau/Content-Ops.git
   cd Content-Ops
   ```

2. **Run the setup script**
   ```bash
   ./setup.sh
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual configuration
   ```

4. **Start the services**
   ```bash
   docker-compose up -d
   ```

5. **Access your sites**
   - Site 1: http://site1.localhost
   - Site 2: http://site2.localhost

## ⚙️ Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Database
MYSQL_ROOT_PASSWORD=your_secure_root_password
MYSQL_DATABASE=content_ops
MYSQL_USER=content_user
MYSQL_PASSWORD=your_secure_password

# WordPress Sites
SITE1_DOMAIN=site1.localhost
SITE2_DOMAIN=site2.localhost

# Cloudflare R2
R2_ACCOUNT_ID=your_cloudflare_account_id
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_key
R2_BUCKET_NAME=content-ops-backups

# Redis
REDIS_PASSWORD=your_redis_password

# Backup Settings
BACKUP_RETENTION_DAYS=30
```

## 🤖 Automation Features

### Scheduled Jobs

- **Database Backups**: Daily at 2 AM with R2 upload
- **Content Sync**: Every 6 hours between sites
- **Cleanup Tasks**: Weekly cleanup of old backups and revisions
- **Health Checks**: Hourly system health monitoring

### Manual Operations

```bash
# Manual backup
python python-automation/scripts/backup_now.py --upload

# Content synchronization
python python-automation/scripts/sync_content.py --full

# Run specific automation job
docker-compose exec automation python -m content_ops.scheduler run-job backup
```

## 📊 Management Commands

### Docker Operations
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild images
docker-compose build

# Scale WordPress instances
docker-compose up -d --scale wordpress-site1=2
```

### Python Automation
```bash
# Enter automation container
docker-compose exec automation bash

# Run backup manually
python -m content_ops.backup

# Run content sync
python -m content_ops.content_sync full-sync

# Check R2 storage
python -m content_ops.r2_storage list --prefix backups/
```

## 🔧 Development

### Local Python Development

1. **Setup Poetry environment**
   ```bash
   cd python-automation
   poetry install
   poetry shell
   ```

2. **Run tests**
   ```bash
   poetry run pytest
   ```

3. **Code formatting**
   ```bash
   poetry run black .
   poetry run flake8
   ```

### Adding New Automation Scripts

1. Create your script in `python-automation/src/content_ops/`
2. Add CLI commands using Click
3. Update `pyproject.toml` with new entry points
4. Add to scheduler if needed

## 📁 Project Structure

```
Content-Ops/
├── docker-compose.yml          # Main orchestration
├── .env.example               # Environment template
├── setup.sh                   # Setup script
├── wordpress/                 # WordPress configurations
│   ├── site1/
│   ├── site2/
│   └── shared-config/
├── database/                  # Database files
│   ├── init/                 # Initialization scripts
│   └── backups/              # Local backup storage
├── python-automation/         # Python automation suite
│   ├── pyproject.toml        # Poetry configuration
│   ├── src/content_ops/      # Main automation modules
│   └── scripts/              # Utility scripts
├── nginx/                     # Nginx configuration
│   └── nginx.conf
├── cron/                      # Scheduled job definitions
│   └── crontab
└── docs/                      # Additional documentation
```

## 🔒 Security Features

- Rate limiting on login endpoints
- Security headers via Nginx
- Database user separation
- Redis password protection
- File upload restrictions
- Automated security updates

## 📈 Monitoring & Logging

All services generate comprehensive logs:

- **Application logs**: `/app/logs/` in automation container
- **Nginx logs**: Available via `docker-compose logs nginx`
- **WordPress logs**: Available via `docker-compose logs wordpress-site1`
- **Database logs**: Available via `docker-compose logs mysql`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

For issues and questions:

1. Check the [documentation](docs/)
2. Review existing [issues](https://github.com/RDComeau/Content-Ops/issues)
3. Create a new issue with detailed information

## 🚀 Roadmap

- [ ] SSL/TLS automation with Let's Encrypt
- [ ] Multi-environment support (dev/staging/prod)
- [ ] Advanced content migration tools
- [ ] Real-time sync capabilities
- [ ] Enhanced monitoring dashboard
- [ ] Plugin management automation
- [ ] Theme deployment pipeline