@echo off
REM PrismQ - Create Idea Variants
REM This script creates idea variants from a title
REM
REM Usage:
REM   create_variants.bat "My Idea Title"
REM   create_variants.bat "My Idea Title" --variant emotion_first
REM   create_variants.bat "My Idea Title" --variant emotion_first --count 5
REM   create_variants.bat "My Idea Title" --all
REM   create_variants.bat --list

echo ========================================
echo PrismQ - Create Idea Variants
echo ========================================

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

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
