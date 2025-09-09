#!/bin/bash

# Automated Backup Script for Soleva Platform
# This script creates backups of the database and media files

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/var/www/soleva-platform"  # Adjust to your project directory
BACKUP_DIR="/var/backups/soleva"
LOG_FILE="/var/log/soleva-backup.log"
RETENTION_DAYS=30  # Keep backups for 30 days

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Change to project directory
cd "$PROJECT_DIR" || error "Cannot change to project directory: $PROJECT_DIR"

# Load environment variables
if [ -f ".env" ]; then
    source .env
else
    error ".env file not found in $PROJECT_DIR"
fi

# Generate timestamp for backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="soleva_backup_$TIMESTAMP"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

log "Starting backup process: $BACKUP_NAME"

# Create backup directory
mkdir -p "$BACKUP_PATH"

# 1. Database Backup
log "Creating database backup..."
docker-compose exec -T postgres pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_PATH/database.sql.gz"

if [ $? -eq 0 ]; then
    DB_SIZE=$(du -h "$BACKUP_PATH/database.sql.gz" | cut -f1)
    log "✅ Database backup completed (Size: $DB_SIZE)"
else
    error "Database backup failed"
fi

# 2. Media Files Backup
log "Creating media files backup..."
if docker-compose exec backend test -d /app/media; then
    docker cp soleva_backend:/app/media "$BACKUP_PATH/"
    
    if [ $? -eq 0 ]; then
        MEDIA_SIZE=$(du -sh "$BACKUP_PATH/media" | cut -f1)
        log "✅ Media files backup completed (Size: $MEDIA_SIZE)"
    else
        warn "Media files backup failed"
    fi
else
    warn "No media files found to backup"
fi

# 3. Configuration Backup
log "Creating configuration backup..."
cp .env "$BACKUP_PATH/env_backup.txt" 2>/dev/null || warn "Could not backup .env file"
cp docker-compose.yml "$BACKUP_PATH/" 2>/dev/null || warn "Could not backup docker-compose.yml"

# 4. SSL Certificates Backup (if they exist)
if [ -d "letsencrypt" ]; then
    log "Creating SSL certificates backup..."
    cp -r letsencrypt "$BACKUP_PATH/" 2>/dev/null || warn "Could not backup SSL certificates"
fi

# 5. Create backup manifest
log "Creating backup manifest..."
cat > "$BACKUP_PATH/manifest.txt" << EOF
Soleva Platform Backup
======================
Backup Date: $(date)
Backup Name: $BACKUP_NAME
Database: $DB_NAME
Domain: $DOMAIN

Contents:
- database.sql.gz: PostgreSQL database dump
- media/: User uploaded files and payment proofs
- env_backup.txt: Environment configuration
- docker-compose.yml: Docker configuration
- letsencrypt/: SSL certificates (if present)

Backup Size: $(du -sh "$BACKUP_PATH" | cut -f1)
EOF

# 6. Create compressed archive
log "Creating compressed archive..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"

if [ $? -eq 0 ]; then
    # Remove uncompressed backup directory
    rm -rf "$BACKUP_NAME"
    
    ARCHIVE_SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)
    log "✅ Compressed backup created: ${BACKUP_NAME}.tar.gz (Size: $ARCHIVE_SIZE)"
else
    error "Failed to create compressed archive"
fi

# 7. Cleanup old backups
log "Cleaning up old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "soleva_backup_*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete

# Count remaining backups
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "soleva_backup_*.tar.gz" -type f | wc -l)
log "✅ Cleanup completed. $BACKUP_COUNT backup(s) retained."

# 8. Optional: Upload to cloud storage
if [ -n "$AWS_S3_BUCKET" ] && command -v aws &> /dev/null; then
    log "Uploading backup to S3..."
    aws s3 cp "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" "s3://$AWS_S3_BUCKET/backups/"
    
    if [ $? -eq 0 ]; then
        log "✅ Backup uploaded to S3 successfully"
    else
        warn "Failed to upload backup to S3"
    fi
fi

# 9. Send notification (optional)
if [ -n "$SLACK_WEBHOOK_URL" ]; then
    TOTAL_SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"✅ Soleva backup completed successfully\n📦 Size: $TOTAL_SIZE\n📅 Date: $(date)\n🗂️ File: ${BACKUP_NAME}.tar.gz\"}" \
        "$SLACK_WEBHOOK_URL" > /dev/null 2>&1 || warn "Failed to send Slack notification"
fi

# 10. Summary
log "Backup process completed successfully!"
info "Backup location: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
info "Backup size: $(du -h "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)"
info "Total backups: $BACKUP_COUNT"

# Set proper permissions
chmod 600 "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"

log "🎉 Backup process finished!"
