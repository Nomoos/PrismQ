@echo off
REM Run.bat - PrismQ.T.Review.Content.Readability
REM Script readability and clarity check from database
REM
REM Usage: Run.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Review\Script\Readability"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Review.Content.Readability
echo ========================================
echo.

python ..\..\..\T\Review\Script\Readability\src\script_readability_workflow.py

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0
