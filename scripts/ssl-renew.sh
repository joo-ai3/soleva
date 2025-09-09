#!/bin/bash

# SSL Certificate Renewal Script for Soleva Platform
# This script should be run by cron to automatically renew SSL certificates

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/var/www/soleva-platform"  # Adjust to your project directory
LOG_FILE="/var/log/soleva-ssl-renewal.log"

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

# Change to project directory
cd "$PROJECT_DIR" || error "Cannot change to project directory: $PROJECT_DIR"

# Load environment variables
if [ -f ".env" ]; then
    source .env
else
    error ".env file not found in $PROJECT_DIR"
fi

log "Starting SSL certificate renewal for $DOMAIN"

# Check if certificates expire in the next 30 days
EXPIRY_DATE=$(openssl x509 -enddate -noout -in "letsencrypt/live/$DOMAIN/cert.pem" 2>/dev/null | cut -d= -f2)
if [ -n "$EXPIRY_DATE" ]; then
    EXPIRY_TIMESTAMP=$(date -d "$EXPIRY_DATE" +%s)
    CURRENT_TIMESTAMP=$(date +%s)
    DAYS_UNTIL_EXPIRY=$(( (EXPIRY_TIMESTAMP - CURRENT_TIMESTAMP) / 86400 ))
    
    if [ $DAYS_UNTIL_EXPIRY -gt 30 ]; then
        log "Certificate is valid for $DAYS_UNTIL_EXPIRY more days. No renewal needed."
        exit 0
    fi
    
    log "Certificate expires in $DAYS_UNTIL_EXPIRY days. Proceeding with renewal."
else
    warn "Could not check certificate expiry. Proceeding with renewal."
fi

# Renew certificates
log "Attempting to renew SSL certificates..."
docker-compose run --rm certbot renew --quiet

# Check if renewal was successful
if [ $? -eq 0 ]; then
    log "✅ SSL certificate renewal successful"
    
    # Reload nginx to use new certificates
    log "Reloading Nginx to use new certificates..."
    docker-compose exec nginx nginx -s reload
    
    if [ $? -eq 0 ]; then
        log "✅ Nginx reloaded successfully"
    else
        error "Failed to reload Nginx"
    fi
    
    # Test the new certificate
    log "Testing new certificate..."
    if curl -sSf "https://$DOMAIN" > /dev/null; then
        log "✅ Certificate test successful"
    else
        warn "Certificate test failed - website may not be accessible"
    fi
    
else
    error "SSL certificate renewal failed"
fi

log "SSL certificate renewal process completed"
