# Fix Docker Registry Connectivity Issues
Write-Host "=== Docker Registry Connectivity Fix ===" -ForegroundColor Green

# Option 1: Try using Docker Hub mirror
Write-Host "Testing alternative Docker registries..." -ForegroundColor Yellow

# Test connectivity to different registries
$registries = @(
    "registry-1.docker.io",
    "index.docker.io", 
    "registry.docker-cn.com",
    "dockerhub.azk8s.cn"
)

foreach ($registry in $registries) {
    Write-Host "Testing $registry..." -ForegroundColor Cyan
    $result = Test-NetConnection -ComputerName $registry -Port 443 -InformationLevel Quiet
    if ($result) {
        Write-Host "✓ $registry is accessible" -ForegroundColor Green
    } else {
        Write-Host "✗ $registry is not accessible" -ForegroundColor Red
    }
}

# Option 2: Configure Docker daemon with registry mirrors
Write-Host "`nConfiguring Docker daemon..." -ForegroundColor Yellow

$dockerConfigPath = "$env:USERPROFILE\.docker\daemon.json"
$dockerConfig = @{
    "registry-mirrors" = @(
        "https://registry.docker-cn.com",
        "https://dockerhub.azk8s.cn",
        "https://docker.mirrors.ustc.edu.cn"
    )
    "insecure-registries" = @()
    "dns" = @("8.8.8.8", "1.1.1.1")
}

# Create .docker directory if it doesn't exist
$dockerDir = Split-Path $dockerConfigPath
if (!(Test-Path $dockerDir)) {
    New-Item -ItemType Directory -Path $dockerDir -Force
}

# Write configuration
$dockerConfig | ConvertTo-Json -Depth 3 | Set-Content $dockerConfigPath
Write-Host "Docker daemon configuration updated at: $dockerConfigPath" -ForegroundColor Green

Write-Host "`nRestart Docker Desktop for changes to take effect." -ForegroundColor Yellow
Write-Host "Then try: docker compose up -d" -ForegroundColor Cyan
