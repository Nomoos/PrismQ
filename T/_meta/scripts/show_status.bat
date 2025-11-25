@echo off
REM PrismQ.T - Show Workflow Status
REM This script shows the current workflow status and next item to process
REM 
REM Usage: show_status.bat

echo ========================================
echo PrismQ.T - Workflow Status
echo ========================================

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Run Python with the status action
python run_text_client.py --action status

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to show status
    pause
    exit /b 1
)

pause
