@echo off
REM PrismQ.T - Step 3: Generate Script
REM This script runs the script generation step as a separate process
REM 
REM Usage: step3_generate_script.bat

echo ========================================
echo PrismQ.T - Step 3: Generate Script
echo ========================================

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Run Python with the generate script action
python run_text_client.py --action generate_script

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to generate script
    pause
    exit /b 1
)

echo.
echo Step 3 completed. Run step4_iterate_script.bat to iterate, or step5_export.bat to export.
pause
