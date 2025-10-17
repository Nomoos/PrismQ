@echo off
REM Git Commit All - Recursive commit wrapper
REM Commits all changes in all repositories with one commit message

setlocal

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "PYTHON_SCRIPT=%SCRIPT_DIR%git-utils\git_commit_all.py"

REM Check if Python script exists
if not exist "%PYTHON_SCRIPT%" (
    echo Error: Python script not found at: %PYTHON_SCRIPT%
    exit /b 1
)

REM Check if commit message is provided
if "%~1"=="" (
    echo Usage: git-commit-all "commit message"
    echo.
    echo Example:
    echo   git-commit-all "Update all repositories"
    exit /b 1
)

REM Run the Python script with all arguments
python "%PYTHON_SCRIPT%" %*

REM Exit with the same code as the Python script
exit /b %ERRORLEVEL%
