@echo off
REM PrismQ.T.Title.From.Idea - Create Stories from Ideas
REM Loads Ideas from database and creates 10 Stories with Titles for each
REM
REM Usage:
REM   Run.bat                               Process all pending Ideas
REM   Run.bat --db path\to\database.db      Use specific database
REM   Run.bat --idea-id 123                 Process specific Idea
REM   Run.bat --limit 5                     Process max 5 Ideas
REM   Run.bat --json                        Output as JSON
REM
REM Run Preview.bat first to see what would be processed.

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
echo PrismQ.T.Title.From.Idea - Create Stories
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
    python run.py --db "%DEFAULT_DB%" %*
) else (
    python run.py %*
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Story creation failed
    pause
    exit /b 1
)

echo.
pause
