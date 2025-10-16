@echo off
REM PrismQ Repository Builder - Run Script
REM Activates virtual environment and runs the repo_builder.py script

setlocal

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%repo-builder\.venv"
set "PYTHON_SCRIPT=%SCRIPT_DIR%repo-builder\repo_builder.py"

REM Check if virtual environment exists
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Error: Virtual environment not found
    echo Please run setup_env.bat first to create the virtual environment
    exit /b 1
)

REM Activate virtual environment
call "%VENV_DIR%\Scripts\activate.bat"

REM Run the Python script with all arguments passed to this batch file
python "%PYTHON_SCRIPT%" %*

REM Capture exit code
set EXIT_CODE=%ERRORLEVEL%

REM Deactivate virtual environment
deactivate

REM Exit with the same code as the Python script
exit /b %EXIT_CODE%
