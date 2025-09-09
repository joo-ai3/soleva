
# Docker Desktop Health Check Script
# Diagnoses and attempts to fix Docker Desktop startup issues

Write-Host "🔍 Docker Desktop Health Check" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check 1: Docker CLI
Write-Host "1️⃣ Checking Docker CLI..." -ForegroundColor Blue
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker CLI: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker CLI not found or not working" -ForegroundColor Red
    Write-Host "   Please reinstall Docker Desktop" -ForegroundColor Yellow
    exit 1
}

# Check 2: Docker Daemon
Write-Host ""
Write-Host "2️⃣ Checking Docker Daemon..." -ForegroundColor Blue
try {
    $daemonInfo = docker version --format "{{.Server.Version}}" 2>$null
    if ($daemonInfo) {
        Write-Host "✅ Docker Daemon: Running (Version: $daemonInfo)" -ForegroundColor Green
        $daemonRunning = $true
    } else {
        throw "Daemon not responding"
    }
} catch {
    Write-Host "❌ Docker Daemon: Not running" -ForegroundColor Red
    $daemonRunning = $false
}

# Check 3: Docker Desktop Processes
Write-Host ""
Write-Host "3️⃣ Checking Docker Desktop Processes..." -ForegroundColor Blue
$dockerProcesses = Get-Process | Where-Object {$_.ProcessName -like "*docker*"} 
if ($dockerProcesses.Count -gt 0) {
    Write-Host "✅ Docker Desktop Processes:" -ForegroundColor Green
    $dockerProcesses | ForEach-Object { 
        Write-Host "   - $($_.ProcessName)" -ForegroundColor White 
    }
} else {
    Write-Host "❌ No Docker Desktop processes found" -ForegroundColor Red
}

# Check 4: Windows Services
Write-Host ""
Write-Host "4️⃣ Checking Docker Windows Services..." -ForegroundColor Blue
try {
    $dockerServices = Get-Service -Name "*docker*" -ErrorAction SilentlyContinue
    if ($dockerServices.Count -gt 0) {
        Write-Host "✅ Docker Services:" -ForegroundColor Green
        $dockerServices | ForEach-Object {
            $status = if ($_.Status -eq 'Running') { '🟢' } else { '🔴' }
            Write-Host "   $status $($_.Name): $($_.Status)" -ForegroundColor White
        }
    } else {
        Write-Host "⚠️  No Docker services found (normal for newer Docker Desktop)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Could not check Docker services" -ForegroundColor Yellow
}

# Check 5: WSL2 Status (if applicable)
Write-Host ""
Write-Host "5️⃣ Checking WSL2 Status..." -ForegroundColor Blue
try {
    $wslDistros = wsl --list --quiet 2>$null
    if ($wslDistros) {
        Write-Host "✅ WSL2 Distributions found:" -ForegroundColor Green
        $wslDistros | ForEach-Object { 
            if ($_.Trim()) { Write-Host "   - $($_.Trim())" -ForegroundColor White }
        }
    } else {
        Write-Host "⚠️  No WSL2 distributions found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  WSL2 not available or not configured" -ForegroundColor Yellow
}

# Summary and Recommendations
Write-Host ""
Write-Host "📋 DIAGNOSIS SUMMARY" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan

if ($daemonRunning) {
    Write-Host "🎉 Docker is working properly!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ You can now run:" -ForegroundColor Green
    Write-Host "   docker-compose up -d --build" -ForegroundColor White
    Write-Host "   OR" -ForegroundColor Gray
    Write-Host "   .\docker-recovery.ps1" -ForegroundColor White
} else {
    Write-Host "🚨 Docker Daemon is not running" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 RECOMMENDED ACTIONS:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1️⃣ RESTART DOCKER DESKTOP:" -ForegroundColor Cyan
    Write-Host "   - Close Docker Desktop completely" -ForegroundColor White
    Write-Host "   - Right-click Docker Desktop → 'Run as administrator'" -ForegroundColor White
    Write-Host "   - Or run: .\start-docker-desktop.ps1" -ForegroundColor White
    Write-Host "   - Wait 2-5 minutes for full startup" -ForegroundColor White
    Write-Host ""
    Write-Host "2️⃣ IF THAT FAILS - RESET DOCKER:" -ForegroundColor Cyan
    Write-Host "   - Open Docker Desktop Settings" -ForegroundColor White
    Write-Host "   - Go to Troubleshoot → Reset to factory defaults" -ForegroundColor White
    Write-Host "   - Restart as administrator" -ForegroundColor White
    Write-Host ""
    Write-Host "3️⃣ ALTERNATIVE - USE WSL2 DOCKER:" -ForegroundColor Cyan
    Write-Host "   - See DOCKER_DESKTOP_FIX.md for WSL2 setup" -ForegroundColor White
    Write-Host ""
    Write-Host "4️⃣ LAST RESORT:" -ForegroundColor Cyan
    Write-Host "   - Restart Windows" -ForegroundColor White
    Write-Host "   - Update Docker Desktop" -ForegroundColor White
}

Write-Host ""
Write-Host "📚 For detailed troubleshooting, see:" -ForegroundColor Blue
Write-Host "   - DOCKER_DESKTOP_FIX.md" -ForegroundColor White
Write-Host "   - DOCKER_TROUBLESHOOTING.md" -ForegroundColor White

Write-Host ""
Read-Host "Press Enter to continue"
