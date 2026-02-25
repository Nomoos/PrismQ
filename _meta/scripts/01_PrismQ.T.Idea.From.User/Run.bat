@echo off
REM Run.bat - PrismQ.T.Idea.From.User
REM Continuous interactive idea creation - saves to database
REM
REM Usage: Run.bat
REM
REM Requires: Ollama must be running for AI-powered idea generation
REM
REM Environment:
REM   Virtual environment: T\Idea\From\User\.venv (created automatically)
REM   Dependencies: T\Idea\From\User\requirements.txt

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Start Ollama if not running
call ..\common\start_ollama.bat
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

REM Setup Python virtual environment
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Idea\From\User"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Idea.From.User - Continuous Mode
echo ========================================
echo.
echo This mode continuously accepts input and saves ideas to the database.
echo.

REM Run Python module
python ..\..\..\T\Idea\From\User\src\idea_creation_interactive.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Script execution failed
    pause
    exit /b 1
)

echo.
pause
exit /b 0
