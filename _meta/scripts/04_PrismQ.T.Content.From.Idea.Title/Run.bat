@echo off
REM Run.bat - PrismQ.T.Content.From.Idea.Title
REM Process stories from database
REM
REM Usage: Run.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Start Ollama if not running
call ..\common\start_ollama.bat
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Content\From\Idea\Title"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Content.From.Idea.Title
echo ========================================
echo.

python ..\..\..\T\Content\From\Idea\Title\src\content_from_idea_title_workflow.py

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0
