#!/bin/bash
# Content Ops setup script
# This script initializes the Content Ops environment

set -e

echo "🚀 Setting up Content Ops environment..."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
    echo "📋 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual configuration values!"
    echo "   Required: MYSQL passwords, Redis password, R2 credentials"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p database/data
mkdir -p database/backups
mkdir -p wordpress/site1/wp-content/uploads
mkdir -p wordpress/site2/wp-content/uploads
mkdir -p nginx/ssl
mkdir -p python-automation/logs

# Set proper permissions
echo "🔐 Setting permissions..."
chmod 755 python-automation/scripts/*.py
chmod 600 cron/crontab

# Initialize Poetry in Python automation directory
echo "🐍 Initializing Python environment..."
cd python-automation

if command -v poetry &> /dev/null; then
    echo "📦 Installing Python dependencies with Poetry..."
    poetry install
else
    echo "⚠️  Poetry not found. Install Poetry for dependency management:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
fi

cd ..

# Build Docker images
echo "🐳 Building Docker images..."
docker-compose build

echo "✅ Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run: docker-compose up -d"
echo "3. Access your sites:"
echo "   - Site 1: http://site1.localhost"
echo "   - Site 2: http://site2.localhost"
echo ""
echo "🛠️  Available commands:"
echo "   - docker-compose up -d          # Start all services"
echo "   - docker-compose down           # Stop all services"
echo "   - docker-compose logs -f        # View logs"
echo "   - ./scripts/backup_now.sh       # Manual backup"
echo "   - ./scripts/sync_content.sh     # Manual content sync"