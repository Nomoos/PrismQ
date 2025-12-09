@echo off
REM Manual.bat - PrismQ.T.Title.From.Idea
REM Manual mode - user writes prompt into console and fills in AI response manually
REM
REM Usage: Manual.bat
REM
REM This mode allows you to manually control the AI interaction by:
REM   1. Viewing the prompt that would be sent to AI
REM   2. Running the AI manually (e.g., in Ollama CLI or web interface)
REM   3. Pasting the response back into this script
REM
REM Useful for debugging, testing prompts, or when AI is unavailable

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Start Ollama if not running
call ..\common\start_ollama.bat
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

call :setup_env
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Title.From.Idea - MANUAL MODE
echo ========================================
echo.
echo This mode allows you to manually control AI interactions.
echo You will see the prompt and manually provide responses.
echo.

python ..\..\..\T\Title\From\Idea\src\title_from_idea_interactive.py --manual --debug

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
echo Check log file for detailed output
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
