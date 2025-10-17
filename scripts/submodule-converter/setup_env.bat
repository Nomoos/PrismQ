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
    
    REM Validate if venv is still functional
    echo Validating virtual environment...
    
    REM Check if Python executable exists in venv
    if not exist "%VENV_DIR%\Scripts\python.exe" (
        echo Virtual environment is invalid (missing Python executable^)
        echo Recreating virtual environment...
        rmdir /s /q "%VENV_DIR%"
        goto :create_venv
    )
    
    REM Try to run Python in the venv to check if it works
    "%VENV_DIR%\Scripts\python.exe" --version >nul 2>&1
    if errorlevel 1 (
        echo Virtual environment is broken (Python not working^)
        echo Recreating virtual environment...
        rmdir /s /q "%VENV_DIR%"
        goto :create_venv
    )
    
    REM Check if venv Python version matches system Python
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set SYSTEM_PY_VER=%%i
    for /f "tokens=2" %%i in ('"%VENV_DIR%\Scripts\python.exe" --version 2^>^&1') do set VENV_PY_VER=%%i
    
    if not "%SYSTEM_PY_VER%"=="%VENV_PY_VER%" (
        echo Virtual environment Python version mismatch
        echo System: %SYSTEM_PY_VER%, Venv: %VENV_PY_VER%
        echo Recreating virtual environment...
        rmdir /s /q "%VENV_DIR%"
        goto :create_venv
    )
    
    echo Virtual environment is valid
    set /p RECREATE="Do you want to recreate it anyway? (y/n): "
    if /i not "!RECREATE!"=="y" (
        echo Using existing virtual environment
        goto :activate_env
    )
    echo Removing existing virtual environment...
    rmdir /s /q "%VENV_DIR%"
)

:create_venv

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
