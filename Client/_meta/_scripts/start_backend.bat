@echo off
REM PrismQ Web Client Backend - Windows Startup Script
REM Primary Platform: Windows 10/11

echo ========================================
echo PrismQ Web Client Backend
echo Starting on Windows...
echo ========================================
echo.

REM Navigate to Backend directory
cd /d "%~dp0..\..\Backend"

echo Current directory: %CD%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Display Python version
echo Python version:
python --version
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo WARNING: Virtual environment not found at Backend\venv
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated
echo.

REM Check if uvicorn is installed
python -c "import uvicorn" 2>nul
if errorlevel 1 (
    echo WARNING: uvicorn is not installed
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo Dependencies installed successfully
    echo.
)

REM Check if src/main.py exists
if not exist "src\main.py" (
    echo ERROR: src\main.py not found
    echo Please ensure you are running this script from the correct location
    pause
    exit /b 1
)

echo ========================================
echo Starting Backend Server...
echo ========================================
echo.
echo Server will run on http://127.0.0.1:8000
echo API docs available at http://127.0.0.1:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run uvicorn with Windows subprocess support
python -m src.uvicorn_runner

REM If we get here, the server has stopped
echo.
echo Server stopped
pause
