@echo off
REM Run.bat - PrismQ.T.Title.From.Idea
REM Generate title from idea - saves to database in continuous mode (default)
REM
REM Usage: Run.bat [database_path]
REM   database_path - Optional path to database file (default: from Config or C:/PrismQ/db.s3db)
REM
REM Requires: Ollama must be running with qwen2.5:14b-instruct model
REM
REM Note: Runs in continuous mode by default (1ms delay between runs)

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Start Ollama if not running
call ..\common\start_ollama.bat
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

call :setup_env
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Title.From.Idea - CONTINUOUS MODE
echo ========================================
echo.

REM Get database path from argument or let Python use the default
if not "%~1"=="" (
    python ..\..\..\T\Title\From\Idea\src\title_from_idea_interactive.py --db "%~1"
) else (
    python ..\..\..\T\Title\From\Idea\src\title_from_idea_interactive.py
)

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0

:setup_env
setlocal enabledelayedexpansion
set MODULE_DIR=%SCRIPT_DIR%..\..\..\T\Title\From\Idea
set VENV_DIR=%MODULE_DIR%\.venv
set REQUIREMENTS=%MODULE_DIR%\requirements.txt
set VENV_MARKER=%VENV_DIR%\pyvenv.cfg
echo [INFO] Setting up Python environment...
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 ( echo ERROR: Python not found & exit /b 1 )
if not exist "%VENV_MARKER%" (
    echo [INFO] Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if %ERRORLEVEL% NEQ 0 exit /b 1
)
call "%VENV_DIR%\Scripts\activate.bat"
if exist "%REQUIREMENTS%" if not exist "%VENV_DIR%\.requirements_installed" (
    echo [INFO] Installing dependencies...
    pip install -r "%REQUIREMENTS%" --quiet
    echo Installed > "%VENV_DIR%\.requirements_installed"
)
echo [INFO] Environment ready
endlocal & call "%VENV_DIR%\Scripts\activate.bat"
exit /b 0

