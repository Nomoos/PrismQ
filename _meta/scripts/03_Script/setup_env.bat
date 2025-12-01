@echo off
REM setup_env.bat - Setup Python Virtual Environment for PrismQ.T.Script.From.Idea.Title
REM This script creates and activates a virtual environment for the module
REM
REM Virtual environment location: T\Script\From\Idea\Title\.venv
REM Dependencies: T\Script\From\Idea\Title\requirements.txt
REM
REM This script is designed to be called from other batch scripts

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set MODULE_DIR=%SCRIPT_DIR%..\..\..\T\Script\From\Idea\Title
set VENV_DIR=%MODULE_DIR%\.venv
set REQUIREMENTS=%MODULE_DIR%\requirements.txt
set ENV_FILE=%MODULE_DIR%\.env
set VENV_MARKER=%VENV_DIR%\pyvenv.cfg

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

REM Check if virtual environment exists
if exist "%VENV_MARKER%" (
    echo [INFO] Virtual environment found: %VENV_DIR%
    echo [INFO] Using existing virtual environment
    goto :activate_venv
)

REM Create virtual environment
echo [INFO] Virtual environment not found
echo [INFO] Creating virtual environment at: %VENV_DIR%
echo.
python -m venv "%VENV_DIR%"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create virtual environment
    echo.
    echo Please ensure you have the 'venv' module installed.
    exit /b 1
)
echo [SUCCESS] Virtual environment created

:activate_venv
REM Activate virtual environment
echo [INFO] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to activate virtual environment
    exit /b 1
)

REM Show activated Python path
for /f "delims=" %%i in ('where python') do (
    set PYTHON_PATH=%%i
    goto :show_path
)
:show_path
echo [INFO] Using Python: %PYTHON_PATH%

REM Check if requirements need to be installed
set NEEDS_INSTALL=0
if not exist "%VENV_DIR%\.requirements_installed" (
    set NEEDS_INSTALL=1
)

if "%NEEDS_INSTALL%"=="1" (
    if exist "%REQUIREMENTS%" (
        echo [INFO] Installing dependencies from requirements.txt...
        pip install -r "%REQUIREMENTS%" --quiet
        if %ERRORLEVEL% NEQ 0 (
            echo ERROR: Failed to install dependencies
            exit /b 1
        )
        echo Installed on %DATE% %TIME% > "%VENV_DIR%\.requirements_installed"
        echo [SUCCESS] Dependencies installed
    ) else (
        echo [INFO] No requirements.txt found, skipping dependency installation
        echo Installed on %DATE% %TIME% > "%VENV_DIR%\.requirements_installed"
    )
) else (
    echo [INFO] Dependencies already installed
)

REM Create .env file if it doesn't exist
if not exist "%ENV_FILE%" (
    echo [INFO] Creating .env file at: %ENV_FILE%
    echo # PrismQ.T.Script.From.Idea.Title Environment Configuration > "%ENV_FILE%"
    echo # Created automatically on first run >> "%ENV_FILE%"
    echo. >> "%ENV_FILE%"
    echo # Working directory ^(auto-detected^) >> "%ENV_FILE%"
    echo # WORKING_DIRECTORY= >> "%ENV_FILE%"
    echo. >> "%ENV_FILE%"
    echo # Database configuration >> "%ENV_FILE%"
    echo # DATABASE_URL=sqlite:///db.s3db >> "%ENV_FILE%"
    echo. >> "%ENV_FILE%"
    echo [SUCCESS] .env file created
) else (
    echo [INFO] .env file exists: %ENV_FILE%
)

echo.
echo ========================================
echo Environment Setup Complete
echo ========================================
echo   Virtual Environment: %VENV_DIR%
echo   Python: %PYTHON_PATH%
echo   Requirements: %REQUIREMENTS%
echo   Config: %ENV_FILE%
echo ========================================
echo.

endlocal & (
    set "PRISMQ_VENV=%VENV_DIR%"
    set "PRISMQ_PYTHON=%PYTHON_PATH%"
    call "%VENV_DIR%\Scripts\activate.bat"
)
exit /b 0
