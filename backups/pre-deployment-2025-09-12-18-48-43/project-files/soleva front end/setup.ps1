# Soleva Frontend Setup Script
Write-Host "🚀 Setting up Soleva Frontend Environment..." -ForegroundColor Green

# Check Node.js version
Write-Host "📋 Checking Node.js version..." -ForegroundColor Yellow
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check npm version
Write-Host "📋 Checking npm version..." -ForegroundColor Yellow
$npmVersion = npm --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ npm version: $npmVersion" -ForegroundColor Green
} else {
    Write-Host "❌ npm not found. Please ensure npm is installed with Node.js" -ForegroundColor Red
    exit 1
}

# Clean environment
Write-Host "🧹 Cleaning environment..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Remove-Item -Recurse -Force "node_modules" -ErrorAction SilentlyContinue
    Write-Host "✅ Removed node_modules" -ForegroundColor Green
}

if (Test-Path "package-lock.json") {
    Remove-Item "package-lock.json" -ErrorAction SilentlyContinue
    Write-Host "✅ Removed package-lock.json" -ForegroundColor Green
}

if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue
    Write-Host "✅ Removed dist folder" -ForegroundColor Green
}

# Clear npm cache
Write-Host "🧹 Clearing npm cache..." -ForegroundColor Yellow
npm cache clean --force 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ npm cache cleared" -ForegroundColor Green
} else {
    Write-Host "⚠️ Could not clear npm cache, continuing..." -ForegroundColor Yellow
}

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
npm install --no-audit --no-fund --legacy-peer-deps
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Write-Host "Trying alternative installation..." -ForegroundColor Yellow
    npm install --force
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Installation failed. Please check your internet connection and try again." -ForegroundColor Red
        exit 1
    }
}

# Verify installation
Write-Host "🔍 Verifying installation..." -ForegroundColor Yellow

# Test scripts
Write-Host "🧪 Testing npm scripts..." -ForegroundColor Yellow

Write-Host "Testing 'npm run build'..." -ForegroundColor Cyan
npm run build 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build successful" -ForegroundColor Green
} else {
    Write-Host "❌ Build failed" -ForegroundColor Red
}

Write-Host "Testing 'npm run lint'..." -ForegroundColor Cyan
npm run lint 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Lint successful" -ForegroundColor Green
} else {
    Write-Host "⚠️ Lint has warnings (this is normal)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "  npm run dev      - Start development server" -ForegroundColor White
Write-Host "  npm start        - Start development server" -ForegroundColor White
Write-Host "  npm run build    - Build for production" -ForegroundColor White
Write-Host "  npm run preview  - Preview production build" -ForegroundColor White
Write-Host "  npm run lint     - Run linter" -ForegroundColor White
Write-Host ""
Write-Host "To start development: npm run dev" -ForegroundColor Green
