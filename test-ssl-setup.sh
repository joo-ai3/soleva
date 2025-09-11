#!/bin/bash

# SSL Setup Test Script for Soleva
# This script tests the SSL certificate installation and HTTPS configuration

set -e

# Load environment variables
if [ -f docker.env ]; then
    export $(cat docker.env | grep -v '^#' | xargs)
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 SSL Setup Verification for Soleva${NC}"
echo "========================================"

# Check if domain is configured
if [ -z "$DOMAIN" ]; then
    echo -e "${RED}❌ DOMAIN environment variable is not set${NC}"
    exit 1
fi

echo -e "${BLUE}Domain:${NC} $DOMAIN"
echo -e "${BLUE}SSL Email:${NC} $SSL_EMAIL"
echo ""

# Check SSL certificate files
echo -e "${YELLOW}📜 Checking SSL certificate files...${NC}"

CERT_PATH="ssl/certbot/conf/live/$DOMAIN"
if [ -d "$CERT_PATH" ]; then
    echo -e "${GREEN}✅ Certificate directory exists: $CERT_PATH${NC}"

    if [ -f "$CERT_PATH/fullchain.pem" ]; then
        echo -e "${GREEN}✅ Full chain certificate found${NC}"
    else
        echo -e "${RED}❌ Full chain certificate missing${NC}"
    fi

    if [ -f "$CERT_PATH/privkey.pem" ]; then
        echo -e "${GREEN}✅ Private key found${NC}"
    else
        echo -e "${RED}❌ Private key missing${NC}"
    fi
else
    echo -e "${RED}❌ Certificate directory not found: $CERT_PATH${NC}"
    echo -e "${YELLOW}💡 Run ./ssl/init-ssl.sh to obtain certificates${NC}"
fi

# Check DH parameters
if [ -f "ssl/certbot/conf/ssl-dhparams.pem" ]; then
    echo -e "${GREEN}✅ DH parameters file exists${NC}"
else
    echo -e "${RED}❌ DH parameters file missing${NC}"
fi

echo ""

# Check Docker services
echo -e "${YELLOW}🐳 Checking Docker services...${NC}"

if docker ps | grep -q soleva_nginx; then
    echo -e "${GREEN}✅ Nginx container is running${NC}"
else
    echo -e "${RED}❌ Nginx container is not running${NC}"
fi

if docker ps | grep -q soleva_certbot; then
    echo -e "${GREEN}✅ Certbot container is running${NC}"
else
    echo -e "${RED}❌ Certbot container is not running${NC}"
fi

echo ""

# Test HTTP to HTTPS redirect (if nginx is running locally)
echo -e "${YELLOW}🔄 Testing HTTP to HTTPS redirect...${NC}"

if curl -s -I http://localhost 2>/dev/null | grep -q "301"; then
    echo -e "${GREEN}✅ HTTP redirect is working${NC}"
else
    echo -e "${YELLOW}⚠️ HTTP redirect test inconclusive (may be normal if nginx is not binding to localhost)${NC}"
fi

# Test HTTPS access (if nginx is running locally)
if curl -s -k -I https://localhost 2>/dev/null | grep -q "200\|301"; then
    echo -e "${GREEN}✅ HTTPS access is working${NC}"
else
    echo -e "${YELLOW}⚠️ HTTPS access test inconclusive (may be normal if nginx is not binding to localhost)${NC}"
fi

echo ""

# DNS check (external)
echo -e "${YELLOW}🌐 DNS Configuration Check...${NC}"

if command -v dig >/dev/null 2>&1; then
    DOMAIN_IP=$(dig +short $DOMAIN 2>/dev/null | head -1)
    WWW_DOMAIN_IP=$(dig +short www.$DOMAIN 2>/dev/null | head -1)

    if [ -n "$DOMAIN_IP" ]; then
        echo -e "${GREEN}✅ $DOMAIN resolves to: $DOMAIN_IP${NC}"
    else
        echo -e "${RED}❌ $DOMAIN does not resolve${NC}"
    fi

    if [ -n "$WWW_DOMAIN_IP" ]; then
        echo -e "${GREEN}✅ www.$DOMAIN resolves to: $WWW_DOMAIN_IP${NC}"
    else
        echo -e "${RED}❌ www.$DOMAIN does not resolve${NC}"
    fi

    # Check if IPs match
    if [ "$DOMAIN_IP" = "$WWW_DOMAIN_IP" ] && [ -n "$DOMAIN_IP" ]; then
        echo -e "${GREEN}✅ DNS records match${NC}"
    elif [ -n "$DOMAIN_IP" ] && [ -n "$WWW_DOMAIN_IP" ]; then
        echo -e "${YELLOW}⚠️ DNS records don't match - this may cause issues${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ dig command not available - skipping DNS check${NC}"
fi

echo ""

# SSL Certificate validation (if certificates exist)
if [ -f "$CERT_PATH/fullchain.pem" ]; then
    echo -e "${YELLOW}🔒 SSL Certificate Information...${NC}"

    # Get certificate info
    CERT_INFO=$(openssl x509 -in "$CERT_PATH/fullchain.pem" -text -noout 2>/dev/null)

    # Extract expiry date
    EXPIRY_DATE=$(echo "$CERT_INFO" | grep "Not After" | cut -d: -f2- | xargs)
    echo -e "${BLUE}Certificate expires:${NC} $EXPIRY_DATE"

    # Check if certificate is valid
    if openssl x509 -checkend 86400 -in "$CERT_PATH/fullchain.pem" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Certificate is valid (not expired)${NC}"
    else
        echo -e "${RED}❌ Certificate has expired or will expire within 24 hours${NC}"
    fi

    # Check domains in certificate
    CERT_DOMAINS=$(echo "$CERT_INFO" | grep "DNS:" | sed 's/.*DNS://g' | tr -d ' ')
    echo -e "${BLUE}Certificate domains:${NC} $CERT_DOMAINS"

    if echo "$CERT_DOMAINS" | grep -q "$DOMAIN"; then
        echo -e "${GREEN}✅ Primary domain ($DOMAIN) is in certificate${NC}"
    else
        echo -e "${RED}❌ Primary domain ($DOMAIN) is not in certificate${NC}"
    fi

    if echo "$CERT_DOMAINS" | grep -q "www.$DOMAIN"; then
        echo -e "${GREEN}✅ WWW domain (www.$DOMAIN) is in certificate${NC}"
    else
        echo -e "${RED}❌ WWW domain (www.$DOMAIN) is not in certificate${NC}"
    fi
fi

echo ""

# Recommendations
echo -e "${BLUE}📋 Recommendations:${NC}"
echo "1. Ensure DNS A records point to your server IP:"
echo "   $DOMAIN A [YOUR_SERVER_IP]"
echo "   www.$DOMAIN A [YOUR_SERVER_IP]"
echo ""
echo "2. Test live URLs after DNS propagation:"
echo "   https://$DOMAIN"
echo "   https://www.$DOMAIN"
echo "   http://$DOMAIN (should redirect to HTTPS)"
echo "   http://www.$DOMAIN (should redirect to HTTPS)"
echo ""
echo "3. SSL certificates auto-renew every 12 hours via certbot container"
echo "4. Monitor logs: docker-compose -f docker-compose.production.yml logs -f nginx"
echo ""

echo -e "${GREEN}🎉 SSL setup verification completed!${NC}"
