@echo off
REM PrismQ.T.Script.From.Idea.Title.Preview.bat - Interactive Script Generation (Preview Mode)
REM This script runs in preview mode WITHOUT saving to database
REM Extensive logging is enabled for testing and tuning purposes
REM
REM Usage:
REM   PrismQ.T.Script.From.Idea.Title.Preview.bat
REM
REM Features:
REM   - Generates scripts from idea+title input
REM   - Does NOT save to database
REM   - Extensive debug logging to file

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
echo PrismQ.T.Script.From.Idea.Title - PREVIEW MODE
echo ========================================
echo.
echo This mode is for TESTING and TUNING.
echo Scripts will NOT be saved to database.
echo Extensive logging enabled.
echo.

REM Run Python module in preview mode
python ..\..\..\T\Script\From\Idea\Title\src\script_from_idea_title_interactive.py --preview --debug

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
