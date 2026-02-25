@echo off
REM Preview.bat - PrismQ.T.Title.From.Script.Review.Title
REM Preview mode - enables extensive logging for debugging
REM
REM Usage: Preview.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Title\From\Title\Review\Script"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Title.From.Script.Review.Title - PREVIEW MODE
echo ========================================
echo.
echo Preview mode with extensive logging enabled
echo.

python ..\..\..\T\Title\From\Title\Review\Script\src\title_from_review_interactive.py --preview --debug

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
echo Check log file for detailed output
pause
exit /b 0
