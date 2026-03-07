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

REM ── Ollama performance settings for RTX 5090 (32 GB VRAM) ──────────────────
REM FLASH_ATTN=1          enables flash attention (reduces KV cache overhead)
REM KV_CACHE_TYPE=q8_0    quantizes KV cache → saves ~4-5 GB on qwen3:32b
REM MAX_LOADED_MODELS=2   keeps qwen3:32b + qwen3:14b both hot in VRAM simultaneously
REM NUM_PARALLEL=4        saturates 4 review workers + 4 step-03 workers
REM KEEP_ALIVE=-1         never evict models; they stay loaded until Ollama stops
REM These are also set as permanent Windows User env vars via SetEnvironmentVariable
if not defined OLLAMA_FLASH_ATTN         set OLLAMA_FLASH_ATTN=1
if not defined OLLAMA_KV_CACHE_TYPE      set OLLAMA_KV_CACHE_TYPE=q8_0
if not defined OLLAMA_MAX_LOADED_MODELS  set OLLAMA_MAX_LOADED_MODELS=2
if not defined OLLAMA_NUM_PARALLEL       set OLLAMA_NUM_PARALLEL=4
if not defined OLLAMA_KEEP_ALIVE         set OLLAMA_KEEP_ALIVE=-1

REM Start Ollama in a new CMD window
start "Ollama Server" cmd /c "set OLLAMA_FLASH_ATTN=%OLLAMA_FLASH_ATTN% && set OLLAMA_KV_CACHE_TYPE=%OLLAMA_KV_CACHE_TYPE% && set OLLAMA_MAX_LOADED_MODELS=%OLLAMA_MAX_LOADED_MODELS% && set OLLAMA_NUM_PARALLEL=%OLLAMA_NUM_PARALLEL% && set OLLAMA_KEEP_ALIVE=%OLLAMA_KEEP_ALIVE% && ollama serve"

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
