@echo off
REM PrismQ.T.Script.From.Title.Review.Script.bat - Interactive Script Improvement
REM This script improves scripts based on review feedback
REM
REM Usage:
REM   PrismQ.T.Script.From.Title.Review.Script.bat

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
echo PrismQ.T.Script.From.Title.Review.Script - Interactive Mode
echo ========================================
echo.

REM Run Python module
python ..\..\..\T\Script\From\Title\Review\Script\src\script_from_review_interactive.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Script execution failed
    pause
    exit /b 1
)

echo.
pause
