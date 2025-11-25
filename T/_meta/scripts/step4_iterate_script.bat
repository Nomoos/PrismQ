@echo off
REM PrismQ.T - Step 4: Iterate on Script (Feedback Loop)
REM This script runs the script iteration step as a separate process
REM Can be run multiple times (unlimited iterations)
REM 
REM Usage: step4_iterate_script.bat

echo ========================================
echo PrismQ.T - Step 4: Iterate on Script
echo ========================================

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Run Python with the iterate script action
python run_text_client.py --action iterate_script

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to iterate script
    pause
    exit /b 1
)

echo.
echo Step 4 completed. Run again for more iterations, or step5_export.bat to export.
pause
