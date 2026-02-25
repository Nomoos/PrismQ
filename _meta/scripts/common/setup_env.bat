@echo off
REM setup_env.bat - Set up Python virtual environment for a PrismQ module
REM Uses the project-managed Python in <repo_root>\.python\ (installed automatically)
REM
REM Usage: call setup_env.bat "<MODULE_DIR>"
REM   MODULE_DIR: path to the module directory (contains requirements.txt)
REM On return: virtual environment is activated and ready to use

setlocal enabledelayedexpansion

REM Normalize MODULE_DIR path (resolve any .. segments)
for %%D in ("%~1") do set "MODULE_DIR=%%~fD"
set "VENV_DIR=%MODULE_DIR%\.venv"
set "REQUIREMENTS=%MODULE_DIR%\requirements.txt"
set "VENV_MARKER=%VENV_DIR%\pyvenv.cfg"

echo [INFO] Setting up Python environment...

REM Find or install project Python
call "%~dp0find_python.bat"
if !ERRORLEVEL! NEQ 0 exit /b 1

REM Create virtual environment if it does not exist
if not exist "%VENV_MARKER%" (
    echo [INFO] Creating virtual environment...
    "!PYTHON_EXE!" -m venv "%VENV_DIR%"
    if !ERRORLEVEL! NEQ 0 exit /b 1
)

REM Activate the virtual environment
call "%VENV_DIR%\Scripts\activate.bat"

REM Install dependencies if not yet installed
if exist "%REQUIREMENTS%" if not exist "%VENV_DIR%\.requirements_installed" (
    echo [INFO] Installing dependencies...
    pip install -r "%REQUIREMENTS%" --quiet
    echo Installed > "%VENV_DIR%\.requirements_installed"
)

echo [INFO] Environment ready
endlocal & call "%VENV_DIR%\Scripts\activate.bat"
exit /b 0
