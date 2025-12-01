@echo off
REM PrismQ - Create Stories with Titles from Idea
REM This script creates 10 Story objects from an Idea, each with an initial Title (v0)
REM
REM Usage:
REM   create_stories.bat "Idea Title" "Idea concept"
REM   create_stories.bat --file idea.json
REM   create_stories.bat --idea-id "my-id" "Title" "Concept"
REM   create_stories.bat --db prismq.db "Title" "Concept"
REM
REM Environment:
REM   Virtual environment: T\Title\From\Idea\.venv (created automatically)
REM   Dependencies: T\Title\From\Idea\requirements.txt (if exists)

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
echo PrismQ - Create Stories from Idea
echo ========================================

REM Run Python script with all arguments
python create_stories.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to create stories
    pause
    exit /b 1
)

echo.
pause
