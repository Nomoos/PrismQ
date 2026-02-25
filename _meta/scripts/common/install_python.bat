@echo off
REM install_python.bat - Download and install Python 3.11 embedded package
REM Installs to <repo_root>\.python\ (gitignored, shared by all modules)
REM Sets PYTHON_EXE on success
REM
REM Usage: call install_python.bat
REM Returns: ERRORLEVEL 0 on success, 1 on failure

setlocal enabledelayedexpansion

REM Compute repo root (3 levels up from _meta\scripts\common\)
pushd "%~dp0..\..\..\"
set "REPO_ROOT=%CD%"
popd

set "PYTHON_DIR=%REPO_ROOT%\.python"
set "PYTHON_EXE_PATH=%PYTHON_DIR%\python.exe"
set "PYTHON_VERSION=3.10.9"
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-embed-amd64.zip"
set "GET_PIP_URL=https://bootstrap.pypa.io/get-pip.py"
set "PYTHON_ZIP=%TEMP%\prismq_python_embed.zip"
set "GET_PIP=%TEMP%\prismq_get_pip.py"

echo [INFO] Installing Python %PYTHON_VERSION% (embedded)...
echo [INFO] Destination: %PYTHON_DIR%

REM Create destination directory
mkdir "%PYTHON_DIR%" 2>nul

REM Download Python embeddable package
echo [INFO] Downloading Python %PYTHON_VERSION%...
powershell -NoProfile -NonInteractive -Command ^
    "try { Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_ZIP%' -UseBasicParsing; exit 0 } catch { Write-Host $_.Exception.Message; exit 1 }"
if !ERRORLEVEL! NEQ 0 (
    echo ERROR: Failed to download Python. Check your internet connection.
    echo        URL: %PYTHON_URL%
    rmdir /s /q "%PYTHON_DIR%" 2>nul
    exit /b 1
)

REM Extract the package
echo [INFO] Extracting Python...
powershell -NoProfile -NonInteractive -Command ^
    "try { Expand-Archive -Path '%PYTHON_ZIP%' -DestinationPath '%PYTHON_DIR%' -Force; exit 0 } catch { Write-Host $_.Exception.Message; exit 1 }"
if !ERRORLEVEL! NEQ 0 (
    echo ERROR: Failed to extract Python.
    del /q "%PYTHON_ZIP%" 2>nul
    rmdir /s /q "%PYTHON_DIR%" 2>nul
    exit /b 1
)
del /q "%PYTHON_ZIP%" 2>nul

REM Enable site-packages (required for pip and venv)
echo [INFO] Configuring Python...
for %%F in ("%PYTHON_DIR%\python3*._pth") do (
    powershell -NoProfile -NonInteractive -Command ^
        "(Get-Content '%%F') -replace '#import site', 'import site' | Set-Content '%%F'"
)

REM Download pip installer
echo [INFO] Downloading pip...
powershell -NoProfile -NonInteractive -Command ^
    "try { Invoke-WebRequest -Uri '%GET_PIP_URL%' -OutFile '%GET_PIP%' -UseBasicParsing; exit 0 } catch { Write-Host $_.Exception.Message; exit 1 }"
if !ERRORLEVEL! NEQ 0 (
    echo ERROR: Failed to download pip installer. Check your internet connection.
    rmdir /s /q "%PYTHON_DIR%" 2>nul
    exit /b 1
)

REM Install pip
echo [INFO] Installing pip...
"%PYTHON_DIR%\python.exe" "%GET_PIP%" --quiet
if !ERRORLEVEL! NEQ 0 (
    echo ERROR: Failed to install pip.
    del /q "%GET_PIP%" 2>nul
    rmdir /s /q "%PYTHON_DIR%" 2>nul
    exit /b 1
)
del /q "%GET_PIP%" 2>nul

echo [INFO] Python %PYTHON_VERSION% installed successfully.
endlocal & set "PYTHON_EXE=%PYTHON_EXE_PATH%"
exit /b 0
