# Manual Backend Container Fix Guide

## 🚨 Issue Summary
Your backend containers are failing to start due to:
1. Missing `gevent` package (required for Gunicorn)
2. Docker API connectivity issues preventing container management
3. Environment variables not loading properly

## 🔧 Manual Fix Steps

### Step 1: Stop All Running Containers
```bash
# Try these commands in order:
docker compose down
docker-compose down
docker stop $(docker ps -aq)
```

### Step 2: Clean Up Docker System
```bash
# Clean up old containers and images
docker system prune -f
docker volume prune -f
docker image prune -f
```

### Step 3: Restart Docker Desktop
1. Right-click Docker Desktop icon in system tray
2. Click "Restart Docker Desktop"
3. Wait for Docker to fully restart (2-3 minutes)
4. Verify Docker is running: `docker --version`

### Step 4: Rebuild Containers
```bash
# Rebuild from scratch to ensure gevent is installed
docker compose build --no-cache

# Or if compose doesn't work:
docker-compose build --no-cache
```

### Step 5: Start Services in Order
```bash
# Start database first
docker compose up -d postgres redis

# Wait 15-20 seconds for database to be ready
sleep 20

# Start backend
docker compose up -d backend

# Wait 10 seconds for backend to start
sleep 10

# Start remaining services
docker compose up -d frontend nginx celery celery-beat
```

### Step 6: Verify Everything is Working
```bash
# Check service status
docker compose ps

# Check backend logs
docker compose logs backend

# Test backend health
curl http://localhost:8000/health/

# Test full application
curl https://solevaeg.com
```

## 🔍 Troubleshooting

### If Backend Still Fails:
```bash
# Check if gevent is installed
docker compose exec backend python -c "import gevent; print('gevent OK')"

# Check environment variables
docker compose exec backend env | grep DB_

# Check database connectivity
docker compose exec backend python manage.py dbshell
```

### If Nginx Shows Errors:
```bash
# Check Nginx configuration
docker compose logs nginx

# Test backend connectivity from Nginx
docker compose exec nginx curl http://backend:8000/health/
```

### Alternative Commands (if docker-compose doesn't work):
```bash
# Use docker-compose instead of docker compose
docker-compose build --no-cache
docker-compose up -d postgres redis
docker-compose up -d backend
docker-compose up -d frontend nginx celery celery-beat
```

## 📊 Expected Results

After successful fix, you should see:
- ✅ Backend container starts without errors
- ✅ Gunicorn server runs on port 8000
- ✅ Database migrations complete successfully
- ✅ Nginx properly proxies requests to backend
- ✅ Website loads at https://solevaeg.com

## 🎯 Quick Test Commands

```bash
# Test backend directly
curl http://localhost:8000/api/

# Test through Nginx
curl https://solevaeg.com/api/

# Check logs
docker compose logs backend --tail=20
docker compose logs nginx --tail=10
```

## 💡 If Issues Persist

1. **Check Docker Desktop Version**: Ensure you have the latest version
2. **Restart Computer**: Sometimes a full system restart fixes Docker issues
3. **Check Windows Firewall**: Ensure Docker isn't blocked
4. **Reinstall Docker Desktop**: As a last resort if all else fails

## 📞 Support

If you continue having issues:
1. Run: `docker compose logs --tail=50` and share the output
2. Check: `docker --version` and `docker compose version`
3. Verify: Docker Desktop is running and not showing errors
