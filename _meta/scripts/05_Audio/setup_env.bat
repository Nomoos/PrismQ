@echo off
REM setup_env.bat - Setup Python Virtual Environment for PrismQ Audio Modules
REM This script provides environment setup for Audio modules
REM
REM This script is designed to be called from other batch scripts

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0

echo.
echo ========================================
echo PrismQ - Python Environment Setup
echo ========================================
echo.

REM Check Python availability
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo and ensure it is added to your PATH.
    exit /b 1
)

REM Show Python version
for /f "delims=" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Python version: %PYTHON_VERSION%

echo.
echo [INFO] Audio module environment ready
echo.

endlocal
exit /b 0
