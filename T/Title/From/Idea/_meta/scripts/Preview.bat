@echo off
REM PrismQ.T.Title.From.Idea - Preview Mode
REM Shows what Ideas would be processed without making changes
REM
REM Usage:
REM   Preview.bat --db path\to\database.db
REM   Preview.bat --db prismq.db --idea-id 123
REM   Preview.bat --db prismq.db --limit 5
REM   Preview.bat --db prismq.db --json
REM
REM Environment:
REM   Virtual environment: T\Title\From\Idea\.venv (created automatically)
REM   Dependencies: T\Title\From\Idea\requirements.txt

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

REM Run Python script with all arguments plus --preview
python run.py --preview %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Preview failed
    pause
    exit /b 1
)

echo.
pause
