# Quick Production Deployment for Soleva
# This script creates a deployment package and provides instructions

Write-Host "=== QUICK SOLEVA PRODUCTION DEPLOYMENT ===" -ForegroundColor Green

# Create deployment directory
$deployDir = "production-deploy"
if (Test-Path $deployDir) { Remove-Item -Recurse -Force $deployDir }
New-Item -ItemType Directory -Path $deployDir | Out-Null

Write-Host "Creating deployment package..." -ForegroundColor Yellow

# Copy essential files
Copy-Item -Recurse "soleva back end" "$deployDir/"
Copy-Item -Recurse "soleva front end" "$deployDir/"
Copy-Item -Recurse "nginx" "$deployDir/"
Copy-Item "docker-compose.yml" "$deployDir/"
Copy-Item "docker.env" "$deployDir/"

# Ensure HTTP-only configuration is active
Copy-Item "nginx/conf.d/soleva-temp-http.conf" "$deployDir/nginx/conf.d/soleva.conf" -Force

# Create server deployment script
$serverScript = @'
#!/bin/bash
echo "🚀 Deploying Soleva to production server..."

# Install Docker if needed
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
fi

# Install Docker Compose if needed
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Stop existing containers
docker-compose down --remove-orphans 2>/dev/null || true

# Start new deployment
docker-compose up -d

# Configure firewall
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable 2>/dev/null || echo "UFW not available"

echo "✅ Deployment complete!"
echo "🌐 Site available at: http://solevaeg.com"
docker-compose ps
'@

$serverScript | Out-File -FilePath "$deployDir/deploy.sh" -Encoding UTF8

# Create archive
Compress-Archive -Path "$deployDir/*" -DestinationPath "soleva-production.zip" -Force

Write-Host "✅ Deployment package created: soleva-production.zip" -ForegroundColor Green

Write-Host "`n=== DEPLOYMENT INSTRUCTIONS ===" -ForegroundColor Cyan
Write-Host "1. Upload to your server:" -ForegroundColor Yellow
Write-Host "   scp soleva-production.zip root@213.130.147.41:/opt/" -ForegroundColor White
Write-Host ""
Write-Host "2. Connect to server and deploy:" -ForegroundColor Yellow
Write-Host "   ssh root@213.130.147.41" -ForegroundColor White
Write-Host "   cd /opt" -ForegroundColor White
Write-Host "   unzip -o soleva-production.zip" -ForegroundColor White
Write-Host "   chmod +x deploy.sh" -ForegroundColor White
Write-Host "   ./deploy.sh" -ForegroundColor White
Write-Host ""
Write-Host "3. Test the website:" -ForegroundColor Yellow
Write-Host "   http://solevaeg.com" -ForegroundColor White
Write-Host ""

Write-Host "=== ALTERNATIVE: Docker Hub Deployment ===" -ForegroundColor Cyan
Write-Host "If you have Docker Hub access, you can also:" -ForegroundColor Yellow
Write-Host "1. Build and push images to Docker Hub" -ForegroundColor White
Write-Host "2. Pull and run on production server" -ForegroundColor White

# Cleanup
Remove-Item -Recurse -Force $deployDir

Write-Host "`n🚀 Ready to deploy! Follow the instructions above." -ForegroundColor Green
