@echo off
REM Run.bat - PrismQ.T.Title.From.Script.Review.Title
REM Refine titles interactively from script and review feedback
REM
REM Usage: Run.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Title\From\Title\Review\Script"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Title.From.Script.Review.Title
echo ========================================
echo.

python ..\..\..\T\Title\From\Title\Review\Script\src\title_from_review_interactive.py

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0
