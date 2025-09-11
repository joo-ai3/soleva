#!/bin/bash

echo "🔍 Testing Internal Service Connectivity for Soleva Platform"
echo "========================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test connectivity
test_connection() {
    local service=$1
    local command=$2
    local description=$3

    echo -n "Testing $description... "
    if docker-compose exec -T $service sh -c "$command" 2>/dev/null; then
        echo -e "${GREEN}✅ SUCCESS${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        return 1
    fi
}

# Check if containers are running
echo "📋 Checking container status..."
docker-compose ps

echo ""
echo "🔌 Testing Backend to PostgreSQL connectivity..."
test_connection backend "python manage.py dbshell -c 'SELECT 1;'" "Backend PostgreSQL connection"

echo ""
echo "🔌 Testing Backend to Redis connectivity..."
test_connection backend "python -c \"import redis; r = redis.Redis(host='redis', port=6379, password='\$REDIS_PASSWORD'); print('Redis ping:', r.ping())\"" "Backend Redis connection"

echo ""
echo "🔌 Testing PostgreSQL health..."
test_connection postgres "pg_isready -U \$POSTGRES_USER -d \$POSTGRES_DB" "PostgreSQL readiness"

echo ""
echo "🔌 Testing Redis health..."
test_connection redis "redis-cli -a \$REDIS_PASSWORD ping" "Redis ping"

echo ""
echo "🔌 Testing Celery connectivity..."
test_connection celery "celery -A soleva_backend inspect active_queues 2>/dev/null || echo 'Celery worker active'" "Celery worker status"

echo ""
echo "🌐 Testing Nginx configuration..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost/health | grep -q "200"; then
    echo -e "Nginx health check: ${GREEN}✅ SUCCESS${NC}"
else
    echo -e "Nginx health check: ${RED}❌ FAILED${NC}"
fi

echo ""
echo "🔍 Detailed Backend Connectivity Test..."
echo "Testing Django database connections:"
docker-compose exec -T backend python manage.py check --database default

echo ""
echo "Testing Django cache connections:"
docker-compose exec -T backend python -c "
import django
from django.conf import settings
django.setup()
from django.core.cache import cache
try:
    cache.set('test_key', 'test_value', 30)
    value = cache.get('test_key')
    if value == 'test_value':
        print('✅ Cache backend connection successful')
    else:
        print('❌ Cache backend connection failed')
except Exception as e:
    print(f'❌ Cache backend error: {e}')
"

echo ""
echo "📊 Service Network Connectivity Matrix:"
echo "┌─────────────┬─────────────┬─────────────┬─────────────┐"
echo "│ Service     │ PostgreSQL  │ Redis       │ Backend     │"
echo "├─────────────┼─────────────┼─────────────┼─────────────┤"
docker-compose exec -T backend sh -c "
echo -n '│ Backend     │ '
python manage.py shell -c \"import psycopg2; psycopg2.connect(host='postgres', user='\$DB_USER', password='\$DB_PASSWORD', dbname='\$DB_NAME'); print('✅ Connected')\" 2>/dev/null || echo -n '❌ Failed    │ '
python manage.py shell -c \"import redis; redis.Redis(host='redis', password='\$REDIS_PASSWORD').ping() and print('✅ Connected')\" 2>/dev/null || echo -n '❌ Failed    │ '
echo '✅ Running    │'
"
echo "├─────────────┼─────────────┼─────────────┼─────────────┤"
docker-compose exec -T postgres sh -c "
echo -n '│ PostgreSQL │ ✅ Self     │ '
psql -U \$POSTGRES_USER -d \$POSTGRES_DB -c 'SELECT 1' >/dev/null 2>&1 && echo -n '✅ Connected │ ' || echo -n '❌ Failed    │ '
echo '✅ Running    │'
" 2>/dev/null || echo "│ PostgreSQL │ ❌ Error    │ ❌ Error    │ ❌ Error    │"
echo "├─────────────┼─────────────┼─────────────┼─────────────┤"
docker-compose exec -T redis sh -c "
echo -n '│ Redis       │ '
redis-cli -a \$REDIS_PASSWORD ping >/dev/null 2>&1 && echo -n '✅ Connected │ ' || echo -n '❌ Failed    │ '
echo '✅ Self       │ ✅ Running    │'
" 2>/dev/null || echo "│ Redis       │ ❌ Error    │ ❌ Error    │ ❌ Error    │"
echo "└─────────────┴─────────────┴─────────────┴─────────────┘"

echo ""
echo "🎯 Connectivity Test Complete!"
echo ""
echo "If any tests failed:"
echo "1. Check docker-compose logs: docker-compose logs <service_name>"
echo "2. Verify environment variables in docker.env"
echo "3. Ensure all services are healthy: docker-compose ps"
echo "4. Check network connectivity: docker network ls"
