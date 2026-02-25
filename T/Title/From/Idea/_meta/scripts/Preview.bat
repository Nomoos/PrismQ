@echo off
REM PrismQ.T.Title.From.Idea - Preview Mode
REM Shows what Stories would be processed and what titles would be generated
REM without making any database changes
REM
REM Usage:
REM   Preview.bat                               Use default database
REM   Preview.bat --db C:\path\to\db.s3db       Use specific database
REM   Preview.bat --debug                       Enable debug logging
REM
REM Requirements:
REM   Ollama must be running with qwen3:32b model

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Setup Python virtual environment
call "%SCRIPT_DIR%setup_env.bat"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to setup Python environment
    pause
    exit /b 1
)

echo ========================================
echo PrismQ.T.Title.From.Idea - Preview
echo ========================================

REM Run Python script with --preview flag plus any additional arguments
python run.py --preview %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Preview failed
    pause
    exit /b 1
)

echo.
pause
