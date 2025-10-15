@echo off
REM PrismQ Add Module Script (Windows)
REM This script sets up Python environment and runs the add_module.py script

setlocal enabledelayedexpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%add_module\.venv"
set "PYTHON_SCRIPT=%SCRIPT_DIR%add_module.py"

REM Check if we're in a git repository and get the root directory
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo Error: Not in a git repository
    echo Please run this script from the root of the PrismQ repository
    exit /b 1
)

REM Change to repository root to ensure correct relative paths
for /f "delims=" %%i in ('git rev-parse --show-toplevel') do set repo_root=%%i
REM Convert forward slashes to backslashes for Windows
set repo_root=!repo_root:/=\!
cd /d "!repo_root!"
if errorlevel 1 (
    echo Error: Failed to change to repository root
    exit /b 1
)

REM Check if virtual environment exists
if not exist "%VENV_DIR%" (
    echo Python virtual environment not found
    echo Setting up environment for the first time...
    echo.
    call "%SCRIPT_DIR%add_module\setup_env.bat"
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
    echo Please run: %SCRIPT_DIR%add_module\setup_env.bat
    exit /b 1
)

REM Run the Python script with all arguments passed to this batch file
python "%PYTHON_SCRIPT%" %*
set PYTHON_EXIT_CODE=!errorlevel!

REM Deactivate virtual environment
call deactivate

exit /b !PYTHON_EXIT_CODE!
