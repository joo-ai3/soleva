#!/bin/bash

# SSL Certificate Renewal Script for Soleva
# This script renews SSL certificates using Let's Encrypt Certbot

set -e

echo "Checking for SSL certificate renewals..."

# Run certbot renewal
docker run --rm -v "$(pwd)/certbot/conf:/etc/letsencrypt" -v "$(pwd)/certbot/www:/var/www/certbot" certbot/certbot renew --webroot --webroot-path=/var/www/certbot

# Reload nginx to pick up new certificates
echo "Reloading nginx configuration..."
docker exec soleva_nginx nginx -s reload

echo "SSL certificate renewal completed successfully!"
