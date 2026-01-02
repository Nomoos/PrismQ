@echo off
REM Run.bat - PrismQ.T.Content.From.Idea.Title
REM Continuous workflow - process stories from database
REM
REM Usage: Run.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Start Ollama if not running
call ..\common\start_ollama.bat
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

call :setup_env
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Content.From.Idea.Title - CONTINUOUS MODE
echo ========================================
echo.

python ..\..\..\T\Content\From\Idea\Title\src\content_from_idea_title_workflow.py

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0

:setup_env
setlocal enabledelayedexpansion
set MODULE_DIR=%SCRIPT_DIR%..\..\..\T\Content\From\Idea\Title
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
