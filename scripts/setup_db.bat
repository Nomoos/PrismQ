@echo off
REM Database Setup Script for PrismQ Model Repositories
REM This script sets up the database in the nearest PrismQ directory
REM Use this file if your repository is a Model type

setlocal enabledelayedexpansion

echo =====================================
echo PrismQ Database Setup
echo =====================================
echo.

REM Get the script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%\.."

REM Set default Python executable
set "PYTHON_EXEC=python"

REM Use Python to set up configuration and get working directory
echo [INFO] Setting up configuration...
for /f "delims=" %%i in ('%PYTHON_EXEC% -c "import sys; sys.path.insert(0, 'src'); from config import Config; config = Config(interactive=True); print(config.working_directory)"') do set "USER_WORK_DIR=%%i"

if errorlevel 1 (
    echo [ERROR] Failed to set up configuration.
    echo [ERROR] Please install Python 3.14 or higher and try again.
    pause
    exit /b 1
)

REM Get Python executable from environment
for /f "delims=" %%i in ('%PYTHON_EXEC% -c "import os; print(os.getenv('PYTHON_EXECUTABLE', 'python'))"') do set "PYTHON_EXEC=%%i"

echo [INFO] Using Python: %PYTHON_EXEC%
%PYTHON_EXEC% --version
echo.

echo [INFO] Working directory: %USER_WORK_DIR%
echo.

REM Create the database path
set "DB_PATH=%USER_WORK_DIR%\db.s3db"
echo [INFO] Database will be created at: %DB_PATH%
echo.

REM Check if database already exists
if exist "%DB_PATH%" (
    echo [WARNING] Database file already exists: %DB_PATH%
    set /p "OVERWRITE=Do you want to recreate it? (Y/N): "
    if /i not "!OVERWRITE!"=="Y" (
        echo [INFO] Keeping existing database.
        echo [INFO] Setup completed.
        pause
        exit /b 0
    )
    echo [INFO] Removing existing database...
    del "%DB_PATH%"
)

REM Create database using Python
echo [INFO] Creating database...
%PYTHON_EXEC% -c "import sqlite3; import sys; sys.path.insert(0, 'src'); conn = sqlite3.connect('%DB_PATH%'); print('[SUCCESS] Database created successfully'); conn.close()"

if errorlevel 1 (
    echo [ERROR] Failed to create database.
    pause
    exit /b 1
)

echo.
echo =====================================
echo Setup completed successfully!
echo =====================================
echo.
echo Database location: %DB_PATH%
echo Working directory: %USER_WORK_DIR%
echo.
echo You can now use this database with your PrismQ module.
echo.

pause
