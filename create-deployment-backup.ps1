#!/usr/bin/env powershell
# Soleva Website - Pre-Deployment Backup Script
# Creates comprehensive backup of database, code, and configurations

param(
    [switch]$Help,
    [string]$BackupPath = ".\backups\pre-deployment-$(Get-Date -Format 'yyyy-MM-dd-HH-mm-ss')"
)

if ($Help) {
    Write-Host "Soleva Pre-Deployment Backup Script" -ForegroundColor Green
    Write-Host "Usage: .\create-deployment-backup.ps1 [-BackupPath <path>]" -ForegroundColor White
    Write-Host ""
    Write-Host "Parameters:" -ForegroundColor Yellow
    Write-Host "  -BackupPath    Custom backup directory path" -ForegroundColor White
    Write-Host "  -Help          Show this help message" -ForegroundColor White
    exit 0
}

function Write-Status($Message) {
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning($Message) {
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error($Message) {
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Create backup directory
Write-Status "Creating backup directory: $BackupPath"
New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null

# 1. Backup Project Files
Write-Status "Backing up project files..."
$ProjectBackupPath = Join-Path $BackupPath "project-files"
New-Item -ItemType Directory -Path $ProjectBackupPath -Force | Out-Null

# Copy essential project files
$FilesToBackup = @(
    "docker-compose.yml",
    "docker.env",
    "nginx",
    "soleva back end",
    "soleva front end",
    "scripts",
    "README.md",
    "DEPLOYMENT_GUIDE.md",
    "FINAL_DEPLOYMENT_CHECKLIST.md"
)

foreach ($file in $FilesToBackup) {
    if (Test-Path $file) {
        Write-Status "Backing up: $file"
        if (Test-Path $file -PathType Container) {
            Copy-Item -Path $file -Destination $ProjectBackupPath -Recurse -Force
        } else {
            Copy-Item -Path $file -Destination $ProjectBackupPath -Force
        }
    } else {
        Write-Warning "File not found: $file"
    }
}

# 2. Backup Configuration Files
Write-Status "Backing up configuration files..."
$ConfigBackupPath = Join-Path $BackupPath "configurations"
New-Item -ItemType Directory -Path $ConfigBackupPath -Force | Out-Null

# Copy configuration files
$ConfigFiles = @(
    "docker.env",
    "nginx/nginx.conf",
    "nginx/conf.d/soleva.conf",
    "soleva back end/soleva_backend/settings.py",
    "soleva back end/requirements.txt",
    "soleva front end/package.json",
    "soleva front end/vite.config.ts"
)

foreach ($config in $ConfigFiles) {
    if (Test-Path $config) {
        $destPath = Join-Path $ConfigBackupPath (Split-Path $config -Leaf)
        Copy-Item -Path $config -Destination $destPath -Force
        Write-Status "Backed up config: $config"
    }
}

# 3. Create Database Backup Script
Write-Status "Creating database backup script..."
$DbBackupScript = @"
#!/bin/bash
# Database Backup Script for Soleva
# Run this script after deployment to backup the database

echo "Creating PostgreSQL database backup..."
docker-compose exec -T postgres pg_dump -U soleva_user soleva_db > "$BackupPath/database-backup.sql"

if [ `$? -eq 0 ]; then
    echo "Database backup created successfully: $BackupPath/database-backup.sql"
else
    echo "Database backup failed!"
    exit 1
fi

# Create compressed backup
gzip "$BackupPath/database-backup.sql"
echo "Database backup compressed: $BackupPath/database-backup.sql.gz"
"@

$DbBackupScript | Out-File -FilePath (Join-Path $BackupPath "backup-database.sh") -Encoding UTF8
Write-Status "Database backup script created"

# 4. Create Environment Variables Backup
Write-Status "Backing up environment variables..."
if (Test-Path "docker.env") {
    # Create sanitized version (remove sensitive data)
    $envContent = Get-Content "docker.env"
    $sanitizedEnv = @()
    
    foreach ($line in $envContent) {
        if ($line -match "PASSWORD|SECRET|KEY" -and -not ($line -match "^#")) {
            $parts = $line -split "=", 2
            if ($parts.Length -eq 2) {
                $sanitizedEnv += "$($parts[0])=***REDACTED***"
            } else {
                $sanitizedEnv += $line
            }
        } else {
            $sanitizedEnv += $line
        }
    }
    
    $sanitizedEnv | Out-File -FilePath (Join-Path $BackupPath "docker.env.template") -Encoding UTF8
    Write-Status "Environment template created (sensitive data redacted)"
    
    # Also create full backup (for recovery purposes)
    Copy-Item -Path "docker.env" -Destination (Join-Path $BackupPath "docker.env.backup") -Force
    Write-Status "Full environment backup created"
}

# 5. Create Recovery Instructions
Write-Status "Creating recovery instructions..."
$RecoveryInstructions = @"
# Soleva Website - Recovery Instructions

## Backup Information
- **Created**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- **Backup Path**: $BackupPath
- **Project Version**: 1.0.0

## Recovery Steps

### 1. Project Files Recovery
To restore project files:
``````
# Copy project files back to deployment directory
cp -r project-files/* /var/www/soleva/
``````

### 2. Database Recovery
To restore database:
``````
# Stop services
docker-compose down

# Start only database
docker-compose up -d postgres

# Restore database
gunzip -c database-backup.sql.gz | docker-compose exec -T postgres psql -U soleva_user -d soleva_db

# Start all services
docker-compose up -d
``````

### 3. Configuration Recovery
To restore configurations:
``````
# Copy configuration files
cp configurations/docker.env ../docker.env
cp configurations/soleva.conf ../nginx/conf.d/soleva.conf
# ... restore other configs as needed
``````

### 4. SSL Certificates
SSL certificates will be regenerated automatically by certbot.
If needed, run:
``````
docker-compose run --rm certbot
``````

## Verification
After recovery, verify:
1. Website loads: https://solevaeg.com
2. Admin panel works: https://solevaeg.com/admin/
3. Database connectivity
4. All services running: docker-compose ps

## Contact
For support, contact the development team.
"@

$RecoveryInstructions | Out-File -FilePath (Join-Path $BackupPath "RECOVERY_INSTRUCTIONS.md") -Encoding UTF8

# 6. Create Backup Manifest
Write-Status "Creating backup manifest..."
$Manifest = @{
    "backup_date" = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    "backup_path" = $BackupPath
    "project_version" = "1.0.0"
    "domain" = "solevaeg.com"
    "admin_email" = "admin@solevaeg.com"
    "files_backed_up" = $FilesToBackup
    "configurations_backed_up" = $ConfigFiles
    "database_backup_script" = "backup-database.sh"
    "recovery_instructions" = "RECOVERY_INSTRUCTIONS.md"
}

$Manifest | ConvertTo-Json -Depth 3 | Out-File -FilePath (Join-Path $BackupPath "backup-manifest.json") -Encoding UTF8

# 7. Create Verification Script
Write-Status "Creating verification script..."
$VerificationScript = @"
#!/bin/bash
# Backup Verification Script

echo "Verifying Soleva backup..."

# Check backup directory
if [ ! -d "$BackupPath" ]; then
    echo "ERROR: Backup directory not found!"
    exit 1
fi

# Check essential files
essential_files=(
    "backup-manifest.json"
    "RECOVERY_INSTRUCTIONS.md"
    "backup-database.sh"
    "docker.env.backup"
    "project-files/docker-compose.yml"
    "project-files/docker.env"
)

for file in "`${essential_files[@]}"; do
    if [ ! -f "$BackupPath/`$file" ]; then
        echo "ERROR: Missing essential file: `$file"
        exit 1
    fi
done

echo "Backup verification completed successfully!"
echo "Backup location: $BackupPath"
echo "All essential files are present."
"@

$VerificationScript | Out-File -FilePath (Join-Path $BackupPath "verify-backup.sh") -Encoding UTF8

# 8. Calculate backup size
Write-Status "Calculating backup size..."
$BackupSize = (Get-ChildItem -Path $BackupPath -Recurse | Measure-Object -Property Length -Sum).Sum
$BackupSizeMB = [math]::Round($BackupSize / 1MB, 2)

# Final Summary
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "BACKUP COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
Write-Host "Backup Details:" -ForegroundColor Yellow
Write-Host "  Location: $BackupPath" -ForegroundColor White
Write-Host "  Size: $BackupSizeMB MB" -ForegroundColor White
Write-Host "  Created: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
Write-Host ""
Write-Host "Backup Contents:" -ForegroundColor Yellow
Write-Host "  - Project files and source code" -ForegroundColor White
Write-Host "  - Configuration files" -ForegroundColor White
Write-Host "  - Environment variables (full + template)" -ForegroundColor White
Write-Host "  - Database backup script" -ForegroundColor White
Write-Host "  - Recovery instructions" -ForegroundColor White
Write-Host "  - Verification script" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Run database backup after deployment:" -ForegroundColor White
Write-Host "     bash $BackupPath/backup-database.sh" -ForegroundColor Cyan
Write-Host "  2. Verify backup integrity:" -ForegroundColor White
Write-Host "     bash $BackupPath/verify-backup.sh" -ForegroundColor Cyan
Write-Host "  3. Store backup in secure location" -ForegroundColor White
Write-Host ""
Write-Host "The Soleva website is ready for deployment!" -ForegroundColor Green
