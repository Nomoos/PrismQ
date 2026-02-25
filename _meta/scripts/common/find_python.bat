@echo off
REM find_python.bat - Locate project Python, installing it if needed
REM Sets PYTHON_EXE in the calling environment
REM
REM Usage: call find_python.bat
REM Returns: ERRORLEVEL 0 on success with PYTHON_EXE set, 1 on failure

REM Derive repo root (3 levels up from _meta\scripts\common\) and set PYTHON_EXE
pushd "%~dp0..\..\..\"
set "PYTHON_EXE=%CD%\.python\python.exe"
popd

REM Check if project's own Python is already installed
if exist "%PYTHON_EXE%" exit /b 0

REM Not installed yet - download and install it
call "%~dp0install_python.bat"
exit /b %ERRORLEVEL%
