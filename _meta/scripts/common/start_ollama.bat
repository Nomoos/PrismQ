@echo off
REM start_ollama.bat - Common utility to ensure Ollama is running
REM
REM This script checks if Ollama is running and starts it if necessary.
REM It opens Ollama in a separate CMD window and waits for it to become available.
REM
REM Usage: call ..\common\start_ollama.bat
REM Returns: ERRORLEVEL 0 on success, 1 on failure

echo [INFO] Checking if Ollama is running...

REM Check if Ollama is responding on localhost:11434
curl -s -o nul -w "" http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Ollama is already running
    exit /b 0
)

echo [INFO] Ollama is not running. Starting Ollama in separate window...

REM Check if ollama is installed
where ollama >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Ollama is not installed or not in PATH
    echo [ERROR] Please install Ollama from https://ollama.ai
    exit /b 1
)

REM Start Ollama in a new CMD window
start "Ollama Server" cmd /c "ollama serve"

echo [INFO] Waiting for Ollama to start...

REM Wait up to 30 seconds for Ollama to start
set /a WAIT_COUNT=0
:wait_loop
timeout /t 1 /nobreak >nul
curl -s -o nul -w "" http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Ollama started successfully
    exit /b 0
)
set /a WAIT_COUNT+=1
if %WAIT_COUNT% LSS 30 goto wait_loop

echo [ERROR] Ollama failed to start within 30 seconds
echo [ERROR] Please check the Ollama window for errors
exit /b 1
