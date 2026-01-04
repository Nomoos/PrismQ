@echo off
REM Run.bat - PrismQ.T.Idea.From.User
REM Continuous interactive idea creation - saves to database
REM
REM Usage: Run.bat
REM
REM Requires: Ollama must be running for AI-powered idea generation
REM
REM Environment:
REM   Virtual environment: T\Idea\From\User\.venv (created automatically)
REM   Dependencies: T\Idea\From\User\requirements.txt

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Start Ollama if not running
call ..\common\start_ollama.bat
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

REM Setup Python virtual environment
call :setup_env
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to setup Python environment
    pause
    exit /b 1
)

echo ========================================
echo PrismQ.T.Idea.From.User - Continuous Mode
echo ========================================
echo.
echo This mode continuously accepts input and saves ideas to the database.
echo.

REM Run Python module
python ..\..\..\T\Idea\From\User\src\idea_creation_interactive.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Script execution failed
    pause
    exit /b 1
)

echo.
pause
exit /b 0

:setup_env
setlocal enabledelayedexpansion

set MODULE_DIR=%SCRIPT_DIR%..\..\..\T\Idea\From\User
set VENV_DIR=%MODULE_DIR%\.venv
set REQUIREMENTS=%MODULE_DIR%\requirements.txt
set VENV_MARKER=%VENV_DIR%\pyvenv.cfg

echo [INFO] Setting up Python environment...

REM Check Python availability
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    exit /b 1
)

REM Create virtual environment if needed
if not exist "%VENV_MARKER%" (
    echo [INFO] Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if %ERRORLEVEL% NEQ 0 exit /b 1
)

REM Activate and install dependencies
call "%VENV_DIR%\Scripts\activate.bat"
if not exist "%VENV_DIR%\.requirements_installed" (
    echo [INFO] Installing dependencies...
    pip install -r "%REQUIREMENTS%" --quiet
    echo Installed > "%VENV_DIR%\.requirements_installed"
)

echo [INFO] Environment ready
endlocal & call "%VENV_DIR%\Scripts\activate.bat"
exit /b 0
