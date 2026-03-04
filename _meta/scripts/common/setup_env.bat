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

REM Remove broken virtual environment (marker exists but Python executable is missing)
if exist "%VENV_MARKER%" (
    if not exist "%VENV_DIR%\Scripts\python.exe" (
        echo [INFO] Virtual environment is broken, removing and recreating...
        rmdir /s /q "%VENV_DIR%"
    )
)

REM Create virtual environment if it does not exist
if not exist "%VENV_MARKER%" (
    echo [INFO] Creating virtual environment...
    REM Ensure virtualenv is installed (may be missing if Python was installed before PR345)
    "!PYTHON_EXE!" -m virtualenv --version >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        echo [INFO] Installing virtualenv...
        "!PYTHON_EXE!" -m pip install virtualenv --quiet
        if !ERRORLEVEL! NEQ 0 exit /b 1
    )
    "!PYTHON_EXE!" -m virtualenv "%VENV_DIR%"
    if !ERRORLEVEL! NEQ 0 exit /b 1
)

REM Activate the virtual environment
call "%VENV_DIR%\Scripts\activate.bat"

REM Install (or reinstall) dependencies when requirements.txt has changed
set "NEEDS_INSTALL=0"
if exist "%REQUIREMENTS%" (
    if not exist "%VENV_DIR%\.requirements_installed" (
        set "NEEDS_INSTALL=1"
    ) else (
        fc "%REQUIREMENTS%" "%VENV_DIR%\.requirements_installed" >nul 2>&1
        if !ERRORLEVEL! NEQ 0 set "NEEDS_INSTALL=1"
    )
)
if "!NEEDS_INSTALL!"=="1" (
    echo [INFO] Installing dependencies...
    pip install -r "%REQUIREMENTS%" --quiet
    if !ERRORLEVEL! NEQ 0 exit /b 1
    copy /y "%REQUIREMENTS%" "%VENV_DIR%\.requirements_installed" >nul
)

REM ── Ollama model check ──────────────────────────────────────────────────────
where ollama >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Checking Ollama AI models...
    for %%M in (qwen3:8b qwen3:14b qwen3:32b) do (
        ollama list 2>nul | findstr /i /c:"%%M" >nul
        if errorlevel 1 (
            echo [INFO] Pulling model: %%M
            ollama pull %%M
        ) else (
            echo [INFO] Model ready: %%M
        )
    )
) else (
    echo [INFO] Ollama not found - skipping model check
)

echo [INFO] Environment ready
endlocal & call "%VENV_DIR%\Scripts\activate.bat"
exit /b 0
