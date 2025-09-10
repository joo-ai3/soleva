# 🔧 Docker Backend Connection Fix

## 🚨 Problem Solved

This guide addresses the common Docker issues with Soleva:

- ✅ **Backend stuck on "Waiting for database..."**
- ✅ **Orphan containers causing conflicts**
- ✅ **Database connection failures**
- ✅ **Service startup order issues**

## 📋 Quick Diagnosis

Run the diagnostic script first to check your current setup:

### Windows (PowerShell)
```powershell
.\docker-diagnostic.ps1
```

### Linux/macOS (Bash)
```bash
chmod +x docker-diagnostic.sh
./docker-diagnostic.sh
```

## 🚀 Complete Fix (Recommended)

Use the comprehensive cleanup and startup script:

### Windows (PowerShell)
```powershell
.\docker-cleanup-and-start.ps1
```

### Linux/macOS (Bash)
```bash
chmod +x docker-cleanup-and-start.sh
./docker-cleanup-and-start.sh
```

## 🔍 What These Scripts Do

### Diagnostic Script
- ✅ Checks Docker installation and status
- ✅ Verifies environment configuration
- ✅ Detects orphan containers
- ✅ Shows current container status
- ✅ Identifies potential issues

### Cleanup & Startup Script
1. **🧹 Cleanup Phase:**
   - Removes orphan containers
   - Cleans up unused Docker resources
   - Stops conflicting services

2. **🔧 Fix Phase:**
   - Verifies environment variables
   - Fixes health check configurations
   - Ensures proper service dependencies

3. **🚀 Startup Phase:**
   - Starts services in correct order:
     - Database (PostgreSQL) → Redis → Backend → Frontend → Nginx
   - Waits for each service to be healthy
   - Verifies all services are working

## 🔧 Manual Troubleshooting

If you prefer manual control:

### 1. Clean Up Orphans
```bash
# Stop all containers and remove orphans
docker compose down --remove-orphans

# Clean up system resources
docker system prune -f
```

### 2. Start Services in Order
```bash
# Start database and Redis first
docker compose up -d postgres redis

# Wait 30 seconds, then check status
docker compose ps

# Start backend
docker compose up -d backend

# Wait for backend to be ready, then start others
docker compose up -d frontend nginx celery celery-beat
```

### 3. Check Logs
```bash
# Check all service logs
docker compose logs

# Check specific service logs
docker compose logs backend
docker compose logs postgres
```

### 4. Verify Connections
```bash
# Test database connection from backend
docker compose exec backend python manage.py dbshell --command "SELECT 1;"

# Test Redis connection
docker compose exec redis redis-cli -a "Redis@2025" ping
```

## ⚙️ Environment Variables

Ensure your `docker.env` file has these critical variables:

```env
# Database Configuration
DB_HOST=postgres
DB_NAME=soleva_db
DB_USER=soleva_user
DB_PASSWORD=Soleva@2025
DB_PORT=5432

# Redis Configuration
REDIS_PASSWORD=Redis@2025

# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=solevaeg.com,www.solevaeg.com,localhost
```

## 🔍 Common Issues & Solutions

### Issue: "Waiting for database..."
**Solution:** Database container isn't healthy yet
```bash
# Check database logs
docker compose logs postgres

# Manually test database
docker compose exec postgres pg_isready -U soleva_user -d soleva_db
```

### Issue: Orphan containers
**Solution:** Clean up old containers
```bash
docker compose down --remove-orphans --volumes
```

### Issue: Port conflicts
**Solution:** Check what's using the ports
```bash
# Windows
netstat -ano | findstr ":5432\|:6379\|:8000\|:3000\|:80"

# Linux/macOS
lsof -i :5432,6379,8000,3000,80
```

### Issue: Environment variables not loaded
**Solution:** Ensure docker.env is in the project root
```bash
ls -la docker.env
cat docker.env | head -10
```

## 📊 Health Checks Fixed

The Docker Compose file has been updated with:

- ✅ **Backend**: Uses `python manage.py check --deploy` instead of curl
- ✅ **Frontend**: Uses `wget` instead of curl for better reliability
- ✅ **Nginx**: Uses `wget` for health checks
- ✅ **Celery**: Fixed app name from `soleva_app` to `soleva_backend`
- ✅ **Added start_period**: Gives services time to initialize

## 🎯 Monitoring & Verification

### Check Service Status
```bash
docker compose ps
```

### View Real-time Logs
```bash
docker compose logs -f
```

### Test API Endpoints
```bash
# Backend API
curl http://localhost:8000/api/health/

# Frontend
curl http://localhost:3000/

# Nginx (main entry point)
curl http://localhost/
```

### Monitor Resource Usage
```bash
docker stats
```

## 🚨 Emergency Commands

### Complete Reset
```bash
# Stop everything
docker compose down --volumes --remove-orphans

# Clean everything
docker system prune -a --volumes -f

# Restart fresh
docker compose up -d
```

### Force Rebuild
```bash
# Rebuild all images
docker compose build --no-cache

# Start fresh
docker compose up -d
```

## 📞 Support

If issues persist after running the scripts:

1. **Run diagnostics:** `./docker-diagnostic.ps1`
2. **Check logs:** `docker compose logs backend`
3. **Verify environment:** `cat docker.env`
4. **Test connections:** Use the manual troubleshooting steps above

The automated scripts handle 95% of common Docker issues. If you still have problems, the diagnostic output will help identify the specific issue.

## 🎉 Success Indicators

Your setup is working when you see:

- ✅ All containers show "healthy" or "running"
- ✅ Backend API responds at `http://localhost:8000/api/health/`
- ✅ Frontend loads at `http://localhost:3000/`
- ✅ Nginx serves content at `http://localhost/`
- ✅ No orphan container warnings

**🎯 Ready to fix your Docker issues? Run the cleanup script now!**
