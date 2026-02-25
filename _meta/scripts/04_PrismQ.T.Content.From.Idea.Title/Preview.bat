@echo off
REM Preview.bat - PrismQ.T.Content.From.Idea.Title
REM Preview mode - does NOT save to database
REM
REM Usage: Preview.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Content\From\Idea\Title"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Content.From.Idea.Title - PREVIEW MODE
echo ========================================
echo.
echo This mode is for TESTING. Content will NOT be saved.
echo.

python ..\..\..\T\Content\From\Idea\Title\src\content_from_idea_title_interactive.py --preview --debug

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
echo Check log file for detailed output
pause
exit /b 0
