@echo off
REM PrismQ Module Sync Script (Windows)
REM This script syncs first-level modules from their remote repositories using git subtree
REM Each module can be maintained in a separate repository and synced to the main PrismQ repo

setlocal enabledelayedexpansion

REM Configuration: Module definitions
REM Format: module_path|remote_name|remote_url|branch
REM NOTE: If a module has a REMOTE.md file, it will be read automatically
set "modules[0]=src/RepositoryTemplate|repositorytemplate-remote|https://github.com/Nomoos/PrismQ.RepositoryTemplate.git|main"
set "modules[1]=src/IdeaInspiration|ideainspiration-remote|https://github.com/Nomoos/PrismQ.IdeaInspiration.git|main"
REM Add more modules as needed

set module_count=2

REM Check for help argument
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="--list" goto :list_modules
if "%1"=="-l" goto :list_modules

echo ╔════════════════════════════════════════════════════════╗
echo ║        PrismQ Module Synchronization Script           ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check if we're in a git repository
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo Error: Not in a git repository
    exit /b 1
)

REM Determine operation mode
set sync_all=1
set specific_module=

if not "%1"=="" (
    if not "%1"=="--all" (
        if not "%1"=="-a" (
            set sync_all=0
            set specific_module=%1
        )
    )
)

set sync_errors=0

if %sync_all%==1 (
    echo Syncing all configured modules...
    echo.
    
    for /l %%i in (0,1,%module_count%) do (
        if defined modules[%%i] (
            call :sync_module "!modules[%%i]!"
        )
    )
) else (
    set found=0
    for /l %%i in (0,1,%module_count%) do (
        if defined modules[%%i] (
            for /f "tokens=1 delims=|" %%a in ("!modules[%%i]!") do (
                if "%%a"=="%specific_module%" (
                    set found=1
                    call :sync_module "!modules[%%i]!"
                )
            )
        )
    )
    
    if !found!==0 (
        echo Error: Module '%specific_module%' not found in configuration
        echo Use --list to see configured modules
        exit /b 1
    )
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if %sync_errors%==0 (
    echo ✓ All modules synced successfully
    exit /b 0
) else (
    echo ✗ %sync_errors% module(s) failed to sync
    echo Note: Some modules may not have remote repositories yet
    exit /b 1
)

:sync_module
set module_config=%~1
for /f "tokens=1,2,3,4 delims=|" %%a in ("%module_config%") do (
    set module_path=%%a
    set remote_name=%%b
    set remote_url=%%c
    set branch=%%d
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo Syncing module: !module_path!
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REM Check if module directory exists
if not exist "!module_path!" (
    echo Module directory '!module_path!' does not exist yet
    echo This module will be added on first sync from remote
)

REM Check if remote exists
git remote | findstr /x "!remote_name!" >nul 2>&1
if errorlevel 1 (
    echo Adding remote '!remote_name!' -^> !remote_url!
    git remote add "!remote_name!" "!remote_url!"
) else (
    echo Remote '!remote_name!' already exists
)

REM Fetch from remote
echo Fetching from !remote_name!...
git fetch "!remote_name!" "!branch!" >nul 2>&1
if errorlevel 1 (
    echo Failed to fetch from !remote_name!
    echo Repository may not exist yet: !remote_url!
    set /a sync_errors+=1
    goto :eof
)

REM Pull updates using subtree
echo Pulling updates to !module_path!...
git subtree pull --prefix="!module_path!" "!remote_name!" "!branch!" --squash
if errorlevel 1 (
    echo ✗ Failed to sync !module_path!
    set /a sync_errors+=1
) else (
    echo ✓ Successfully synced !module_path!
)
goto :eof

:show_help
echo Usage: %0 [OPTIONS] [MODULE_PATH]
echo.
echo Options:
echo   --help, -h        Show this help message
echo   --list, -l        List configured modules
echo   --all, -a         Sync all configured modules (default)
echo.
echo Arguments:
echo   MODULE_PATH       Sync only the specified module (e.g., src/RepositoryTemplate)
echo.
echo Examples:
echo   %0                          # Sync all modules
echo   %0 --all                    # Sync all modules
echo   %0 src/RepositoryTemplate   # Sync only RepositoryTemplate module
exit /b 0

:list_modules
echo Configured modules:
echo.
for /l %%i in (0,1,%module_count%) do (
    if defined modules[%%i] (
        for /f "tokens=1,2,3,4 delims=|" %%a in ("!modules[%%i]!") do (
            echo   • %%a
            echo     Remote: %%b (%%c)
            echo     Branch: %%d
            echo.
        )
    )
)
exit /b 0
