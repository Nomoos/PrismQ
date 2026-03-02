@echo off
REM Run.bat - PrismQ.T.Review.Content.Tone
REM Tone consistency check from database
REM
REM Usage: Run.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Review\Script\Tone"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Review.Content.Tone
echo ========================================
echo.

python ..\..\..\T\Review\Script\Tone\src\tone_workflow.py

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0
