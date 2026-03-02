@echo off
REM Run.bat - PrismQ.T.Review.Content.Content
REM Content accuracy validation from database
REM
REM Usage: Run.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Review\Script\Content"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Review.Content.Content
echo ========================================
echo.

python ..\..\..\T\Review\Script\Content\content_review_workflow.py

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0
