@echo off
REM Preview.bat - PrismQ.T.Idea.From.User
REM PREVIEW MODE: Generate idea variants without saving to database
REM
REM Usage: Preview.bat
REM
REM Requires: Python and Ollama must be available
REM
REM Environment:
REM   Virtual environment: T\Idea\Creation\.venv (created automatically)
REM   Dependencies: T\Idea\Creation\requirements.txt

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Check Python availability
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please install Python 3.9 or later.
    pause
    exit /b 1
)

REM Start Ollama if not running
call ..\common\start_ollama.bat
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

REM Setup Python virtual environment
call :setup_env
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Idea.From.User - Preview Mode
echo ========================================
echo.
echo PREVIEW MODE: Generates ideas but will NOT save to database.
echo Use Run.bat to save results to the database.
echo.

REM Run Python module with preview and debug flags
python ..\..\..\T\Idea\Creation\src\idea_creation_interactive.py --preview --debug

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
REM Setup Python virtual environment for the Creation module
set "MODULE_DIR=%SCRIPT_DIR%..\..\..\T\Idea\Creation"
set "VENV_DIR=%MODULE_DIR%\.venv"
set "REQUIREMENTS=%MODULE_DIR%\requirements.txt"

if not exist "%VENV_DIR%\pyvenv.cfg" (
    echo [INFO] Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if %ERRORLEVEL% NEQ 0 exit /b 1
)

call "%VENV_DIR%\Scripts\activate.bat"

if exist "%REQUIREMENTS%" if not exist "%VENV_DIR%\.requirements_installed" (
    echo [INFO] Installing dependencies...
    pip install -r "%REQUIREMENTS%"
    echo Installed > "%VENV_DIR%\.requirements_installed"
)

exit /b 0
