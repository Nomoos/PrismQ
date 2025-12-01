@echo off
REM PrismQ.T.Title.From.Idea - Create Stories from Ideas
REM Loads Ideas from database and creates 10 Stories with Titles for each
REM
REM Usage:
REM   Run.bat                                   Use default .env (C:/PrismQ/.env)
REM   Run.bat --env path\to\.env                Use custom .env file
REM   Run.bat --idea-id 123                     Process specific Idea
REM   Run.bat --limit 5                         Process max 5 Ideas
REM   Run.bat --json                            Output as JSON
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
echo PrismQ.T.Title.From.Idea - Create Stories
echo ========================================

REM Run Python script with all arguments
python run.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Story creation failed
    pause
    exit /b 1
)

echo.
pause
