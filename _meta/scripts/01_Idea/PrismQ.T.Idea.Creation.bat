@echo off
REM PrismQ.Idea.Creation.bat - Interactive Idea Creation
REM This script runs in interactive mode and saves ideas to the database
REM
REM Usage:
REM   PrismQ.Idea.Creation.bat
REM
REM After running, the script will wait for text input.
REM Enter your text (title, description, story snippet, or JSON)
REM Press Enter twice to submit.
REM Type 'quit' to exit.
REM
REM Environment:
REM   Virtual environment: T\Idea\Creation\.venv (created automatically)
REM   Dependencies: T\Idea\Creation\requirements.txt
REM   Config file: T\Idea\Creation\.env (created on first run)

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
echo PrismQ.Idea.Creation - Interactive Mode
echo ========================================
echo.

REM Run Python module from T/Idea/Creation/src
python ..\..\..\T\Idea\Creation\src\idea_creation_interactive.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Script execution failed
    pause
    exit /b 1
)

echo.
pause
