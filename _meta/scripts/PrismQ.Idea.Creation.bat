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

echo ========================================
echo PrismQ.Idea.Creation - Interactive Mode
echo ========================================
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check Python availability
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Run Python script in interactive mode
python PrismQ.Idea.Creation.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Script execution failed
    pause
    exit /b 1
)

echo.
pause
