@echo off
REM PrismQ.T.Title.From.Idea - Preview Mode
REM Shows what Ideas would be processed without making changes
REM
REM Usage:
REM   Preview.bat                               Use default .env (C:/PrismQ/.env)
REM   Preview.bat --env path\to\.env            Use custom .env file
REM   Preview.bat --idea-id 123                 Preview specific Idea
REM   Preview.bat --limit 5                     Preview max 5 Ideas
REM   Preview.bat --json                        Output as JSON
REM
REM Environment:
REM   .env file defines WORKING_DIRECTORY where db.s3db is located
REM   Default .env location: C:/PrismQ/.env

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
echo PrismQ.T.Title.From.Idea - Preview
echo ========================================

REM Run Python script with all arguments plus --preview
python run.py --preview %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Preview failed
    pause
    exit /b 1
)

echo.
pause
