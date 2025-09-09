# Content Operations Setup Guide

This guide provides detailed instructions for setting up and configuring the Content Operations platform.

## System Requirements

### Minimum Requirements
- 4 GB RAM
- 20 GB available disk space
- Docker 20.10+
- Docker Compose 2.0+

### Recommended Requirements
- 8 GB RAM
- 50 GB available disk space
- SSD storage for database
- Dedicated server or VPS

## Initial Setup

### 1. Environment Configuration

After running `./setup.sh`, you'll need to configure your `.env` file:

#### Database Configuration
```env
MYSQL_ROOT_PASSWORD=your_very_secure_root_password
MYSQL_DATABASE=content_ops
MYSQL_USER=content_user
MYSQL_PASSWORD=your_secure_user_password
```

#### WordPress Sites
```env
SITE1_DOMAIN=myblog.com
SITE1_TITLE=My Personal Blog
SITE1_ADMIN_USER=admin
SITE1_ADMIN_PASSWORD=secure_admin_password
SITE1_ADMIN_EMAIL=admin@myblog.com

SITE2_DOMAIN=myportfolio.com
SITE2_TITLE=My Portfolio
SITE2_ADMIN_USER=admin
SITE2_ADMIN_PASSWORD=secure_admin_password
SITE2_ADMIN_EMAIL=admin@myportfolio.com
```

#### Cloudflare R2 Setup
1. Create a Cloudflare account and enable R2
2. Create an R2 bucket for backups
3. Generate API tokens with R2 permissions

```env
R2_ACCOUNT_ID=your_cloudflare_account_id
R2_ACCESS_KEY_ID=your_r2_access_key
R2_SECRET_ACCESS_KEY=your_r2_secret_key
R2_BUCKET_NAME=content-ops-backups
R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
```

### 2. Domain Configuration

#### For Local Development
Add these entries to your `/etc/hosts` file:
```
127.0.0.1 site1.localhost
127.0.0.1 site2.localhost
```

#### For Production
1. Point your domains to your server's IP address
2. Update the domain names in `.env`
3. Configure SSL certificates (see SSL Setup section)

### 3. Starting Services

```bash
# Start all services
docker-compose up -d

# Verify all containers are running
docker-compose ps

# Check logs for any errors
docker-compose logs
```

## WordPress Configuration

### Initial WordPress Setup

1. **Access WordPress Admin**
   - Site 1: http://site1.localhost/wp-admin
   - Site 2: http://site2.localhost/wp-admin

2. **Complete WordPress Installation**
   - Follow the WordPress setup wizard
   - Use the credentials from your `.env` file

3. **Install Recommended Plugins**
   ```bash
   # Redis Object Cache
   docker-compose exec wordpress-site1 wp plugin install redis-cache --activate
   
   # Security plugin
   docker-compose exec wordpress-site1 wp plugin install wordfence --activate
   
   # Backup plugin (as fallback)
   docker-compose exec wordpress-site1 wp plugin install updraftplus --activate
   ```

### Shared Configuration

The shared configuration in `wordpress/shared-config/content-ops-config.php` provides:

- Redis cache configuration
- Security enhancements
- Performance optimizations
- Cross-site functionality
- Custom REST API endpoints

## Database Management

### Backup Operations

#### Automated Backups
Backups run automatically daily at 2 AM. You can also trigger manual backups:

```bash
# Manual backup with R2 upload
docker-compose exec automation python -m content_ops.backup

# Backup specific tables only
docker-compose exec automation python python/scripts/backup_now.py --tables "site1_posts,site1_users"
```

#### Restore Operations
```bash
# Download backup from R2
docker-compose exec automation python -m content_ops.r2_storage download backups/backup_file.sql /app/backups/

# Restore database
docker-compose exec mysql mysql -u root -p content_ops < /backups/backup_file.sql
```

### Database Optimization

#### Regular Maintenance
```bash
# Cleanup old revisions (older than 30 days)
docker-compose exec automation python -m content_ops.content_sync cleanup-revisions site1_ --days 30

# Optimize database tables
docker-compose exec mysql mysqlcheck -u root -p --optimize content_ops
```

## Content Synchronization

### Automated Sync
Content synchronization runs every 6 hours automatically. Features include:

- Featured content sharing between sites
- User registration sync
- Cross-site link updates
- Revision cleanup

### Manual Sync Operations
```bash
# Full synchronization
docker-compose exec automation python -m content_ops.content_sync full-sync

# Sync specific content type
docker-compose exec automation python python/scripts/sync_content.py --source site1 --target site2
```

## Monitoring & Maintenance

### Health Checks

#### System Health
```bash
# Check overall system health
docker-compose exec automation python -m content_ops.scheduler run-job health_check

# Check individual services
curl http://site1.localhost/wp-json/content-ops/v1/health
curl http://site2.localhost/wp-json/content-ops/v1/health
```

#### Performance Monitoring
```bash
# View resource usage
docker stats

# Check database performance
docker-compose exec mysql mysqladmin -u root -p status

# Check Redis cache
docker-compose exec redis redis-cli info stats
```

### Log Management

#### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f wordpress-site1
docker-compose logs -f automation

# Python automation logs
docker-compose exec automation tail -f /app/logs/scheduler.log
docker-compose exec automation tail -f /app/logs/backup.log
```

#### Log Rotation
Logs are automatically rotated by Docker. For custom log management:

```bash
# Configure log rotation in docker-compose.yml
services:
  wordpress-site1:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Security Configuration

### SSL/TLS Setup

#### Using Let's Encrypt (Recommended)
```bash
# Install Certbot
sudo apt-get install certbot

# Generate certificates
sudo certbot certonly --standalone -d site1.yourdomain.com -d site2.yourdomain.com

# Update nginx configuration with SSL
# Add SSL configuration to nginx/nginx.conf
```

#### Using Custom Certificates
1. Place your certificates in `nginx/ssl/`
2. Update `nginx/nginx.conf` with SSL configuration
3. Restart nginx: `docker-compose restart nginx`

### Security Hardening

#### Database Security
```bash
# Change default passwords
docker-compose exec mysql mysql -u root -p -e "ALTER USER 'root'@'%' IDENTIFIED BY 'new_secure_password';"

# Remove test databases
docker-compose exec mysql mysql -u root -p -e "DROP DATABASE IF EXISTS test;"
```

#### WordPress Security
1. Update `wordpress/shared-config/content-ops-config.php` with security keys
2. Install security plugins (Wordfence, Sucuri)
3. Configure firewall rules
4. Enable two-factor authentication

## Troubleshooting

### Common Issues

#### WordPress Site Not Loading
```bash
# Check if containers are running
docker-compose ps

# Check WordPress logs
docker-compose logs wordpress-site1

# Verify database connection
docker-compose exec wordpress-site1 wp db check
```

#### Database Connection Issues
```bash
# Verify MySQL is running
docker-compose exec mysql mysqladmin -u root -p ping

# Check database permissions
docker-compose exec mysql mysql -u root -p -e "SHOW GRANTS FOR 'content_user'@'%';"
```

#### Backup Failures
```bash
# Check R2 credentials
docker-compose exec automation python -c "from content_ops.r2_storage import R2Storage; r2 = R2Storage(); print('R2 connection successful')"

# Check backup logs
docker-compose exec automation tail -f /app/logs/backup.log
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Monitor database queries
docker-compose exec mysql mysqladmin -u root -p processlist

# Check Redis cache hit ratio
docker-compose exec redis redis-cli info stats | grep hit
```

### Recovery Procedures

#### Complete System Recovery
```bash
# Stop all services
docker-compose down

# Backup current data
cp -r database/data database/data.backup

# Restore from backup
# ... restore procedures ...

# Restart services
docker-compose up -d
```

## Advanced Configuration

### Custom Python Scripts

1. Create new modules in `python-automation/src/content_ops/`
2. Add CLI commands using Click
3. Update `pyproject.toml` with new entry points
4. Rebuild automation container: `docker-compose build automation`

### Custom WordPress Themes/Plugins

1. Add themes to `wordpress/site1/wp-content/themes/`
2. Add plugins to `wordpress/site1/wp-content/plugins/`
3. Restart WordPress containers: `docker-compose restart wordpress-site1`

### Custom Nginx Configuration

1. Edit `nginx/nginx.conf`
2. Add custom configurations to `nginx/sites/`
3. Restart nginx: `docker-compose restart nginx`

## Performance Optimization

### Database Optimization
- Regular maintenance and optimization
- Proper indexing for custom queries
- Query cache configuration
- Connection pooling

### Caching Strategy
- Redis object cache for WordPress
- Nginx caching for static files
- CDN integration for global performance

### Resource Allocation
- Adjust memory limits in docker-compose.yml
- Scale services based on load
- Monitor and optimize container resources

This setup guide should help you get started with Content Operations. For additional support, refer to the main README.md or create an issue in the repository.