@echo off
REM PrismQ.IdeaInspiration.Model - Database Setup Script
REM This script creates db.s3db in the user's working directory and sets up the IdeaInspiration table
REM Target: Windows with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

setlocal enabledelayedexpansion

echo ============================================================
echo PrismQ.IdeaInspiration.Model - Database Setup
echo ============================================================
echo.

REM Store the repository root (where this script is located)
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Set default Python executable
set "PYTHON_EXEC=python"

REM Use Python to set up configuration and get working directory
echo [INFO] Setting up configuration...
for /f "delims=" %%i in ('%PYTHON_EXEC% -c "from config_manager import setup_working_directory; config = setup_working_directory('PrismQ.IdeaInspiration.Model'); print(str(config.working_dir))"') do set "USER_WORK_DIR=%%i"

if errorlevel 1 (
    echo [ERROR] Failed to set up configuration.
    echo [ERROR] Please install Python 3.8 or higher and try again.
    pause
    exit /b 1
)

REM Get Python executable from config
for /f "delims=" %%i in ('%PYTHON_EXEC% -c "from config_manager import ConfigManager; config = ConfigManager('%USER_WORK_DIR%'); python_exec = config.get('PYTHON_EXECUTABLE', 'python'); print(python_exec)"') do set "PYTHON_EXEC=%%i"

echo [INFO] Using Python: %PYTHON_EXEC%
%PYTHON_EXEC% --version
echo.

echo [INFO] Working directory: %USER_WORK_DIR%
echo.

REM Create the database path
set "DB_PATH=%USER_WORK_DIR%\db.s3db"
echo [INFO] Database will be created at: %DB_PATH%
echo.

REM Create Python script to set up the database
echo [INFO] Creating database and IdeaInspiration table...
%PYTHON_EXEC% -c "import sqlite3; import sys; db_path = r'%DB_PATH%'; conn = sqlite3.connect(db_path); cursor = conn.cursor(); cursor.execute('''CREATE TABLE IF NOT EXISTS IdeaInspiration (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT, content TEXT, keywords TEXT, source_type TEXT, metadata TEXT, source_id TEXT, source_url TEXT, source_created_by TEXT, source_created_at TEXT, score INTEGER, category TEXT, subcategory_relevance TEXT, contextual_category_scores TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)'''); conn.commit(); conn.close(); print('[SUCCESS] Database and IdeaInspiration table created successfully!')"

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to create database or table.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Database Location: %DB_PATH%
echo Table Created: IdeaInspiration
echo.
echo Table Schema:
echo   - id: INTEGER PRIMARY KEY AUTOINCREMENT
echo   - title: TEXT NOT NULL
echo   - description: TEXT
echo   - content: TEXT
echo   - keywords: TEXT (JSON array)
echo   - source_type: TEXT (text/video/audio/unknown)
echo   - metadata: TEXT (JSON object with string key-value pairs)
echo   - source_id: TEXT
echo   - source_url: TEXT
echo   - source_created_by: TEXT
echo   - source_created_at: TEXT
echo   - score: INTEGER
echo   - category: TEXT
echo   - subcategory_relevance: TEXT (JSON object with int values)
echo   - contextual_category_scores: TEXT (JSON object with int values)
echo   - created_at: TIMESTAMP
echo   - updated_at: TIMESTAMP
echo.
echo You can now use this database with PrismQ modules.
echo.
pause
