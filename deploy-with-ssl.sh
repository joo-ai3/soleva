#!/bin/bash

# Soleva Production Deployment Script with SSL Setup
# This script deploys the application and sets up SSL certificates

set -e

echo "🚀 Starting Soleva Production Deployment with SSL Setup"
echo "======================================================"

# Load environment variables
if [ -f docker.env ]; then
    export $(cat docker.env | grep -v '^#' | xargs)
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists docker; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command_exists docker-compose; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if domain is configured
if [ -z "$DOMAIN" ]; then
    echo "❌ DOMAIN environment variable is not set"
    echo "Please set DOMAIN=solevaeg.com in docker.env file"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p ssl/certbot/conf ssl/certbot/www logs/nginx

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.production.yml down || true

# Build and start services (except certbot initially)
echo "🏗️ Building and starting services..."
docker-compose -f docker-compose.production.yml up -d --build postgres redis backend frontend

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Initialize SSL certificates
echo "🔐 Initializing SSL certificates..."
if [ ! -d "ssl/certbot/conf/live/$DOMAIN" ]; then
    echo "📜 Obtaining SSL certificates from Let's Encrypt..."
    docker run --rm \
        -v "$(pwd)/ssl/certbot/conf:/etc/letsencrypt" \
        -v "$(pwd)/ssl/certbot/www:/var/www/certbot" \
        certbot/certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email "$SSL_EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN" \
        -d "www.$DOMAIN"

    # Generate DH parameters
    echo "🔧 Generating DH parameters..."
    openssl dhparam -out ssl/certbot/conf/ssl-dhparams.pem 2048
else
    echo "✅ SSL certificates already exist"
fi

# Start nginx and certbot
echo "🌐 Starting nginx and certbot services..."
docker-compose -f docker-compose.production.yml up -d nginx certbot

# Wait for nginx to start
echo "⏳ Waiting for nginx to start..."
sleep 10

# Test the deployment
echo "🧪 Testing deployment..."
echo "Testing HTTP to HTTPS redirect..."
curl -I http://localhost | grep -q "301" && echo "✅ HTTP redirect working" || echo "⚠️ HTTP redirect may not be working"

echo "Testing HTTPS access..."
curl -I -k https://localhost | grep -q "200" && echo "✅ HTTPS access working" || echo "⚠️ HTTPS access may not be working"

echo ""
echo "🎉 Deployment completed successfully!"
echo "======================================================"
echo ""
echo "📋 Next steps:"
echo "1. Update your DNS A records to point $DOMAIN and www.$DOMAIN to your server IP"
echo "2. Wait for DNS propagation (can take up to 48 hours)"
echo "3. Test the live site: https://$DOMAIN"
echo "4. Monitor SSL certificate renewal (happens automatically every 12 hours)"
echo ""
echo "🔗 Useful commands:"
echo "- View logs: docker-compose -f docker-compose.production.yml logs -f"
echo "- Restart services: docker-compose -f docker-compose.production.yml restart"
echo "- Renew SSL manually: ./ssl/renew-ssl.sh"
echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.production.yml ps
