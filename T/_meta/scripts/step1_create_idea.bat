@echo off
REM PrismQ.T - Step 1: Create Idea
REM This script runs the idea creation step as a separate process
REM 
REM Usage: step1_create_idea.bat

echo ========================================
echo PrismQ.T - Step 1: Create Idea
echo ========================================

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Run Python with the create idea action
python run_text_client.py --action create_idea

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create idea
    pause
    exit /b 1
)

echo.
echo Step 1 completed. Run step2_generate_title.bat next.
pause
