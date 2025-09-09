# 🐳 Docker Quick Start Guide

## 🚨 **Issues Fixed**

Your Docker setup had two main issues that have been resolved:

### ✅ **Issue 1: Missing Environment Variables** - **FIXED**
- **Problem**: All environment variables were showing as "not set"
- **Solution**: Created `.env` file from `docker.env.example` template
- **Status**: ✅ **RESOLVED**

### ✅ **Issue 2: Obsolete Docker Compose Version** - **FIXED**
- **Problem**: `version: '3.8'` attribute is obsolete in newer Docker Compose
- **Solution**: Removed `version` attribute from both docker-compose files
- **Status**: ✅ **RESOLVED**

---

## 🚀 **Quick Start Instructions**

### **Option 1: Automated Startup (Recommended)**
```powershell
# Run the automated startup script
.\docker-startup.ps1
```

### **Option 2: Manual Startup**
```powershell
# 1. Ensure .env file exists and is configured
Copy-Item "docker.env.example" -Destination ".env"
# Edit .env with your actual values

# 2. Start Docker services
docker-compose up -d --build

# 3. Run initial setup
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --noinput
```

---

## 📝 **Environment File Configuration**

The `.env` file has been created with default values. **Update these before production:**

```bash
# Critical values to update:
DOMAIN=solevaeg.com                          # ✅ Already set
SECRET_KEY=your-super-secret-key-here        # ⚠️  Change for production
DB_PASSWORD=your-secure-database-password    # ⚠️  Change for production
REDIS_PASSWORD=your-redis-password           # ⚠️  Change for production
EMAIL_HOST_PASSWORD=your-email-app-password  # ⚠️  Add real email credentials
```

---

## 🔧 **Troubleshooting**

### **Docker Image Pull Issues**
If you still get "unexpected end of JSON input" errors:

```powershell
# Clean Docker system
docker system prune -f

# Reset Docker network
docker network prune -f

# Pull images individually
docker pull postgres:15-alpine
docker pull redis:7-alpine
docker pull nginx:alpine

# Try starting again
docker-compose up -d --build
```

### **Network Issues**
```powershell
# Check Docker daemon
docker version

# Restart Docker Desktop if needed
# Then try again
```

### **Permission Issues**
```powershell
# Run PowerShell as Administrator if needed
# Or use Docker Desktop interface
```

---

## 📊 **Service Status Check**

After startup, verify all services are running:

```powershell
# Check service status
docker-compose ps

# Check service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Test connectivity
curl http://localhost/api/health/
```

---

## 🌐 **Service URLs**

Once running, access your services at:

- **Frontend**: http://localhost
- **Backend API**: http://localhost/api
- **Admin Panel**: http://localhost/admin
- **Database**: localhost:5432
- **Redis**: localhost:6379

---

## 📋 **Production Deployment**

For production, use the production compose file:

```powershell
# Production deployment
docker-compose -f docker-compose.production.yml up -d --build
```

Make sure to:
1. Update `.env` with production values
2. Configure SSL certificates
3. Set up proper domain DNS
4. Configure email SMTP settings
5. Add real payment gateway keys

---

## 🎯 **Next Steps**

1. **✅ Start Services**: Use `.\docker-startup.ps1` or manual commands above
2. **✅ Run Migrations**: `docker-compose exec backend python manage.py migrate`
3. **✅ Create Admin User**: `docker-compose exec backend python manage.py createsuperuser`
4. **✅ Test Frontend**: Visit http://localhost
5. **✅ Test Backend**: Visit http://localhost/api/health/
6. **✅ Access Admin**: Visit http://localhost/admin

---

Your Docker environment is now properly configured and ready to run! 🎉
