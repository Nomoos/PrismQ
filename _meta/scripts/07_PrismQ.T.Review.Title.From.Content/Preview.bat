@echo off
REM Preview.bat - PrismQ.T.Review.Title.By.Script
REM Preview mode - does NOT save to database
REM
REM Usage: Preview.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call :setup_env
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Review.Title.By.Script - PREVIEW MODE
echo ========================================
echo.
echo This mode is for TESTING. Reviews will NOT be saved.
echo.

python ..\..\..\T\Review\Title\ByScript\src\review_title_by_script_interactive.py --preview --debug

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
echo Check log file for detailed output
pause
exit /b 0

:setup_env
setlocal enabledelayedexpansion
set MODULE_DIR=%SCRIPT_DIR%..\..\..\T\Review\Title\ByScript
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
