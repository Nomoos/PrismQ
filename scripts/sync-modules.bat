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

REM Discover modules from REMOTE.md files
call :discover_modules_from_remote_files

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

:discover_modules_from_remote_files
REM Discover modules with REMOTE.md files
for /d %%d in (src\*) do (
    if exist "%%d\src" (
        if exist "%%d\REMOTE.md" (
            call :read_and_add_module "%%d"
        )
    )
)
goto :eof

:read_and_add_module
set module_dir=%~1
set remote_file=%module_dir%\REMOTE.md
set remote_url_found=
set remote_name_found=
set branch_found=

REM Read REMOTE.md file line by line
for /f "usebackq tokens=1,* delims==" %%a in ("%remote_file%") do (
    if "%%a"=="REMOTE_URL" set remote_url_found=%%b
    if "%%a"=="REMOTE_NAME" set remote_name_found=%%b
    if "%%a"=="BRANCH" set branch_found=%%b
)

REM Remove spaces from values
set remote_url_found=!remote_url_found: =!
set remote_name_found=!remote_name_found: =!
set branch_found=!branch_found: =!

REM Validate that all required fields are present
if "!remote_url_found!"=="" (
    echo WARNING: %module_dir%\REMOTE.md is missing REMOTE_URL configuration
    goto :eof
)
if "!remote_name_found!"=="" (
    echo WARNING: %module_dir%\REMOTE.md is missing REMOTE_NAME configuration
    goto :eof
)
if "!branch_found!"=="" (
    echo WARNING: %module_dir%\REMOTE.md is missing BRANCH configuration
    goto :eof
)

REM Check if module already configured in modules array
set already_configured=0
for /l %%i in (0,1,%module_count%) do (
    if defined modules[%%i] (
        for /f "tokens=1 delims=|" %%a in ("!modules[%%i]!") do (
            if "%%a"=="%module_dir%" set already_configured=1
        )
    )
)

REM Add to modules if not already configured
if !already_configured!==0 (
    set /a module_count+=1
    set "modules[!module_count!]=%module_dir%|!remote_name_found!|!remote_url_found!|!branch_found!"
    echo Discovered module from REMOTE.md: %module_dir%
)
goto :eof

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
) else (
    REM Check for REMOTE.md and validate/set origin
    if exist "!module_path!\REMOTE.md" (
        call :validate_and_set_origin "!module_path!" "!remote_url!"
    ) else (
        echo WARNING: !module_path!\REMOTE.md not found
        echo The module repository may not have proper remote configuration
    )
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

:validate_and_set_origin
set validate_module_path=%~1
set validate_remote_url=%~2

REM Read REMOTE.md to get configuration
set remote_md_file=!validate_module_path!\REMOTE.md
set remote_url_from_file=

for /f "usebackq tokens=1,* delims==" %%a in ("!remote_md_file!") do (
    if "%%a"=="REMOTE_URL" set remote_url_from_file=%%b
)

REM Remove spaces
set remote_url_from_file=!remote_url_from_file: =!

REM Validate REMOTE.md has proper URL
if "!remote_url_from_file!"=="" (
    echo WARNING: !remote_md_file! is missing REMOTE_URL
) else (
    REM Check if we're in the module directory to set origin
    pushd !validate_module_path! 2>nul
    if errorlevel 1 goto :validate_end
    
    REM Check if this is a git repository (has .git)
    if exist ".git" (
        REM Get current origin URL
        for /f "delims=" %%i in ('git remote get-url origin 2^>nul') do set current_origin=%%i
        
        if "!current_origin!"=="" (
            REM No origin set, add it
            echo Setting origin for !validate_module_path! to !remote_url_from_file!
            git remote add origin "!remote_url_from_file!"
        ) else if not "!current_origin!"=="!remote_url_from_file!" (
            REM Origin exists but different, update it
            echo Updating origin for !validate_module_path! to !remote_url_from_file!
            git remote set-url origin "!remote_url_from_file!"
        )
    )
    
    popd
)

:validate_end
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
