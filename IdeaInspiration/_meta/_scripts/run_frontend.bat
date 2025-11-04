@echo off
REM PrismQ Web Client - Frontend Launcher
REM Starts the Vue 3 frontend development server

setlocal enabledelayedexpansion

REM Get repository root (2 levels up from this script)
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%..\.."
set "REPO_ROOT=%CD%"

REM Navigate to Frontend directory
set "FRONTEND_DIR=%REPO_ROOT%\Client\Frontend"

if not exist "%FRONTEND_DIR%" (
    echo ERROR: Frontend directory not found at: %FRONTEND_DIR%
    echo Please ensure you are running this script from the PrismQ.IdeaInspiration repository.
    pause
    exit /b 1
)

echo ========================================
echo PrismQ Web Client - Frontend
echo ========================================
echo.
echo Repository: %REPO_ROOT%
echo Frontend:   %FRONTEND_DIR%
echo.

cd /d "%FRONTEND_DIR%"

REM Check if Node.js is installed
where node >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    echo.
    echo Please install Node.js 18 or higher from:
    echo   https://nodejs.org/
    echo.
    echo Or see the installation guide at:
    echo   %REPO_ROOT%\Client\docs\NODEJS_INSTALLATION.md
    echo.
    pause
    exit /b 1
)

REM Check Node.js version
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo Node.js version: %NODE_VERSION%

REM Check if npm is installed
where npm >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm is not installed!
    echo Please install Node.js which includes npm.
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "node_modules" (
    echo WARNING: node_modules not found!
    echo Installing dependencies...
    echo.
    call npm install
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting Frontend development server...
echo Server will run on: http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start the development server
call npm run dev

REM If npm exits, pause to see any error messages
if errorlevel 1 (
    echo.
    echo ========================================
    echo Server stopped with error
    echo ========================================
    pause
    exit /b 1
)

endlocal
