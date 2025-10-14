@echo off
REM PrismQ Module Sync Script (Windows)
REM This script sets up Python environment and runs the sync_modules.py script

setlocal enabledelayedexpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"
set "PYTHON_SCRIPT=%SCRIPT_DIR%sync_modules.py"

REM Check if we're in a git repository
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo Error: Not in a git repository
    exit /b 1
)

REM Check if virtual environment exists
if not exist "%VENV_DIR%" (
    echo Python virtual environment not found
    echo Setting up environment for the first time...
    echo.
    call "%SCRIPT_DIR%setup_env.bat"
    if errorlevel 1 (
        echo Error: Failed to setup Python environment
        exit /b 1
    )
    echo.
)

REM Activate virtual environment
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    echo Please run: %SCRIPT_DIR%setup_env.bat
    exit /b 1
)

REM Run the Python script with all arguments passed to this batch file
python "%PYTHON_SCRIPT%" %*
set PYTHON_EXIT_CODE=!errorlevel!

REM Deactivate virtual environment
call deactivate
