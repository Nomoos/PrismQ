@echo off
REM Run.bat - PrismQ.T.Review.Script.Readability
REM Script readability and clarity check - saves to database
REM
REM Usage: Run.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Review\Readability"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Review.Script.Readability - RUN MODE
echo ========================================
echo.

python ..\..\..\T\Review\Readability\src\review_script_readability_interactive.py

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0
