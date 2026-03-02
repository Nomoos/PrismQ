@echo off
REM Run.bat - PrismQ.T.Review.Title.From.Content
REM Review titles from database
REM
REM Usage: Run.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Start Ollama if not running
call ..\common\start_ollama.bat
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Review\Title\From\Content"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Review.Title.From.Content
echo ========================================
echo.

python ..\..\..\T\Review\Title\From\Content\src\review_title_from_script_workflow.py

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0
