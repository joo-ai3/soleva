@echo off
echo 🚀 Setting up Soleva Frontend Environment...

REM Check Node.js
echo 📋 Checking Node.js version...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Node.js found
) else (
    echo ❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

REM Check npm
echo 📋 Checking npm version...
npm --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ npm found
) else (
    echo ❌ npm not found. Please ensure npm is installed with Node.js
    pause
    exit /b 1
)

REM Clean environment
echo 🧹 Cleaning environment...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json
if exist dist rmdir /s /q dist
echo ✅ Environment cleaned

REM Clear npm cache
echo 🧹 Clearing npm cache...
npm cache clean --force >nul 2>&1

REM Install dependencies
echo 📦 Installing dependencies...
npm install --no-audit --no-fund
if %errorlevel% equ 0 (
    echo ✅ Dependencies installed successfully
) else (
    echo ❌ Failed to install dependencies
    echo Trying alternative installation...
    npm install --force
    if %errorlevel% neq 0 (
        echo ❌ Installation failed. Please check your internet connection.
        pause
        exit /b 1
    )
)

echo.
echo 🎉 Setup completed!
echo.
echo Available commands:
echo   npm run dev      - Start development server
echo   npm start        - Start development server  
echo   npm run build    - Build for production
echo   npm run preview  - Preview production build
echo   npm run lint     - Run linter
echo.
echo To start development: npm run dev
pause
