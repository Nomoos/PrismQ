@echo off
REM Preview.bat - PrismQ.A.Publishing
REM Preview mode - does NOT publish audio
REM
REM Usage: Preview.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\A\Publishing"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.A.Publishing - PREVIEW MODE
echo ========================================
echo.
echo This mode is for TESTING. Audio will NOT be published.
echo.

python ..\..\..\A\Publishing\src\publishing_interactive.py --preview --debug

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
echo Check log file for detailed output
pause
exit /b 0
