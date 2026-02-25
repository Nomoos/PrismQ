@echo off
REM Batch setup script for Idea database (Windows)

echo ==========================================
echo PrismQ.Idea.Model - Database Setup
echo ==========================================
echo.

cd /d "%~dp0"

echo Current directory: %CD%
echo.

REM Find project Python (install if needed - installs to <repo_root>\.python\)
set "PYTHON_CMD="
call "%~dp0..\..\..\_meta\scripts\common\find_python.bat"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Could not find or install Python.
    exit /b 1
)
set "PYTHON_CMD=%PYTHON_EXE%"

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
