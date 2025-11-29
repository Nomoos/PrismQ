@echo off
REM PrismQ - Create Idea Variants from Any Text
REM This script creates idea variants from any input (title, description, story, JSON)
REM
REM Usage:
REM   create_variants.bat "I wore a baggy tee on the first day of school..."
REM   create_variants.bat "Fashion Revolution"
REM   create_variants.bat "text" --variant emotion_first
REM   create_variants.bat "text" --count 5
REM   create_variants.bat --file story.txt
REM   create_variants.bat --list
REM
REM Environment:
REM   Virtual environment: T\Idea\Creation\.venv (created automatically)
REM   Dependencies: T\Idea\Creation\requirements.txt
REM   Config file: T\Idea\Creation\.env (created on first run)

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
echo PrismQ - Create Idea Variants
echo ========================================

REM Run Python script with all arguments
python create_variants.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to create variants
    pause
    exit /b 1
)

echo.
pause
