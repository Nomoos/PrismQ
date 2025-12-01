@echo off
REM PrismQ.T.Review.Script.From.Title.bat - Interactive Script Review
REM This script runs in interactive mode for reviewing scripts against titles

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
echo PrismQ.T.Review.Script.From.Title - Interactive Mode
echo ========================================
echo.

python ..\..\..\T\Review\Script\From\Title\src\review_script_from_title_interactive.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Script execution failed
    pause
    exit /b 1
)

echo.
pause
