@echo off
REM PrismQ.T.Title.From.Idea - Preview Mode
REM Shows what Ideas would be processed without making changes
REM
REM Usage:
REM   Preview.bat                           Show all pending Ideas
REM   Preview.bat --db path\to\database.db  Use specific database
REM   Preview.bat --idea-id 123             Preview specific Idea
REM   Preview.bat --limit 5                 Preview max 5 Ideas
REM   Preview.bat --json                    Output as JSON
REM
REM This script does NOT create any Stories - it only shows what would be done.
REM Run Run.bat to actually create Stories.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Setup Python virtual environment
call "%SCRIPT_DIR%setup_env.bat"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to setup Python environment
    pause
    exit /b 1
)

echo ========================================
echo PrismQ.T.Title.From.Idea - PREVIEW MODE
echo ========================================

REM Default database path (relative to script)
set DEFAULT_DB=%SCRIPT_DIR%..\..\..\..\..\..\prismq.db

REM Check if --db is specified, otherwise use default
set HAS_DB=0
for %%a in (%*) do (
    if "%%a"=="--db" set HAS_DB=1
    if "%%a"=="-d" set HAS_DB=1
)

if "%HAS_DB%"=="0" (
    python run.py --db "%DEFAULT_DB%" --preview %*
) else (
    python run.py --preview %*
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Preview failed
    pause
    exit /b 1
)

echo.
pause
