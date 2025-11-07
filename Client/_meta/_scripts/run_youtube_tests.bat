@echo off
REM PrismQ Backend - YouTube Channel Download Tests Runner
REM Double-click this file to run the tests

title YouTube Channel Download Tests

echo.
echo ============================================
echo   YouTube Channel Download Tests
echo ============================================
echo.

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM Navigate to the Client/_meta/_scripts directory and run PowerShell script
cd /d "%SCRIPT_DIR%"

REM Check if PowerShell is available
where powershell >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PowerShell not found
    echo Please ensure PowerShell is installed
    pause
    exit /b 1
)

REM Run the PowerShell script
echo Running PowerShell script...
echo.
powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%run_youtube_tests.ps1" %*

REM Preserve exit code
set EXIT_CODE=%ERRORLEVEL%

REM Pause at the end (PowerShell script already pauses, but just in case)
if %EXIT_CODE% NEQ 0 (
    echo.
    echo Tests completed with errors. Check output above.
    pause
)

exit /b %EXIT_CODE%
