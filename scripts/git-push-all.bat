@echo off
REM Git Push All - Recursive push wrapper
REM Pushes all repositories to their remotes recursively

setlocal

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "PYTHON_SCRIPT=%SCRIPT_DIR%git-utils\git_push_all.py"

REM Check if Python script exists
if not exist "%PYTHON_SCRIPT%" (
    echo Error: Python script not found at: %PYTHON_SCRIPT%
    exit /b 1
)

REM Run the Python script
python "%PYTHON_SCRIPT%" %*

REM Exit with the same code as the Python script
exit /b %ERRORLEVEL%
