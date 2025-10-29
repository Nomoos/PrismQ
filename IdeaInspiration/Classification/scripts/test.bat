@echo off
REM Test script for PrismQ.IdeaInspiration.Classification (Windows)

echo ======================================
echo PrismQ.IdeaInspiration.Classification
echo Running Tests
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

REM Run tests
echo Running test suite...
echo.
pytest -v --cov=prismq --cov-report=html --cov-report=term

echo.
if %errorlevel% neq 0 (
    echo [ERROR] Some tests failed
) else (
    echo [OK] All tests passed!
)

echo.
echo Coverage report saved to: htmlcov/index.html
echo.
pause
