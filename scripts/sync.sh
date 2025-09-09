#!/bin/bash
# Quick content sync script for Content Ops

echo "🔄 Starting content synchronization..."

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Services are not running. Please start with: docker-compose up -d"
    exit 1
fi

# Run full sync
docker-compose exec -T automation python -m content_ops.content_sync full-sync

if [ $? -eq 0 ]; then
    echo "✅ Content synchronization completed successfully!"
else
    echo "❌ Content synchronization failed!"
    exit 1
fi