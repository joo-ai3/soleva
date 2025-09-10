#!/bin/bash
# Docker Diagnostic Script for Soleva (Bash)
# Quickly checks the current state of Docker and containers

echo "🔍 SOLEVA DOCKER DIAGNOSTIC"
echo "============================"

# Check if Docker is running
echo ""
echo "🐳 Checking Docker status..."
if command -v docker &> /dev/null && docker --version &> /dev/null; then
    echo "✅ Docker is running: $(docker --version)"
else
    echo "❌ Docker is not running or not installed"
    echo "   Please start Docker Desktop first"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
    echo "✅ Docker Compose is available"
else
    echo "❌ Docker Compose is not available"
fi

# Check for docker-compose.yml
if [ -f "docker-compose.yml" ]; then
    echo "✅ docker-compose.yml found"
else
    echo "❌ docker-compose.yml not found"
    echo "   Please run this script from the project root directory"
    exit 1
fi

# Check environment file
echo ""
echo "📄 Checking environment configuration..."
if [ -f "docker.env" ]; then
    echo "✅ docker.env file exists"

    # Check critical environment variables
    required_vars=("DB_HOST" "DB_NAME" "DB_USER" "DB_PASSWORD" "REDIS_PASSWORD")

    for var in "${required_vars[@]}"; do
        if grep -q "^${var}=" docker.env; then
            echo "✅ $var is configured"
        else
            echo "❌ $var is missing"
        fi
    done
else
    echo "❌ docker.env file not found"
    if [ -f "docker.env.example" ]; then
        echo "   Found docker.env.example - you may need to copy it"
    fi
fi

# Check current container status
echo ""
echo "📦 Checking container status..."
if docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null; then
    echo "Current containers shown above"
else
    echo "No containers found or unable to check status"
fi

# Check for orphan containers
echo ""
echo "👻 Checking for orphan containers..."
if orphan_containers=$(docker ps -a --filter "label=com.docker.compose.project=soleva" --format "{{.Names}}" 2>/dev/null); then
    if [ -n "$orphan_containers" ]; then
        echo "Found potential orphan containers:"
        echo "$orphan_containers" | sed 's/^/  - /'
        echo "💡 Run cleanup script to remove orphans"
    else
        echo "✅ No orphan containers detected"
    fi
else
    echo "❌ Could not check for orphan containers"
fi

# Check Docker networks
echo ""
echo "🌐 Checking Docker networks..."
if soleva_networks=$(docker network ls --format "{{.Name}}" | grep "soleva" 2>/dev/null); then
    echo "Found Soleva networks:"
    echo "$soleva_networks" | sed 's/^/  - /'
else
    echo "No Soleva networks found (this is normal if services aren't running)"
fi

# Check Docker volumes
echo ""
echo "💾 Checking Docker volumes..."
if soleva_volumes=$(docker volume ls --format "{{.Name}}" | grep "soleva" 2>/dev/null); then
    echo "Found Soleva volumes:"
    echo "$soleva_volumes" | sed 's/^/  - /'
else
    echo "No Soleva volumes found (this is normal if services haven't been started)"
fi

echo ""
echo "🎯 DIAGNOSTIC COMPLETE"
echo "======================"

echo ""
echo "💡 Next steps:"
echo "1. If Docker is not running, start Docker Desktop"
echo "2. If environment variables are missing, check docker.env"
echo "3. If you see orphan containers, run the cleanup script"
echo "4. Run the cleanup and startup script: ./docker-cleanup-and-start.sh"

echo ""
echo "🚀 Ready to fix issues? Run: ./docker-cleanup-and-start.sh"
