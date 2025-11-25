@echo off
REM PrismQ.T - Step 5: Export Content
REM This script runs the export step as a separate process
REM 
REM Usage: step5_export.bat

echo ========================================
echo PrismQ.T - Step 5: Export Content
echo ========================================

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Run Python with the export action
python run_text_client.py --action export

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to export content
    pause
    exit /b 1
)

echo.
echo Step 5 completed. Content exported successfully.
pause
