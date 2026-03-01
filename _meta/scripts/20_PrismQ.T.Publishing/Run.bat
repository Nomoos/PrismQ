@echo off
REM Run.bat - PrismQ.T.Publishing
REM Continuous workflow - text publishing with SEO optimization from database
REM Runs continuously with 30s wait when idle, 1ms between items
REM
REM Usage: Run.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Publishing"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Publishing - CONTINUOUS MODE
echo ========================================
echo.

python ..\..\..\T\Publishing\src\publishing_interactive.py

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0
