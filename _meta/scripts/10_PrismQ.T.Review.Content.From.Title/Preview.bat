@echo off
REM Preview.bat - PrismQ.T.Review.Script.By.Title
REM Preview mode - does NOT save to database
REM
REM Usage: Preview.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Review\Script\From\Title"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Review.Script.By.Title - PREVIEW MODE
echo ========================================
echo.
echo This mode is for TESTING. Reviews will NOT be saved.
echo.

python ..\..\..\T\Review\Script\From\Title\src\review_script_from_title_interactive.py --preview --debug

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
echo Check log file for detailed output
pause
exit /b 0
