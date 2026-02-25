@echo off
REM Run.bat - PrismQ.A.Enhancement
REM Audio enhancement (EQ, compression) - saves to database
REM
REM Usage: Run.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\A\Enhancement"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.A.Enhancement - RUN MODE
echo ========================================
echo.

python ..\..\..\A\Enhancement\src\enhancement_interactive.py

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0
