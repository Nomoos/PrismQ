@echo off
REM Run.bat - PrismQ.T.Idea.From.User
REM Interactive idea creation - saves to database
REM
REM Usage: Run.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Idea\Creation"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Idea.From.User
echo ========================================
echo.

python ..\..\..\T\Idea\Creation\src\idea_creation_interactive.py

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0
