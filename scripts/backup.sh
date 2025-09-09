#!/bin/bash
# Quick backup script for Content Ops

echo "🗄️  Starting manual backup..."

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Services are not running. Please start with: docker-compose up -d"
    exit 1
fi

# Run backup
docker-compose exec -T automation python -m content_ops.backup --upload --cleanup

if [ $? -eq 0 ]; then
    echo "✅ Backup completed successfully!"
else
    echo "❌ Backup failed!"
    exit 1
fi