@echo off
REM ================================================================
REM PrismQ Backend Server - Windows Startup Script
REM ================================================================
REM
REM This script ensures the server starts with the correct Windows
REM event loop policy to support subprocess operations.
REM
REM IMPORTANT: Always use this script on Windows to avoid
REM NotImplementedError when running modules.
REM ================================================================

echo ================================================================
echo PrismQ Backend Server - Windows
echo ================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo WARNING: Virtual environment not found at venv\
    echo.
    echo Create it with:
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

REM Check if requirements are installed
python -c "import uvicorn" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Dependencies not installed
    echo Run: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Start server with correct Windows configuration
echo.
echo Starting PrismQ Backend Server...
echo Server will be available at: http://localhost:8000
echo API Docs at: http://localhost:8000/docs
echo.
echo Press CTRL+C to stop the server
echo ================================================================
echo.

python -m src.uvicorn_runner

REM Only pause if server exited with error
if %ERRORLEVEL% neq 0 (
    echo.
    echo Server exited with error code %ERRORLEVEL%
    pause
)

