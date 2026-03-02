@echo off
REM Run.bat - PrismQ.T.Script.From.Title.Review.Script
REM Refine script from title and review feedback - saves to database
REM
REM Usage: Run.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Content\From\Title\Review\Script"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Script.From.Title.Review.Script - RUN MODE
echo ========================================
echo.

python ..\..\..\T\Content\From\Title\Review\Script\src\script_from_review_workflow.py

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0
