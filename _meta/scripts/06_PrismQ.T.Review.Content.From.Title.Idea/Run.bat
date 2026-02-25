@echo off
REM Run.bat - PrismQ.T.Review.Content.From.Title.Idea
REM Continuous workflow - review content from database (with title and idea context)
REM
REM Usage: Run.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Start Ollama if not running
call ..\common\start_ollama.bat
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Review\Content\From\Title\Idea"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Review.Content.From.Title.Idea - CONTINUOUS MODE
echo ========================================
echo.

python ..\..\..\T\Review\Content\From\Title\Idea\src\review_content_from_title_idea_workflow.py

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0
