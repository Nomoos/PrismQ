@echo off
REM PrismQ Web Client - Backend Server Launcher
REM Starts the FastAPI backend server for the PrismQ Web Client

setlocal enabledelayedexpansion

REM Get repository root (2 levels up from this script)
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%..\.."
set "REPO_ROOT=%CD%"

REM Navigate to Backend directory
set "BACKEND_DIR=%REPO_ROOT%\Client\Backend"

if not exist "%BACKEND_DIR%" (
    echo ERROR: Backend directory not found at: %BACKEND_DIR%
    echo Please ensure you are running this script from the PrismQ.IdeaInspiration repository.
    pause
    exit /b 1
)

echo ========================================
echo PrismQ Web Client - Backend Server
echo ========================================
echo.
echo Repository: %REPO_ROOT%
echo Backend:    %BACKEND_DIR%
echo.

cd /d "%BACKEND_DIR%"

REM Check if virtual environment exists
if not exist "venv" (
    echo WARNING: Virtual environment not found!
    echo.
    echo Please create a virtual environment first:
    echo   cd Client\Backend
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Check if uvicorn is installed
where uvicorn >nul 2>&1
if errorlevel 1 (
    echo WARNING: uvicorn not found in virtual environment
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting Backend server...
echo Server will run on: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start the server with auto-reload for development
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

REM If uvicorn exits, pause to see any error messages
if errorlevel 1 (
    echo.
    echo ========================================
    echo Server stopped with error
    echo ========================================
    pause
    exit /b 1
)

endlocal
