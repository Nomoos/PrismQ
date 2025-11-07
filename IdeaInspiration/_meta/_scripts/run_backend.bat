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

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please ensure Python 3.10+ is installed and added to PATH
    echo Download from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists and is valid
set "VENV_NEEDS_CREATION=0"
if not exist "venv" (
    set "VENV_NEEDS_CREATION=1"
) else (
    REM Check if venv Python executable exists (might be broken reference)
    if not exist "venv\Scripts\python.exe" (
        echo WARNING: Virtual environment exists but appears broken
        echo Recreating virtual environment...
        rmdir /s /q venv
        set "VENV_NEEDS_CREATION=1"
    )
)

REM Create virtual environment if needed
if "%VENV_NEEDS_CREATION%"=="1" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
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
python -c "import uvicorn" >nul 2>&1
if errorlevel 1 (
    echo WARNING: uvicorn not found in virtual environment
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        echo.
        echo If you're using Python 3.14+, some dependencies may lack prebuilt wheels.
        echo Try using Python 3.12 instead:
        echo   1. Delete the venv folder: rmdir /s /q venv
        echo   2. Create venv with Python 3.12: py -3.12 -m venv venv
        echo   3. Run this script again
        echo.
        pause
        exit /b 1
    )
    echo Dependencies installed successfully
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
REM Use uvicorn_runner to properly set Windows ProactorEventLoopPolicy
python -m src.uvicorn_runner

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
