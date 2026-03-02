@echo off
REM PrismQ.T.Title.From.Idea - Generate AI Titles for Stories
REM Processes Stories with state PrismQ.T.Title.From.Idea and generates titles
REM Runs in continuous mode - press Ctrl+C to stop
REM
REM Usage:
REM   Run.bat                                   Use default database
REM   Run.bat --db C:\path\to\db.s3db           Use specific database
REM   Run.bat --debug                           Enable debug logging
REM
REM Requirements:
REM   Ollama must be running with qwen3:32b model
REM   Stories must exist in state PrismQ.T.Title.From.Idea (created by module 02)

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Setup Python virtual environment
call "%SCRIPT_DIR%..\..\..\..\..\..\\_meta\scripts\common\setup_env.bat" "%SCRIPT_DIR%..\.."
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to setup Python environment
    pause
    exit /b 1
)

echo ========================================
echo PrismQ.T.Title.From.Idea
echo ========================================
echo Press Ctrl+C to stop
echo.

REM Run Python script with all arguments
python run.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Title generation failed
    pause
    exit /b 1
)

echo.
pause
