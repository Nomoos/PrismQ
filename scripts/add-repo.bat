@echo off
REM PrismQ Add Repository with Submodule - Run Script
REM Activates virtual environment and runs the add-repo-with-submodule script

setlocal

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%add-repo-with-submodule\.venv"
set "PYTHON_SCRIPT=%SCRIPT_DIR%add-repo-with-submodule\cli.py"
set "SETUP_SCRIPT=%SCRIPT_DIR%add-repo-with-submodule\setup_env.bat"

REM Check if virtual environment exists
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Virtual environment not found. Creating it now...
    echo.
    
    REM Check if setup script exists
    if not exist "%SETUP_SCRIPT%" (
        echo Error: Setup script not found at: %SETUP_SCRIPT%
        echo Cannot create virtual environment automatically
        exit /b 1
    )
    
    REM Run setup script to create virtual environment
    call "%SETUP_SCRIPT%"
    if errorlevel 1 (
        echo.
        echo Error: Failed to create virtual environment
        echo Please check the error messages above
        exit /b 1
    )
    
    echo.
    echo Virtual environment created successfully
    echo.
)

REM Activate virtual environment
call "%VENV_DIR%\Scripts\activate.bat"
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    echo Virtual environment path: %VENV_DIR%
    echo Please ensure the virtual environment was created correctly
    exit /b 1
)

REM Check if Python script exists
if not exist "%PYTHON_SCRIPT%" (
    echo Error: Python script not found at: %PYTHON_SCRIPT%
    echo Please ensure the add-repo-with-submodule is installed correctly
    deactivate
    exit /b 1
)

REM Run the Python script with all arguments passed to this batch file
python "%PYTHON_SCRIPT%" %*

REM Capture exit code
set EXIT_CODE=%ERRORLEVEL%

REM Deactivate virtual environment
deactivate

REM Exit with the same code as the Python script
exit /b %EXIT_CODE%
