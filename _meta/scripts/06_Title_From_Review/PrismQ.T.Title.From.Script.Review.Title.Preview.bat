@echo off
REM PrismQ.T.Title.From.Script.Review.Title.Preview.bat - Title Improvement (Preview Mode)
REM Runs in preview mode WITHOUT saving to database

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

call "%SCRIPT_DIR%setup_env.bat"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to setup Python environment
    pause
    exit /b 1
)

echo ========================================
echo PrismQ.T.Title.From.Script.Review.Title - PREVIEW MODE
echo ========================================
echo.
echo This mode is for TESTING and TUNING.
echo Results will NOT be saved to database.
echo.

python ..\..\..\T\Title\From\Title\Review\Script\src\title_from_review_interactive.py --preview --debug

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
