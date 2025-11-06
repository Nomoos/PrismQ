@echo off
REM Quickstart script for PrismQ.IdeaInspiration.Classification (Windows)

echo ======================================
echo PrismQ.IdeaInspiration.Classification
echo Quickstart - Running Example
echo ======================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo [ERROR] Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

REM Run example
echo Running classification example...
echo.
python _meta/examples/example.py

echo.
echo ======================================
echo Example completed!
echo ======================================
echo.
pause
