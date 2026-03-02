@echo off
REM Run.bat - PrismQ.T.Review.Content.Editing
REM Final editing pass from database
REM
REM Usage: Run.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Review\Script\Editing"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Review.Content.Editing
echo ========================================
echo.

python ..\..\..\T\Review\Script\Editing\src\editing_workflow.py

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0
