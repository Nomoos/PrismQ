@echo off
REM Run.bat - PrismQ.T.Review.Script.By.Title
REM Review script against title - saves to database
REM
REM Usage: Run.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Review\Script\From\Title"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Review.Script.By.Title - RUN MODE
echo ========================================
echo.

python ..\..\..\T\Review\Script\From\Title\src\review_script_from_title_interactive.py

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0
