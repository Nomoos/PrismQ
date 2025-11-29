@echo off
REM PrismQ.Idea.Creation.Preview.bat - Interactive Idea Creation (Preview Mode)
REM This script runs in preview mode WITHOUT saving to database
REM Extensive logging is enabled for testing and tuning purposes
REM
REM Usage:
REM   PrismQ.Idea.Creation.Preview.bat
REM
REM Features:
REM   - Creates ideas from text input
REM   - Does NOT save to database
REM   - Extensive debug logging to file
REM   - Log file created in same directory
REM
REM Environment:
REM   Virtual environment: T\Idea\Creation\.venv (created automatically)
REM   Dependencies: T\Idea\Creation\requirements.txt
REM   Config file: T\Idea\Creation\.env (created on first run)
REM
REM After running, the script will wait for text input.
REM Enter your text (title, description, story snippet, or JSON)
REM Press Enter twice to submit.
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
echo PrismQ.Idea.Creation - PREVIEW MODE
echo ========================================
echo.
echo This mode is for TESTING and TUNING.
echo Ideas will NOT be saved to database.
echo Extensive logging enabled.
echo.

REM Run Python module from T/Idea/Creation/src
python ..\..\..\T\Idea\Creation\src\idea_creation_interactive.py --preview --debug

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
