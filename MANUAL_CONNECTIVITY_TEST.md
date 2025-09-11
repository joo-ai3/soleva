# 🔍 Manual Internal Service Connectivity Test Guide

## Prerequisites
- Docker Desktop running and healthy
- All services started: `docker-compose up -d`

## Quick Start Commands

### 1. Start Services
```bash
docker-compose up -d
```

### 2. Check Service Status
```bash
docker-compose ps
```

### 3. View Service Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs postgres
docker-compose logs redis
```

## 🔧 Manual Connectivity Tests

### Test 1: Backend to PostgreSQL
```bash
docker-compose exec backend python manage.py dbshell -c "SELECT version();"
```

**Expected Output:**
```
PostgreSQL 15.x.x on x86_64-pc-linux-musl, compiled by gcc...
```

### Test 2: Backend to Redis
```bash
docker-compose exec backend python -c "
import redis
import os
r = redis.Redis(host='redis', port=6379, password=os.getenv('REDIS_PASSWORD'))
print('Redis ping:', r.ping())
print('Redis set test:', r.set('test_key', 'test_value'))
print('Redis get test:', r.get('test_key'))
"
```

**Expected Output:**
```
Redis ping: True
Redis set test: True
Redis get test: b'test_value'
```

### Test 3: PostgreSQL Direct Connection
```bash
docker-compose exec postgres pg_isready -U soleva_user -d soleva_db
```

**Expected Output:**
```
/var/lib/postgresql/data:5432 - accepting connections
```

### Test 4: Redis Direct Connection
```bash
docker-compose exec redis redis-cli -a Redis@2025 ping
```

**Expected Output:**
```
PONG
```

### Test 5: Django Health Check
```bash
docker-compose exec backend python manage.py check --deploy
```

**Expected Output:**
```
System check identified no issues.
```

### Test 6: Nginx Health Check
```bash
curl -I http://localhost/health
```

**Expected Output:**
```
HTTP/1.1 200 OK
content-type: text/plain
...
```

## 📊 Connectivity Matrix Verification

Run these commands to verify all connections:

```bash
# Backend → PostgreSQL
docker-compose exec backend python manage.py dbshell -c "SELECT 1;"

# Backend → Redis
docker-compose exec backend python -c "import redis; redis.Redis(host='redis', password='Redis@2025').ping()"

# PostgreSQL self-check
docker-compose exec postgres psql -U soleva_user -d soleva_db -c "SELECT version();"

# Redis self-check
docker-compose exec redis redis-cli -a Redis@2025 info server
```

## 🐛 Troubleshooting

### If Backend Can't Connect to PostgreSQL:
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Check if PostgreSQL is healthy
docker-compose exec postgres pg_isready -U soleva_user -d soleva_db

# Verify environment variables
docker-compose exec backend env | grep DB_
```

### If Backend Can't Connect to Redis:
```bash
# Check Redis logs
docker-compose logs redis

# Test Redis connectivity
docker-compose exec redis redis-cli -a Redis@2025 ping

# Verify Redis password
docker-compose exec backend env | grep REDIS_
```

### If Services Won't Start:
```bash
# Check all logs
docker-compose logs

# Check Docker network
docker network ls

# Restart all services
docker-compose down
docker-compose up -d --build
```

## 🎯 Expected Test Results

| Test | Command | Success Criteria |
|------|---------|------------------|
| Backend→PostgreSQL | `python manage.py dbshell -c "SELECT 1;"` | Returns `1` |
| Backend→Redis | `python -c "import redis; r=redis.Redis(...); r.ping()"` | Returns `True` |
| PostgreSQL Health | `pg_isready -U user -d db` | "accepting connections" |
| Redis Health | `redis-cli ping` | `PONG` |
| Django Check | `python manage.py check` | "no issues" |
| Nginx Health | `curl http://localhost/health` | HTTP 200 |

## 🔒 Security Verification

Verify that internal services are NOT exposed externally:
```bash
# These should fail (connection refused)
curl http://localhost:5432
curl http://localhost:6379

# Only these should work
curl http://localhost:80
curl https://localhost:443
```

## 📝 Test Report Template

```
Internal Connectivity Test Report
=================================

Date: $(date)
Environment: Development/Production

Test Results:
✅ Backend → PostgreSQL: SUCCESS
✅ Backend → Redis: SUCCESS
✅ PostgreSQL Health: SUCCESS
✅ Redis Health: SUCCESS
✅ Nginx Proxy: SUCCESS
✅ Security (No External Exposure): SUCCESS

Issues Found:
- [ ] None
- [ ] PostgreSQL connection failed
- [ ] Redis connection failed
- [ ] Other: ____________________

Recommendations:
_______________________________
_______________________________
```
