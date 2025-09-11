#!/bin/bash

# SSL Certificate Initialization Script for Soleva
# This script initializes SSL certificates using Let's Encrypt Certbot

set -e

# Load environment variables
if [ -f ../docker.env ]; then
    export $(cat ../docker.env | grep -v '^#' | xargs)
fi

# Check if domain is set
if [ -z "$DOMAIN" ]; then
    echo "Error: DOMAIN environment variable is not set"
    echo "Please set DOMAIN=solevaeg.com in docker.env file"
    exit 1
fi

# Check if SSL email is set
if [ -z "$SSL_EMAIL" ]; then
    echo "Error: SSL_EMAIL environment variable is not set"
    echo "Please set SSL_EMAIL=support@solevaeg.com in docker.env file"
    exit 1
fi

echo "Initializing SSL certificates for $DOMAIN and www.$DOMAIN"
echo "Using email: $SSL_EMAIL"

# Create necessary directories
mkdir -p certbot/conf certbot/www

# Stop nginx temporarily for certificate initialization (if running)
echo "Stopping nginx container if running..."
docker stop soleva_nginx || true

# Wait a moment
sleep 2

# Run certbot to get certificates
echo "Requesting SSL certificates from Let's Encrypt..."
docker run --rm \
    -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
    -v "$(pwd)/certbot/www:/var/www/certbot" \
    certbot/certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$SSL_EMAIL" \
    --agree-tos \
    --no-eff-email \
    --non-interactive \
    --keep-until-expiring \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

# Check if certificates were obtained successfully
if [ -d "certbot/conf/live/$DOMAIN" ]; then
    echo "✅ SSL certificates obtained successfully!"

    # Generate DH parameters if not exists
    if [ ! -f "certbot/conf/ssl-dhparams.pem" ]; then
        echo "Generating DH parameters..."
        openssl dhparam -out certbot/conf/ssl-dhparams.pem 2048
    fi

    # Start nginx again
    echo "Starting nginx container..."
    docker start soleva_nginx

    echo ""
    echo "🎉 SSL Setup Complete!"
    echo "Certificate files are located in: ssl/certbot/conf/live/$DOMAIN/"
    echo ""
    echo "📋 Next steps:"
    echo "1. ✅ DNS already configured: $DOMAIN → $(curl -s ifconfig.me)"
    echo "2. 🌐 Test HTTPS access: https://$DOMAIN"
    echo "3. 🔄 Certificates will auto-renew every 60 days"
    echo ""
    echo "🔗 Quick test commands:"
    echo "   curl -I https://$DOMAIN"
    echo "   curl -I https://www.$DOMAIN"
else
    echo "❌ Failed to obtain SSL certificates"
    echo "Please check the error messages above and try again"
    exit 1
fi
