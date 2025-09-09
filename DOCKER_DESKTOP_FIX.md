# 🐳 Docker Desktop Fix Guide

## 🚨 **Current Issue: "Docker Desktop is unable to start"**

You're experiencing a common Windows Docker Desktop startup issue. The `docker --version` command works (showing Docker CLI is installed), but the Docker daemon/engine isn't running.

---

## 🔧 **Step-by-Step Solution**

### **Step 1: Complete Docker Desktop Restart**

1. **Close Docker Desktop completely:**
   - Right-click Docker Desktop system tray icon → "Quit Docker Desktop"
   - Or use Task Manager to end all Docker processes:
     - `Docker Desktop.exe`
     - `com.docker.backend.exe`
     - `com.docker.cli.exe`

2. **Wait 30 seconds** for all processes to fully terminate

3. **Restart as Administrator:**
   - Right-click Docker Desktop icon → "Run as administrator"
   - **This is crucial for Windows Docker Desktop**

4. **Wait for full initialization:**
   - Watch for the green "Docker Desktop is running" status
   - This can take 2-5 minutes on first startup

### **Step 2: Verify Docker is Working**

```powershell
# Test Docker daemon
docker version

# Test image pulling
docker pull hello-world

# Test container running
docker run hello-world
```

If these work, proceed to Step 3. If not, continue to troubleshooting.

### **Step 3: Start Soleva**

Once Docker is confirmed working:

```powershell
# Use the recovery script
.\docker-recovery.ps1

# Or manual startup
docker-compose up -d --build
```

---

## 🛠️ **Advanced Troubleshooting**

### **Option A: Docker Desktop Reset**

If the above doesn't work:

1. **Open Docker Desktop**
2. **Go to Settings (gear icon)**
3. **Navigate to "Troubleshoot" tab**
4. **Click "Reset to factory defaults"**
5. **Confirm and wait for reset**
6. **Restart Docker Desktop as Administrator**

### **Option B: Windows Services Check**

Check if Docker services are running:

```powershell
# Run PowerShell as Administrator
Get-Service -Name "*docker*" | Format-Table -AutoSize

# Start Docker services if needed
Start-Service -Name "com.docker.service"
```

### **Option C: WSL2 Backend Check**

Docker Desktop on Windows uses WSL2. Verify it's working:

```powershell
# Check WSL2 status
wsl --list --verbose

# Update WSL2 if needed
wsl --update

# Restart WSL2
wsl --shutdown
```

### **Option D: Hyper-V Check**

Ensure Windows features are enabled:

1. **Open "Turn Windows features on or off"**
2. **Ensure these are checked:**
   - ✅ Hyper-V
   - ✅ Windows Subsystem for Linux
   - ✅ Virtual Machine Platform
3. **Restart Windows if changes were made**

---

## 🚀 **Alternative: Docker without Docker Desktop**

If Docker Desktop continues to have issues, you can use Docker Engine directly:

### **Install Docker Engine on WSL2**

```bash
# In WSL2 Ubuntu terminal
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Start Docker service
sudo service docker start

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

Then run your project from WSL2:
```bash
cd /mnt/e/البراند/web/fall\ satk\ soleva/
docker-compose up -d --build
```

---

## 📊 **Diagnostic Commands**

Run these to diagnose Docker Desktop issues:

```powershell
# Check Docker Desktop processes
Get-Process | Where-Object {$_.ProcessName -like "*docker*"} | Format-Table

# Check Docker Desktop logs
# Logs are typically in: %APPDATA%\Docker\log\

# Check Windows Event Logs for Docker errors
Get-WinEvent -FilterHashtable @{LogName='Application'; ProviderName='Docker Desktop'} -MaxEvents 10
```

---

## 🎯 **Expected Success Indicators**

When Docker Desktop is working properly, you should see:

1. **Green Docker Desktop icon** in system tray
2. **"Docker Desktop is running"** tooltip
3. **Successful output** from `docker version`
4. **Successful output** from `docker pull hello-world`

---

## 📞 **If All Else Fails**

1. **Restart Windows** (often resolves Windows service conflicts)
2. **Update Docker Desktop** to the latest version
3. **Check antivirus software** (sometimes blocks Docker)
4. **Free up disk space** (Docker needs space for images/containers)
5. **Consider using Docker in WSL2 directly** (more reliable on some systems)

---

## 🚨 **Quick Emergency Solution**

If you need to get Soleva running immediately:

1. **Install WSL2 Ubuntu**
2. **Install Docker in WSL2** (as shown above)
3. **Run Soleva from WSL2 terminal**
4. **Access via http://localhost** (same as before)

This bypasses Docker Desktop entirely and is often more stable on Windows.

---

**💡 Pro Tip:** Many developers prefer running Docker in WSL2 directly rather than using Docker Desktop, especially for development work. It's faster and more reliable!
