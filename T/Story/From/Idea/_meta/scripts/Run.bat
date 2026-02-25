@echo off
REM Run.bat - PrismQ.T.Story.From.Idea - Create Story objects from Idea objects
REM Processes Ideas without Story references and creates 10 Stories per Idea
REM Runs in continuous mode - press Ctrl+C to stop
REM
REM Usage:
REM   Run.bat                  Run continuously with database save
REM   Run.bat --preview        Preview mode (no database changes)
REM   Run.bat --debug          Preview mode with debug output
REM
REM Requirements:
REM   Idea records must exist in the shared database (created by module 01)

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
echo PrismQ.T.Story.From.Idea - Continuous Mode
echo ========================================
echo Press Ctrl+C to stop
echo.

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
