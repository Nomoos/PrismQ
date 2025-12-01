@echo off
REM PrismQ.T.Review.Title.From.Script.bat - Interactive Title Review
REM This script reviews titles against scripts for alignment
REM
REM Usage:
REM   PrismQ.T.Review.Title.From.Script.bat

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
echo PrismQ.T.Review.Title.From.Script - Interactive Mode
echo ========================================
echo.

REM Run Python module
python ..\..\..\T\Review\Title\From\Script\src\review_title_from_script_interactive.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Script execution failed
    pause
    exit /b 1
)

echo.
pause
