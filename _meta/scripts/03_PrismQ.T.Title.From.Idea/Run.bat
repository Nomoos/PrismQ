@echo off
REM Run.bat - PrismQ.T.Title.From.Idea
REM Generate title from idea - saves to database
REM
REM Usage: Run.bat
REM
REM Requires: Ollama must be running with qwen2.5:14b-instruct model

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Start Ollama if not running
call ..\common\start_ollama.bat
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Title\From\Idea"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Title.From.Idea
echo ========================================
echo.

python ..\..\..\T\Title\From\Idea\src\title_from_idea_interactive.py --worker-id 0

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0
