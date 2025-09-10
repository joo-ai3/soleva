#!/bin/bash

# SSL Certificate Renewal Script for Soleva
# This script renews SSL certificates and reloads Nginx

set -e

echo "🔐 Starting SSL certificate renewal process..."

# Check if Docker Compose is available
if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null; then
    echo "❌ Docker or Docker Compose not found!"
    exit 1
fi

# Renew certificates using the renewal profile
echo "📋 Renewing SSL certificates..."
docker compose --profile renewal run --rm certbot-renew

# Check if renewal was successful
if [ $? -eq 0 ]; then
    echo "✅ Certificate renewal completed successfully"
    
    # Reload Nginx to apply new certificates
    echo "🔄 Reloading Nginx configuration..."
    docker compose exec nginx nginx -s reload
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx reloaded successfully"
        echo "🎉 SSL certificate renewal process completed!"
    else
        echo "⚠️  Warning: Certificate renewed but Nginx reload failed"
        echo "   You may need to restart the Nginx container manually:"
        echo "   docker compose restart nginx"
    fi
else
    echo "❌ Certificate renewal failed"
    exit 1
fi

# Optional: Clean up old certificates (older than 30 days)
echo "🧹 Cleaning up old certificate files..."
docker compose exec nginx find /etc/letsencrypt/archive -name "*.pem" -mtime +30 -delete 2>/dev/null || true

echo "✨ SSL renewal process completed successfully!"
