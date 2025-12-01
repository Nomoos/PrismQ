@echo off
REM PrismQ.T.Title.From.Idea - Create Stories from Ideas
REM Loads Ideas from database and creates 10 Stories with Titles for each
REM
REM Usage:
REM   Run.bat --db path\to\database.db
REM   Run.bat --db prismq.db --idea-id 123
REM   Run.bat --db prismq.db --limit 5
REM   Run.bat --db prismq.db --json
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
echo PrismQ.T.Title.From.Idea - Create Stories
echo ========================================

REM Run Python script with all arguments
python run.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Story creation failed
    pause
    exit /b 1
)

echo.
pause
