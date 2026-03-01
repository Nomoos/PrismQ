@echo off
REM Run.bat - PrismQ.T.Story.Polish
REM Continuous workflow - expert-level story polish (GPT) from database
REM Runs continuously with 30s wait when idle, 1ms between items
REM
REM Usage: Run.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Story\Polish"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Story.Polish - CONTINUOUS MODE
echo ========================================
echo.

python ..\..\..\T\Story\Polish\src\story_polish_interactive.py

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0
