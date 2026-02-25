@echo off
REM Run.bat - PrismQ.T.Review.Script.Content
REM Content accuracy and relevance validation - saves to database
REM
REM Usage: Run.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Review\Script\Content"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Review.Script.Content - RUN MODE
echo ========================================
echo.

python ..\..\..\T\Review\Script\Content\script_content_review.py

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0
