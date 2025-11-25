@echo off
REM PrismQ.T - Load Demo Idea
REM This script loads a demo idea for testing
REM 
REM Usage: load_demo.bat

echo ========================================
echo PrismQ.T - Load Demo Idea
echo ========================================

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Run Python with the load demo action
python run_text_client.py --action load_demo

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to load demo
    pause
    exit /b 1
)

echo.
echo Demo loaded. Run step2_generate_title.bat next.
pause
