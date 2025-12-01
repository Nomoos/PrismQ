@echo off
REM setup_env.bat - Setup Python Virtual Environment for PrismQ.T.Script.From.Title.Review.Script

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set MODULE_DIR=%SCRIPT_DIR%..\..\..\T\Script\From\Title\Review\Script
set VENV_DIR=%MODULE_DIR%\.venv
set REQUIREMENTS=%MODULE_DIR%\requirements.txt
set ENV_FILE=%MODULE_DIR%\.env
set VENV_MARKER=%VENV_DIR%\pyvenv.cfg

echo.
echo ========================================
echo PrismQ - Python Environment Setup
echo ========================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    exit /b 1
)

for /f "delims=" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Python version: %PYTHON_VERSION%

if exist "%VENV_MARKER%" (
    echo [INFO] Virtual environment found: %VENV_DIR%
    goto :activate_venv
)

echo [INFO] Creating virtual environment at: %VENV_DIR%
python -m venv "%VENV_DIR%"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create virtual environment
    exit /b 1
)
echo [SUCCESS] Virtual environment created

:activate_venv
echo [INFO] Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to activate virtual environment
    exit /b 1
)

for /f "delims=" %%i in ('where python') do (
    set PYTHON_PATH=%%i
    goto :show_path
)
:show_path
echo [INFO] Using Python: %PYTHON_PATH%

set NEEDS_INSTALL=0
if not exist "%VENV_DIR%\.requirements_installed" (
    set NEEDS_INSTALL=1
)

if "%NEEDS_INSTALL%"=="1" (
    if exist "%REQUIREMENTS%" (
        echo [INFO] Installing dependencies...
        pip install -r "%REQUIREMENTS%" --quiet
        if %ERRORLEVEL% NEQ 0 (
            echo ERROR: Failed to install dependencies
            exit /b 1
        )
        echo Installed on %DATE% %TIME% > "%VENV_DIR%\.requirements_installed"
        echo [SUCCESS] Dependencies installed
    ) else (
        echo [INFO] No requirements.txt found
        echo Installed on %DATE% %TIME% > "%VENV_DIR%\.requirements_installed"
    )
) else (
    echo [INFO] Dependencies already installed
)

if not exist "%ENV_FILE%" (
    echo [INFO] Creating .env file at: %ENV_FILE%
    echo # PrismQ.T.Script.From.Title.Review.Script Environment Configuration > "%ENV_FILE%"
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
echo ========================================
echo.

endlocal & (
    set "PRISMQ_VENV=%VENV_DIR%"
    set "PRISMQ_PYTHON=%PYTHON_PATH%"
    call "%VENV_DIR%\Scripts\activate.bat"
)
exit /b 0
