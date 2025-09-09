# Start Docker Desktop Script
# Uses the confirmed installation path

Write-Host "🐳 Starting Docker Desktop..." -ForegroundColor Blue

$dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Check if Docker Desktop exists
if (-not (Test-Path $dockerPath)) {
    Write-Host "❌ Docker Desktop not found at: $dockerPath" -ForegroundColor Red
    Write-Host "Please verify Docker Desktop is installed." -ForegroundColor Yellow
    exit 1
}

# Stop any existing Docker processes
Write-Host "🛑 Stopping existing Docker processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*docker*"} | Stop-Process -Force -ErrorAction SilentlyContinue

# Wait for processes to fully terminate
Start-Sleep -Seconds 5

# Start Docker Desktop as Administrator
Write-Host "🚀 Starting Docker Desktop as Administrator..." -ForegroundColor Green
try {
    Start-Process $dockerPath -Verb RunAs
    Write-Host "✅ Docker Desktop started successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to start Docker Desktop: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Wait for Docker Desktop to initialize
Write-Host "⏳ Waiting for Docker Desktop to initialize (this may take 2-5 minutes)..." -ForegroundColor Cyan
Write-Host "   You should see a Docker whale icon in your system tray when ready." -ForegroundColor Gray

$maxWaitTime = 300  # 5 minutes
$waitTime = 0
$dockerReady = $false

while ($waitTime -lt $maxWaitTime -and -not $dockerReady) {
    Start-Sleep -Seconds 10
    $waitTime += 10
    
    try {
        $version = docker version --format "{{.Server.Version}}" 2>$null
        if ($version) {
            $dockerReady = $true
            Write-Host "✅ Docker Desktop is ready! (Server Version: $version)" -ForegroundColor Green
        } else {
            Write-Host "   Still waiting... ($waitTime/$maxWaitTime seconds)" -ForegroundColor Gray
        }
    } catch {
        Write-Host "   Still waiting... ($waitTime/$maxWaitTime seconds)" -ForegroundColor Gray
    }
}

if ($dockerReady) {
    Write-Host ""
    Write-Host "🎉 Docker Desktop is now running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 You can now run:" -ForegroundColor Cyan
    Write-Host "   docker-compose up -d --build" -ForegroundColor White
    Write-Host "   OR" -ForegroundColor Gray
    Write-Host "   .\docker-recovery.ps1" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "⚠️  Docker Desktop is taking longer than expected to start." -ForegroundColor Yellow
    Write-Host "   Please check the Docker Desktop application manually." -ForegroundColor Yellow
    Write-Host "   Look for the Docker whale icon in your system tray." -ForegroundColor Yellow
    Write-Host ""
}

Read-Host "Press Enter to continue"
