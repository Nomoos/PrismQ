@echo off
REM PrismQ.T.Title.From.Idea.bat - Interactive Title Generation from Idea
REM This script runs in interactive mode and saves titles to the database
REM
REM Usage:
REM   PrismQ.T.Title.From.Idea.bat
REM
REM After running, the script will wait for idea input.
REM Enter your idea (text, JSON, or title/concept)
REM Press Enter to submit.
REM Type 'quit' to exit.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Setup Python environment
call "%SCRIPT_DIR%setup_env.bat"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to setup Python environment
    pause
    exit /b 1
)

echo ========================================
echo PrismQ.T.Title.From.Idea - Interactive Mode
echo ========================================
echo.

REM Run Python module
python ..\..\..\T\Title\From\Idea\src\title_from_idea_interactive.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Script execution failed
    pause
    exit /b 1
)

echo.
pause
