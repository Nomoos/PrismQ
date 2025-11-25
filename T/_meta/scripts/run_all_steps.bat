@echo off
REM PrismQ.T - Run All Steps Sequentially
REM This script runs all workflow steps in sequence
REM Each step runs as a separate process
REM 
REM Usage: run_all_steps.bat

echo ========================================
echo PrismQ.T - Run All Steps
echo ========================================

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo.
echo Starting Step 1: Create Idea...
call step1_create_idea.bat
if %ERRORLEVEL% NEQ 0 goto :error

echo.
echo Starting Step 2: Generate Title...
call step2_generate_title.bat
if %ERRORLEVEL% NEQ 0 goto :error

echo.
echo Starting Step 3: Generate Script...
call step3_generate_script.bat
if %ERRORLEVEL% NEQ 0 goto :error

echo.
echo Starting Step 4: Iterate on Script...
call step4_iterate_script.bat
if %ERRORLEVEL% NEQ 0 goto :error

echo.
echo Starting Step 5: Export Content...
call step5_export.bat
if %ERRORLEVEL% NEQ 0 goto :error

echo.
echo ========================================
echo All steps completed successfully!
echo ========================================
goto :end

:error
echo.
echo ========================================
echo ERROR: Workflow stopped due to error
echo ========================================

:end
pause
