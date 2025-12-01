@echo off
REM PrismQ.T.Title.From.Idea.Preview.bat - Interactive Title Generation (Preview Mode)
REM This script runs in preview mode WITHOUT saving to database
REM Extensive logging is enabled for testing and tuning purposes
REM
REM Usage:
REM   PrismQ.T.Title.From.Idea.Preview.bat
REM
REM Features:
REM   - Generates titles from idea input
REM   - Does NOT save to database
REM   - Extensive debug logging to file
REM   - Log file created in same directory
REM
REM Environment:
REM   Virtual environment: T\Title\From\Idea\.venv (created automatically)
REM   Dependencies: T\Title\From\Idea\requirements.txt
REM   Config file: T\Title\From\Idea\.env (created on first run)
REM
REM After running, the script will wait for idea input.
REM Enter your idea (text, JSON, or title/concept)
REM Press Enter to submit.
REM Type 'quit' to exit.

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
echo.
echo This mode is for TESTING and TUNING.
echo Titles will NOT be saved to database.
echo Extensive logging enabled.
echo.

REM Run Python module from T/Title/From/Idea/src
python ..\..\..\T\Title\From\Idea\src\title_from_idea_interactive.py --preview --debug

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Script execution failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Check log file for detailed output
echo ========================================
echo.
pause
