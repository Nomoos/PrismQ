@echo off
REM PrismQ.T.Review.Script.From.Title.Preview.bat - Script Review (Preview Mode)
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
echo PrismQ.T.Review.Script.From.Title - PREVIEW MODE
echo ========================================
echo.
echo This mode is for TESTING and TUNING.
echo Reviews will NOT be saved to database.
echo.

python ..\..\..\T\Review\Script\From\Title\src\review_script_from_title_interactive.py --preview --debug

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
