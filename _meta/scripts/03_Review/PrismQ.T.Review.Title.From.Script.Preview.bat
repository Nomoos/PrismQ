@echo off
REM PrismQ.T.Review.Title.From.Script.Preview.bat - Title Review (Preview Mode)
REM Runs in preview mode WITHOUT saving to database
REM
REM Usage:
REM   PrismQ.T.Review.Title.From.Script.Preview.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Setup Python environment
call "%SCRIPT_DIR%setup_env.bat"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to setup Python environment
    pause
    exit /b 1
)

echo ========================================
echo PrismQ.T.Review.Title.From.Script - PREVIEW MODE
echo ========================================
echo.
echo This mode is for TESTING and TUNING.
echo Reviews will NOT be saved to database.
echo.

REM Run Python module in preview mode
python ..\..\..\T\Review\Title\From\Script\src\review_title_from_script_interactive.py --preview --debug

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Script execution failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Check log file for detailed output
echo ========================================
echo.
pause
