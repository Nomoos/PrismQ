@echo off
REM PrismQ.T.Title.From.Idea.Preview.bat - Preview Title Generation from Database Ideas
REM This script runs in preview mode WITHOUT saving to database
REM Shows what Ideas would be processed and titles that would be created
REM
REM Usage:
REM   PrismQ.T.Title.From.Idea.Preview.bat
REM   PrismQ.T.Title.From.Idea.Preview.bat --idea-id 123    Preview specific Idea
REM   PrismQ.T.Title.From.Idea.Preview.bat --limit 5        Preview max 5 Ideas
REM   PrismQ.T.Title.From.Idea.Preview.bat --json           Output as JSON
REM
REM Features:
REM   - Picks ideas from database that don't have stories yet
REM   - Generates title previews (does NOT save to database)
REM   - Shows what would be created without making changes

set SCRIPT_DIR=%~dp0
set MODULE_SCRIPT_DIR=%SCRIPT_DIR%..\..\..\T\Title\From\Idea\_meta\scripts

REM Setup Python environment
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
echo.
echo This mode picks Ideas from the database.
echo Titles will NOT be saved to database.
echo.

REM Change to the module's script directory and run
cd /d "%MODULE_SCRIPT_DIR%"
python run.py --preview %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Script execution failed
    pause
    exit /b 1
)

echo.
pause
