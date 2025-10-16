@echo off
REM PrismQ Submodule Converter - Python Environment Setup Script
REM Sets up Python virtual environment for the submodule-converter script

setlocal enabledelayedexpansion

echo.
echo ========================================================
echo      PrismQ Submodule Converter - Environment Setup
echo ========================================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    exit /b 1
)

REM Display Python version
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Found: %PYTHON_VERSION%

REM Check if virtual environment already exists
if exist "%VENV_DIR%" (
    echo.
    echo Virtual environment already exists at: %VENV_DIR%
    set /p RECREATE="Do you want to recreate it? (y/n): "
    if /i not "!RECREATE!"=="y" (
        echo Using existing virtual environment
        goto :activate_env
    )
    echo Removing existing virtual environment...
    rmdir /s /q "%VENV_DIR%"
)

REM Create virtual environment
echo.
echo Creating Python virtual environment...
python -m venv "%VENV_DIR%"
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    exit /b 1
)
echo Virtual environment created successfully

:activate_env
REM Activate virtual environment and install dependencies
echo.
echo Installing Python dependencies...
call "%VENV_DIR%\Scripts\activate.bat"

REM Upgrade pip
python -m pip install --upgrade pip >nul 2>&1

REM Install dependencies from requirements.txt if it exists
if exist "%SCRIPT_DIR%requirements.txt" (
    pip install -r "%SCRIPT_DIR%requirements.txt"
    if errorlevel 1 (
        echo Warning: Some dependencies failed to install
        echo You may need to install them manually
    ) else (
        echo All dependencies installed successfully
    )
) else (
    echo Note: requirements.txt not found
    echo No external dependencies to install
)

echo.
echo ========================================================
echo Setup complete!
echo ========================================================
echo.
echo Virtual environment location: %VENV_DIR%
echo.
echo To activate the environment manually, run:
echo   %VENV_DIR%\Scripts\activate.bat
echo.
echo To deactivate, run:
echo   deactivate
echo.

REM Keep the environment activated for the current session
endlocal
