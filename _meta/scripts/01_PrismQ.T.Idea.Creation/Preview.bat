@echo off
REM Preview.bat - PrismQ.T.Idea.Creation
REM Preview mode - does NOT save to database, extensive logging enabled
REM
REM Usage: Preview.bat
REM
REM Features:
REM   - Creates ideas from text input
REM   - Does NOT save to database
REM   - Extensive debug logging to file
REM
REM Environment:
REM   Virtual environment: T\Idea\Creation\.venv (created automatically)
REM   Dependencies: T\Idea\Creation\requirements.txt

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Setup Python virtual environment
call :setup_env
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to setup Python environment
    pause
    exit /b 1
)

echo ========================================
echo PrismQ.T.Idea.Creation - PREVIEW MODE
echo ========================================
echo.
echo This mode is for TESTING and TUNING.
echo Ideas will NOT be saved to database.
echo Extensive logging enabled.
echo.

REM Run Python module with preview and debug flags
python ..\..\..\..\T\Idea\Creation\src\idea_creation_interactive.py --preview --debug

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
exit /b 0

:setup_env
setlocal enabledelayedexpansion

set MODULE_DIR=%SCRIPT_DIR%..\..\..\..\T\Idea\Creation
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
