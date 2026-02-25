@echo off
REM Preview.bat - PrismQ.V.Scene
REM Preview mode - does NOT save to database
REM
REM Usage: Preview.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\V\Scene"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.V.Scene - PREVIEW MODE
echo ========================================
echo.
echo This mode is for TESTING. Scenes will NOT be saved.
echo.

python ..\..\..\V\Scene\src\scene_interactive.py --preview --debug

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
echo Check log file for detailed output
pause
exit /b 0
