@echo off
REM Auto-Build and Package Script for Frontend/TaskManager (Windows)
REM Run this script before deployment to create a ready-to-upload package
REM
REM Usage:
REM   build-and-package.bat
REM   build-and-package.bat clean  (rebuild from scratch)

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set FRONTEND_DIR=%SCRIPT_DIR%
set DEPLOY_PACKAGE_DIR=%SCRIPT_DIR%deploy-package
set TIMESTAMP=%date:~-4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

echo ========================================
echo Frontend/TaskManager Auto-Build ^& Package
echo ========================================
echo Build Date: %date% %time%
echo Working Directory: %FRONTEND_DIR%
echo.

REM Check if we're in the right directory
if not exist "%FRONTEND_DIR%package.json" (
    echo [ERROR] package.json not found. Are you in Frontend/TaskManager directory?
    exit /b 1
)

REM Parse arguments
set CLEAN_BUILD=false
if "%1"=="clean" set CLEAN_BUILD=true

REM Step 1: Clean if requested
if "%CLEAN_BUILD%"=="true" (
    echo [STEP] Cleaning previous build...
    if exist node_modules rmdir /s /q node_modules
    if exist dist rmdir /s /q dist
    if exist deploy-package rmdir /s /q deploy-package
    echo [OK] Clean complete
)

REM Step 2: Install dependencies
echo.
echo [STEP] Installing dependencies...
if not exist "node_modules" (
    call npm install --legacy-peer-deps
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [INFO] Dependencies already installed (use 'clean' to reinstall)
)

REM Step 3: Build production bundle
echo.
echo [STEP] Building production bundle...
call npm run build
if errorlevel 1 (
    echo [ERROR] Build failed
    exit /b 1
)
echo [OK] Build complete

REM Step 4: Create deployment package
echo.
echo [STEP] Creating deployment package...

REM Remove old package
if exist "%DEPLOY_PACKAGE_DIR%" rmdir /s /q "%DEPLOY_PACKAGE_DIR%"
mkdir "%DEPLOY_PACKAGE_DIR%"

REM Copy built files
xcopy /E /I /Q dist\* "%DEPLOY_PACKAGE_DIR%\" > nul
echo [INFO] Copied dist/ files

REM Copy deployment scripts
copy /Y deploy.php "%DEPLOY_PACKAGE_DIR%\" > nul
copy /Y deploy-auto.php "%DEPLOY_PACKAGE_DIR%\" > nul
copy /Y public\deploy-deploy.php "%DEPLOY_PACKAGE_DIR%\" > nul
copy /Y public\.htaccess.example "%DEPLOY_PACKAGE_DIR%\" > nul
echo [INFO] Copied deployment scripts

REM Create .htaccess from example
if exist "%DEPLOY_PACKAGE_DIR%\.htaccess.example" (
    copy /Y "%DEPLOY_PACKAGE_DIR%\.htaccess.example" "%DEPLOY_PACKAGE_DIR%\.htaccess" > nul
    echo [INFO] Created .htaccess from example
)

REM Step 5: Create README for deployment
echo Frontend/TaskManager - Deployment Package > "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo ========================================== >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo. >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo Build Date: %date% %time% >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo Build Script: build-and-package.bat >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo. >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo Package Contents: >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo ----------------- >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo - assets/          : Production build files (JS, CSS, images) >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo - index.html       : Main application entry point >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo - deploy.php       : Deployment wizard (open in browser) >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo - deploy-auto.php  : Automated deployment script (CLI) >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo - .htaccess        : Apache SPA routing configuration >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo. >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo Deployment Options: >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo ------------------- >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo. >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo OPTION 1: Upload via FTP/SFTP (Recommended for Vedos/Wedos) >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo 1. Upload entire contents of this directory to your web root >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo 2. Open https://your-domain.com/deploy.php in browser >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo 3. Follow the deployment wizard >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo. >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo OPTION 2: Manual Setup >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo 1. Upload all files to your web root >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo 2. Ensure .htaccess is in place (for SPA routing) >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo 3. Open your domain in browser >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo. >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo Requirements: >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo ------------- >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo - Web server with PHP 7.4+ (for deployment scripts only) >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo - Apache with mod_rewrite (or equivalent for SPA routing) >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo - Backend/TaskManager API running and accessible >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"
echo. >> "%DEPLOY_PACKAGE_DIR%\README_DEPLOYMENT.txt"

echo [OK] Created deployment README

REM Step 6: Create ZIP archive
echo.
echo [STEP] Creating ZIP archive...
set ZIP_FILE=deploy-package-%TIMESTAMP%.zip
powershell -Command "Compress-Archive -Path '%DEPLOY_PACKAGE_DIR%\*' -DestinationPath '%ZIP_FILE%' -Force"
if errorlevel 1 (
    echo [WARNING] Failed to create ZIP archive (PowerShell required)
) else (
    echo [OK] Created %ZIP_FILE%
)

REM Summary
echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo [SUCCESS] Deployment Package Ready!
echo.
echo Package Location:
echo   Directory: %DEPLOY_PACKAGE_DIR%
if exist "%ZIP_FILE%" echo   Archive:   %ZIP_FILE%
echo.
echo Next Steps:
echo   1. Upload deploy-package\ to your web server via FTP/FileZilla
echo   2. Open deploy.php in browser to complete setup
echo.
echo Quick Commands:
echo   View contents:    dir /b "%DEPLOY_PACKAGE_DIR%"
echo   Open folder:      explorer "%DEPLOY_PACKAGE_DIR%"
echo.
echo [SUCCESS] All done!
echo.

endlocal
pause
