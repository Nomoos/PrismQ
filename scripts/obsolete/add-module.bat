@echo off
REM PrismQ Add Module Script (Windows)
REM This script sets up Python environment and runs the add_module CLI

setlocal enabledelayedexpansion

echo.
echo ========================================================
echo         PrismQ Module Creation Script
echo ========================================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%add_module\.venv"

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

REM Check GitHub CLI authentication
echo Checking GitHub CLI authentication...
gh auth status >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: GitHub CLI is not authenticated
    echo You need to authenticate with GitHub to create repositories
    echo.
    set /p "AUTH_CHOICE=Do you want to authenticate now? (y/n): "
    if /i "!AUTH_CHOICE!"=="y" (
        echo.
        echo Running GitHub CLI authentication...
        gh auth login
        if errorlevel 1 (
            echo.
            echo Error: GitHub authentication failed
            echo Please run 'gh auth login' manually and try again
            exit /b 1
        )
        echo.
        echo GitHub authentication successful!
        echo.
    ) else (
        echo.
        echo Continuing without authentication...
        echo Note: Repository creation will fail without authentication
        echo.
    )
) else (
    echo GitHub CLI is authenticated
    echo.
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

REM Get user input for module (URL or module name)
if "%~1"=="" (
    echo You can provide either:
    echo   1. Module name in dot-notation: PrismQ.MyModule
    echo   2. GitHub URL: https://github.com/Nomoos/PrismQ.MyModule
    echo.
    set /p "MODULE_INPUT=Enter module name or GitHub URL: "
) else (
    set "MODULE_INPUT=%~1"
)

REM Run the new CLI with the module input
python -m scripts.add_module.add_module "!MODULE_INPUT!"
set PYTHON_EXIT_CODE=!errorlevel!

REM Deactivate virtual environment
call deactivate

exit /b !PYTHON_EXIT_CODE!
