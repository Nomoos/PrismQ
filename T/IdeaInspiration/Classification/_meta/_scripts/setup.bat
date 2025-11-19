@echo off
REM Setup script for PrismQ.IdeaInspiration.Classification (Windows)

echo ======================================
echo PrismQ.IdeaInspiration.Classification
echo Setup Script
echo ======================================
echo.

REM Check Python version
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [1/5] Checking Python version...
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.8 or higher is required
    pause
    exit /b 1
)
echo [OK] Python version is compatible

echo.
echo [2/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

echo.
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated

echo.
echo [4/5] Installing package and dependencies...
pip install -e ".[dev]" --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install package
    pause
    exit /b 1
)
echo [OK] Package installed

echo.
echo [5/5] Running tests...
pytest -q
if %errorlevel% neq 0 (
    echo [WARNING] Some tests failed, but setup completed
) else (
    echo [OK] All tests passed
)

echo.
echo ======================================
echo Setup completed successfully!
echo ======================================
echo.
echo To activate the environment in the future, run:
echo   venv\Scripts\activate.bat
echo.
echo To run the example:
echo   python _meta/examples/example.py
echo.
echo To run tests:
echo   pytest
echo.
pause
