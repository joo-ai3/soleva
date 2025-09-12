# Soleva Production Server Deployment Script
# This script deploys the Soleva application to the production server at 213.130.147.41

param(
    [string]$ServerIP = "213.130.147.41",
    [string]$Username = "root",  # Change this to your server username
    [string]$KeyPath = "",       # Path to your SSH private key (optional)
    [switch]$HTTPOnly = $false   # Deploy with HTTP-only configuration first
)

Write-Host "=== SOLEVA PRODUCTION DEPLOYMENT ===" -ForegroundColor Green
Write-Host "Target Server: $ServerIP" -ForegroundColor Cyan

# Check if we have SSH access
Write-Host "Step 1: Checking server connectivity..." -ForegroundColor Yellow

try {
    # Test basic connectivity
    Test-NetConnection -ComputerName $ServerIP -Port 22 -ErrorAction Stop
    Write-Host "✅ Server is reachable on SSH port 22" -ForegroundColor Green
} catch {
    Write-Host "❌ Cannot reach server at $ServerIP on port 22" -ForegroundColor Red
    Write-Host "Please ensure:" -ForegroundColor Yellow
    Write-Host "1. The server is running and accessible" -ForegroundColor Yellow
    Write-Host "2. SSH is enabled on the server" -ForegroundColor Yellow
    Write-Host "3. Firewall allows SSH connections" -ForegroundColor Yellow
    exit 1
}

# Create deployment package
Write-Host "Step 2: Creating deployment package..." -ForegroundColor Yellow

$deployDir = "deployment-package"
$timestamp = Get-Date -Format "yyyy-MM-dd-HH-mm-ss"

# Remove old deployment package if exists
if (Test-Path $deployDir) {
    Remove-Item -Recurse -Force $deployDir
}

# Create new deployment directory
New-Item -ItemType Directory -Path $deployDir | Out-Null

# Copy necessary files
Write-Host "Copying project files..." -ForegroundColor Cyan
Copy-Item -Recurse "soleva back end" "$deployDir/"
Copy-Item -Recurse "soleva front end" "$deployDir/"
Copy-Item -Recurse "nginx" "$deployDir/"
Copy-Item "docker-compose.yml" "$deployDir/"
Copy-Item "docker.env" "$deployDir/"

# Create HTTP-only configuration if requested
if ($HTTPOnly) {
    Write-Host "Creating HTTP-only configuration..." -ForegroundColor Cyan
    
    # Use the temporary HTTP configuration we created
    Copy-Item "nginx/conf.d/soleva-temp-http.conf" "$deployDir/nginx/conf.d/soleva.conf" -Force
    
    # Update environment for HTTP
    $envContent = Get-Content "$deployDir/docker.env"
    $envContent = $envContent -replace "VITE_API_BASE_URL=https://solevaeg.com/api", "VITE_API_BASE_URL=http://solevaeg.com/api"
    $envContent | Set-Content "$deployDir/docker.env"
}

# Create deployment script for the server
$serverDeployScript = @"
#!/bin/bash
echo "🚀 Starting Soleva deployment on production server..."

# Update system packages
apt update && apt upgrade -y

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    usermod -aG docker `$USER
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Navigate to project directory
cd /opt/soleva

# Stop existing containers
docker-compose down --remove-orphans 2>/dev/null || true

# Remove old containers and images
docker container prune -f
docker image prune -f

# Start new deployment
echo "Starting containers..."
docker-compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 30

# Check container status
echo "Container status:"
docker-compose ps

# Configure firewall
echo "Configuring firewall..."
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo "✅ Deployment completed!"
echo "🌐 Site should be available at: http://solevaeg.com"

# Show container logs
echo "Recent logs:"
docker-compose logs --tail=20
"@

$serverDeployScript | Out-File -FilePath "$deployDir/deploy-server.sh" -Encoding UTF8

# Create archive
Write-Host "Creating deployment archive..." -ForegroundColor Cyan
Compress-Archive -Path "$deployDir/*" -DestinationPath "soleva-deployment-$timestamp.zip" -Force

Write-Host "Step 3: Deployment package created: soleva-deployment-$timestamp.zip" -ForegroundColor Green

# Instructions for manual deployment
Write-Host "`n=== DEPLOYMENT INSTRUCTIONS ===" -ForegroundColor Green
Write-Host "1. Upload the deployment package to your server:" -ForegroundColor Yellow
Write-Host "   scp soleva-deployment-$timestamp.zip $Username@$ServerIP:/tmp/" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Connect to your server:" -ForegroundColor Yellow
Write-Host "   ssh $Username@$ServerIP" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Extract and deploy:" -ForegroundColor Yellow
Write-Host "   cd /tmp" -ForegroundColor Cyan
Write-Host "   unzip soleva-deployment-$timestamp.zip" -ForegroundColor Cyan
Write-Host "   mkdir -p /opt/soleva" -ForegroundColor Cyan
Write-Host "   cp -r deployment-package/* /opt/soleva/" -ForegroundColor Cyan
Write-Host "   cd /opt/soleva" -ForegroundColor Cyan
Write-Host "   chmod +x deploy-server.sh" -ForegroundColor Cyan
Write-Host "   ./deploy-server.sh" -ForegroundColor Cyan
Write-Host ""

# Automated deployment option
Write-Host "=== AUTOMATED DEPLOYMENT OPTION ===" -ForegroundColor Green
Write-Host "If you have SSH key access, we can deploy automatically." -ForegroundColor Yellow
$automate = Read-Host "Do you want to attempt automated deployment? (y/N)"

if ($automate -eq "y" -or $automate -eq "Y") {
    Write-Host "Step 4: Uploading to production server..." -ForegroundColor Yellow
    
    try {
        # Upload deployment package
        if ($KeyPath) {
            & scp -i $KeyPath "soleva-deployment-$timestamp.zip" "$Username@$ServerIP:/tmp/"
        } else {
            & scp "soleva-deployment-$timestamp.zip" "$Username@$ServerIP:/tmp/"
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Upload successful!" -ForegroundColor Green
            
            Write-Host "Step 5: Running deployment on server..." -ForegroundColor Yellow
            
            # Execute deployment on server
            $deployCommands = @(
                "cd /tmp",
                "unzip -o soleva-deployment-$timestamp.zip",
                "mkdir -p /opt/soleva",
                "cp -r deployment-package/* /opt/soleva/",
                "cd /opt/soleva",
                "chmod +x deploy-server.sh",
                "./deploy-server.sh"
            )
            
            $deployScript = $deployCommands -join "; "
            
            if ($KeyPath) {
                & ssh -i $KeyPath "$Username@$ServerIP" $deployScript
            } else {
                & ssh "$Username@$ServerIP" $deployScript
            }
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "🎉 DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
                Write-Host "Your site should now be available at: http://solevaeg.com" -ForegroundColor Cyan
                
                # Test the deployment
                Write-Host "Step 6: Testing deployment..." -ForegroundColor Yellow
                Start-Sleep -Seconds 10
                
                try {
                    $response = Invoke-WebRequest -Uri "http://solevaeg.com" -TimeoutSec 15 -UseBasicParsing
                    Write-Host "✅ Website is accessible! Status: $($response.StatusCode)" -ForegroundColor Green
                } catch {
                    Write-Host "⚠️ Website test failed, but deployment may still be successful." -ForegroundColor Yellow
                    Write-Host "Please check manually: http://solevaeg.com" -ForegroundColor Cyan
                }
            } else {
                Write-Host "❌ Deployment failed on server" -ForegroundColor Red
            }
        } else {
            Write-Host "❌ Upload failed" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Automated deployment failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Please use manual deployment instructions above." -ForegroundColor Yellow
    }
}

# Cleanup
Write-Host "Step 7: Cleaning up..." -ForegroundColor Yellow
Remove-Item -Recurse -Force $deployDir -ErrorAction SilentlyContinue

Write-Host "`n=== DEPLOYMENT SCRIPT COMPLETE ===" -ForegroundColor Green
Write-Host "If the automated deployment didn't work, follow the manual instructions above." -ForegroundColor Yellow
