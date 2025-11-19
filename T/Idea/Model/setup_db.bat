@echo off
REM Batch setup script for Idea database (Windows)

echo ==========================================
echo PrismQ.Idea.Model - Database Setup
echo ==========================================
echo.

cd /d "%~dp0"

echo Current directory: %CD%
echo.

REM Check for Python
set PYTHON_CMD=
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    py -3.10 --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=py -3.10
        echo Using Python Launcher: py -3.10
    )
)

if "%PYTHON_CMD%"=="" (
    where python3.10 >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set PYTHON_CMD=python3.10
    ) else (
        where python >nul 2>&1
        if %ERRORLEVEL% EQU 0 (
            set PYTHON_CMD=python
        )
    )
)

if "%PYTHON_CMD%"=="" (
    echo Error: Python not found!
    echo Please install Python 3.10.x from https://www.python.org/downloads/
    exit /b 1
)

echo Using: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

echo Setting up Idea database...

%PYTHON_CMD% -c "import sys; sys.path.insert(0, '.'); from src.idea_db import setup_database; db = setup_database('idea.db'); print('Database created: idea.db'); print('Tables created: ideas, idea_inspirations'); db.close(); print('Setup complete!')"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==========================================
    echo Database setup successful!
    echo Database file: idea.db
    echo ==========================================
) else (
    echo.
    echo Error: Database setup failed!
    exit /b 1
)
