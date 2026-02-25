@echo off
REM Preview.bat - PrismQ.T.Review.Script.By.Title.Idea
REM Preview mode - does NOT save to database
REM
REM Usage: Preview.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Review\Content\From\Title\Idea"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Review.Script.By.Title.Idea - PREVIEW MODE
echo ========================================
echo.
echo This mode is for TESTING. Reviews will NOT be saved.
echo.

python ..\..\..\T\Review\Content\From\Title\Idea\src\review_script_by_title_idea_interactive.py --preview --debug

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
echo Check log file for detailed output
pause
exit /b 0
