#!/bin/bash

# =======================================
# Soleva Environment Test Script
# =======================================
# This script tests if the environment is properly configured

echo "🧪 Testing Soleva Environment Setup..."
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    local status=$1
    local message=$2
    if [ "$status" -eq 0 ]; then
        echo -e "${GREEN}✅ $message${NC}"
    else
        echo -e "${RED}❌ $message${NC}"
    fi
}

# Check if .env file exists
echo "📁 Checking .env file..."
if [ -f ".env" ]; then
    print_status 0 ".env file exists"
else
    print_status 1 ".env file missing - run setup-env.sh first"
    exit 1
fi

# Check if .env is in .gitignore
echo "🔒 Checking .gitignore security..."
if grep -q "^\.env$" .gitignore; then
    print_status 0 ".env is properly ignored in .gitignore"
else
    print_status 1 ".env is NOT in .gitignore - add it for security!"
fi

# Check docker-compose.yml exists
echo "🐳 Checking docker-compose.yml..."
if [ -f "docker-compose.yml" ]; then
    print_status 0 "docker-compose.yml exists"
else
    print_status 1 "docker-compose.yml missing"
    exit 1
fi

# Validate environment variables
echo "🔧 Validating environment variables..."
source .env

required_vars=("DB_NAME" "DB_USER" "DB_PASSWORD" "REDIS_PASSWORD" "SECRET_KEY" "DOMAIN")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -eq 0 ]; then
    print_status 0 "All required environment variables are set"
else
    print_status 1 "Missing environment variables: ${missing_vars[*]}"
fi

# Test Docker availability
echo "🐳 Checking Docker..."
if command -v docker &> /dev/null; then
    print_status 0 "Docker is installed"
else
    print_status 1 "Docker is not installed"
    exit 1
fi

# Test Docker Compose availability
echo "🐳 Checking Docker Compose..."
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
    print_status 0 "Docker Compose is available"
else
    print_status 1 "Docker Compose is not available"
    exit 1
fi

echo ""
echo "📊 Environment Summary:"
echo "=========================="
echo "Database: PostgreSQL ($DB_NAME)"
echo "Redis: Enabled with authentication"
echo "Backend: Django (DEBUG=$DEBUG)"
echo "Domain: $DOMAIN"
echo ""

echo "🚀 Ready to start services!"
echo "=========================="
echo "Run: docker compose up -d"
echo ""
echo "Check status: docker compose ps"
echo ""
echo "View logs: docker compose logs -f"
echo ""
echo "Stop services: docker compose down"
