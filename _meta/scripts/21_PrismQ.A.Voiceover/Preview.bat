@echo off
REM Preview.bat - PrismQ.A.Voiceover
REM Preview mode - does NOT save to database
REM
REM Usage: Preview.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\A\Voiceover"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.A.Voiceover - PREVIEW MODE
echo ========================================
echo.
echo This mode is for TESTING. Audio will NOT be saved.
echo.

python ..\..\..\A\Voiceover\src\voiceover_interactive.py --preview --debug

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
echo Check log file for detailed output
pause
exit /b 0
