@echo off
REM Check Submodules - Validation wrapper
REM Validates if each folder in any mod/ folder is mapped in .gitmodules

setlocal

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "PYTHON_SCRIPT=%SCRIPT_DIR%git-utils\check_submodules.py"

REM Check if Python script exists
if not exist "%PYTHON_SCRIPT%" (
    echo Error: Python script not found at: %PYTHON_SCRIPT%
    exit /b 1
)

REM Run the Python script
python "%PYTHON_SCRIPT%" %*

REM Exit with the same code as the Python script
exit /b %ERRORLEVEL%
