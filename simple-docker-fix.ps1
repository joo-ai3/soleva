# Simple Docker Registry Fix
Write-Host "Configuring Docker registry mirrors..." -ForegroundColor Green

# Create Docker daemon configuration
$dockerConfigPath = "$env:USERPROFILE\.docker\daemon.json"
$dockerDir = Split-Path $dockerConfigPath

if (!(Test-Path $dockerDir)) {
    New-Item -ItemType Directory -Path $dockerDir -Force
}

$config = @"
{
  "registry-mirrors": [
    "https://registry.docker-cn.com",
    "https://dockerhub.azk8s.cn"
  ],
  "dns": ["8.8.8.8", "1.1.1.1"]
}
"@

$config | Set-Content $dockerConfigPath
Write-Host "Docker configuration created at: $dockerConfigPath" -ForegroundColor Green
Write-Host "Please restart Docker Desktop and try again." -ForegroundColor Yellow
