# Repository Cleanup Script for Soleva Project
# This script helps clean up files that should be ignored after .gitignore update

Write-Host "🧹 Soleva Repository Cleanup" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green

# Check if we're in a git repository
if (!(Test-Path ".git")) {
    Write-Host "❌ Not in a git repository. Please run this from the project root." -ForegroundColor Red
    exit 1
}

Write-Host "📋 Checking for files that should be ignored..." -ForegroundColor Yellow

# Files that should definitely not be in the repository
$sensitiveFiles = @(
    "docker.env",
    ".env",
    ".env.local",
    ".env.production",
    "soleva back end/logs/",
    "nginx/logs/",
    "ssl/certbot/",
    "letsencrypt/",
    "*.log",
    "deployment-status.json"
)

$foundSensitiveFiles = @()

foreach ($pattern in $sensitiveFiles) {
    $files = git ls-files $pattern 2>$null
    if ($files) {
        $foundSensitiveFiles += $files
        Write-Host "⚠️  Found tracked sensitive file(s): $files" -ForegroundColor Yellow
    }
}

if ($foundSensitiveFiles.Count -eq 0) {
    Write-Host "✅ No sensitive files found in repository" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "🚨 SENSITIVE FILES DETECTED IN REPOSITORY" -ForegroundColor Red
    Write-Host "The following files should be removed from git tracking:" -ForegroundColor Yellow
    
    foreach ($file in $foundSensitiveFiles) {
        Write-Host "   - $file" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: These files contain sensitive information!" -ForegroundColor Yellow
    Write-Host "They should be removed from git history to prevent security issues." -ForegroundColor Yellow
    
    $response = Read-Host "Do you want to remove these files from git tracking? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Host ""
        Write-Host "🗑️  Removing sensitive files from git tracking..." -ForegroundColor Yellow
        
        foreach ($file in $foundSensitiveFiles) {
            try {
                git rm --cached $file
                Write-Host "✅ Removed $file from git tracking" -ForegroundColor Green
            } catch {
                Write-Host "❌ Failed to remove $file" -ForegroundColor Red
            }
        }
        
        Write-Host ""
        Write-Host "📝 Files removed from tracking. You should now commit these changes:" -ForegroundColor Cyan
        Write-Host "   git add .gitignore" -ForegroundColor White
        Write-Host "   git commit -m 'Update .gitignore and remove sensitive files'" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "🔍 Checking current git status..." -ForegroundColor Yellow
git status --short

Write-Host ""
Write-Host "📊 Repository Statistics:" -ForegroundColor Cyan
$trackedFiles = (git ls-files | Measure-Object).Count
$gitignoreLines = (Get-Content ".gitignore" | Measure-Object -Line).Lines
Write-Host "   Tracked files: $trackedFiles" -ForegroundColor White
Write-Host "   .gitignore rules: $gitignoreLines" -ForegroundColor White

Write-Host ""
Write-Host "✅ Repository cleanup completed!" -ForegroundColor Green

Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Review the git status above" -ForegroundColor White
Write-Host "2. Add and commit the .gitignore changes" -ForegroundColor White
Write-Host "3. Ensure team members pull the latest .gitignore" -ForegroundColor White
Write-Host "4. Consider cleaning git history if sensitive data was committed" -ForegroundColor White

Write-Host ""
Write-Host "🔒 Security Reminder:" -ForegroundColor Yellow
Write-Host "Always double-check that sensitive files (docker.env, .env, SSL certs)" -ForegroundColor Yellow
Write-Host "are never committed to the repository!" -ForegroundColor Yellow
