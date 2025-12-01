@echo off
REM PrismQ.T.Script.From.Idea.Title.bat - Interactive Script Generation
REM This script runs in interactive mode and saves scripts to the database
REM
REM Usage:
REM   PrismQ.T.Script.From.Idea.Title.bat
REM
REM After running, the script will wait for input.
REM Enter idea+title (JSON or plain text)
REM Press Enter to submit.
REM Type 'quit' to exit.
REM
REM Environment:
REM   Virtual environment: T\Script\From\Idea\Title\.venv (created automatically)
REM   Dependencies: T\Script\From\Idea\Title\requirements.txt
REM   Config file: T\Script\From\Idea\Title\.env (created on first run)

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
echo PrismQ.T.Script.From.Idea.Title - Interactive Mode
echo ========================================
echo.

REM Run Python module
python ..\..\..\T\Script\From\Idea\Title\src\script_from_idea_title_interactive.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Script execution failed
    pause
    exit /b 1
)

echo.
pause
