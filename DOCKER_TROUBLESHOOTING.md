# 🚨 Docker Troubleshooting Guide

## **Current Issue: `fallsatksoleva-celery-beat` Image Error**

The error you're seeing indicates Docker is trying to pull a custom image that doesn't exist. This happens when Docker Compose has cached references to previously built images.

---

## 🔧 **Step-by-Step Solution**

### **Step 1: Start Docker Desktop**
The error shows "Docker Desktop is unable to start". First:

1. **Close Docker Desktop completely**
2. **Restart Docker Desktop as Administrator**
3. **Wait for Docker Desktop to fully initialize** (green status)
4. **Test Docker is working**: `docker version`

### **Step 2: Clean Docker Environment**
Once Docker Desktop is running:

```powershell
# Remove all containers, images, and build cache
docker system prune -a -f --volumes

# Remove any orphaned containers
docker-compose down --volumes --remove-orphans

# Remove custom networks (if any)
docker network prune -f
```

### **Step 3: Fresh Start with Correct Configuration**
```powershell
# Use the startup script (recommended)
.\docker-startup.ps1

# OR manual startup
docker-compose up -d --build --force-recreate
```

---

## 🛠️ **Alternative: Docker Desktop Reset**

If the above doesn't work, reset Docker Desktop:

1. **Open Docker Desktop**
2. **Go to Settings → Troubleshoot**
3. **Click "Reset to factory defaults"**
4. **Restart Docker Desktop**
5. **Try starting Soleva again**

---

## 🔍 **Root Cause Analysis**

The error `unable to get image 'fallsatksoleva-celery-beat'` suggests:

1. **Project name issue**: Docker Compose is using the folder name with spaces/special characters
2. **Cached build references**: Previous builds are cached with incorrect names
3. **Docker Desktop state**: Docker daemon might be in an inconsistent state

---

## ✅ **Prevention for Future**

### **Set Explicit Project Name**
Add this to your docker-compose files:

```yaml
# At the top of docker-compose.yml
name: soleva

services:
  # ... rest of your services
```

### **Use Consistent Commands**
Always use these commands for clean builds:

```powershell
# Stop everything cleanly
docker-compose down

# Start with fresh build
docker-compose up -d --build

# Or use the startup script
.\docker-startup.ps1
```

---

## 🚀 **Quick Recovery Script**

I'll create a recovery script for you:

```powershell
# Save as docker-recovery.ps1
Write-Host "🔧 Docker Recovery Script" -ForegroundColor Yellow

# Check Docker Desktop
Write-Host "Checking Docker Desktop..." -ForegroundColor Blue
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Start Docker Desktop first, then run this script again" -ForegroundColor Red
    exit 1
}

# Clean everything
Write-Host "🧹 Cleaning Docker environment..." -ForegroundColor Blue
docker-compose down --volumes --remove-orphans 2>$null
docker system prune -a -f --volumes

# Fresh start
Write-Host "🚀 Starting fresh..." -ForegroundColor Blue
docker-compose up -d --build --force-recreate

Write-Host "✅ Recovery complete!" -ForegroundColor Green
```

---

## 📞 **If Problems Persist**

1. **Restart Windows** (sometimes helps with Docker Desktop issues)
2. **Update Docker Desktop** to the latest version
3. **Check Windows features**: Ensure WSL2 and Hyper-V are enabled
4. **Try running PowerShell as Administrator**

---

## 🎯 **Expected Result**

After following these steps, you should see:
- All services starting successfully
- No image pull errors
- Services accessible at http://localhost

Let me know if you need help with any of these steps!
