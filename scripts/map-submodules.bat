@echo off
REM Map Submodules - Auto-registration wrapper
REM Checks mod/ directories and adds git repos to .gitmodules

setlocal

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "PYTHON_SCRIPT=%SCRIPT_DIR%git-utils\map_submodules.py"

REM Check if Python script exists
if not exist "%PYTHON_SCRIPT%" (
    echo Error: Python script not found at: %PYTHON_SCRIPT%
    exit /b 1
)

REM Run the Python script
python "%PYTHON_SCRIPT%" %*

REM Exit with the same code as the Python script
exit /b %ERRORLEVEL%
