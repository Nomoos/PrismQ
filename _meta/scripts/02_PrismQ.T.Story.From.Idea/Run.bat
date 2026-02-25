@echo off
REM Run.bat - PrismQ.T.Story.From.Idea
REM Create Story objects from Idea - saves to database
REM Runs continuously with dynamic wait times until cancelled (Ctrl+C or close window)
REM
REM Usage: Run.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"
call ..\common\setup_env.bat "%SCRIPT_DIR%..\..\..\T\Story\From\Idea"
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Story.From.Idea - RUN MODE
echo ========================================
echo.

python ..\..\..\T\Story\From\Idea\src\story_from_idea_interactive.py

if %ERRORLEVEL% NEQ 0 ( echo ERROR: Script execution failed & pause & exit /b 1 )
echo.
pause
exit /b 0
