@echo off
REM PrismQ Web Client - Full Stack Launcher
REM Starts both Backend and Frontend servers in separate windows

setlocal enabledelayedexpansion

REM Get repository root (2 levels up from this script)
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%..\.."
set "REPO_ROOT=%CD%"

REM Define script paths
set "BACKEND_SCRIPT=%REPO_ROOT%\_meta\_scripts\run_backend.bat"
set "FRONTEND_SCRIPT=%REPO_ROOT%\_meta\_scripts\run_frontend.bat"

echo ========================================
echo PrismQ Web Client - Full Stack Launcher
echo ========================================
echo.
echo This will start both Backend and Frontend servers
echo in separate console windows.
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Close both console windows to stop the servers.
echo ========================================
echo.

REM Check if scripts exist
if not exist "%BACKEND_SCRIPT%" (
    echo ERROR: Backend script not found at: %BACKEND_SCRIPT%
    pause
    exit /b 1
)

if not exist "%FRONTEND_SCRIPT%" (
    echo ERROR: Frontend script not found at: %FRONTEND_SCRIPT%
    pause
    exit /b 1
)

echo Starting Backend server in new window...
start "PrismQ Backend Server" cmd /k "%BACKEND_SCRIPT%"

REM Wait a moment to ensure Backend starts first
timeout /t 3 /nobreak >nul

echo Starting Frontend server in new window...
start "PrismQ Frontend Server" cmd /k "%FRONTEND_SCRIPT%"

echo.
echo ========================================
echo Both servers are starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000 (API Documentation: /docs)
echo Frontend: http://localhost:5173
echo.
echo Two new console windows have been opened.
echo Close them to stop the servers.
echo.
echo Waiting for servers to start...
echo ========================================

REM Wait for servers to fully start (Frontend typically takes 5-10 seconds)
echo.
echo Opening browser in 10 seconds...
timeout /t 10 /nobreak

REM Open the Frontend in the default browser
echo Opening http://localhost:5173 in your default browser...
start http://localhost:5173

echo.
echo ========================================
echo All done!
echo ========================================
echo.
echo Browser should now be open at http://localhost:5173
echo The two server console windows are still running.
echo Close them when you're done to stop the servers.
echo.
echo This window will now close.
echo ========================================

REM Wait a moment for user to read the message
timeout /t 5 /nobreak

endlocal
