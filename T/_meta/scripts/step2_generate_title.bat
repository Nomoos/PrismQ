@echo off
REM PrismQ.T - Step 2: Generate Title
REM This script runs the title generation step as a separate process
REM 
REM Usage: step2_generate_title.bat

echo ========================================
echo PrismQ.T - Step 2: Generate Title
echo ========================================

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Run Python with the generate title action
python run_text_client.py --action generate_title

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to generate title
    pause
    exit /b 1
)

echo.
echo Step 2 completed. Run step3_generate_script.bat next.
pause
