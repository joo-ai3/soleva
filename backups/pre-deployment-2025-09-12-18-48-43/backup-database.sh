#!/bin/bash
# Database Backup Script for Soleva
# Run this script after deployment to backup the database

echo "Creating PostgreSQL database backup..."
docker-compose exec -T postgres pg_dump -U soleva_user soleva_db > ".\backups\pre-deployment-2025-09-12-18-48-43/database-backup.sql"

if [ $? -eq 0 ]; then
    echo "Database backup created successfully: .\backups\pre-deployment-2025-09-12-18-48-43/database-backup.sql"
else
    echo "Database backup failed!"
    exit 1
fi

# Create compressed backup
gzip ".\backups\pre-deployment-2025-09-12-18-48-43/database-backup.sql"
echo "Database backup compressed: .\backups\pre-deployment-2025-09-12-18-48-43/database-backup.sql.gz"
