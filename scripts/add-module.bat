@echo off
REM PrismQ Add Module Script (Windows)
REM This script interactively creates a new PrismQ module

setlocal enabledelayedexpansion

echo.
echo ========================================================
echo         PrismQ Module Creation Script
echo ========================================================
echo.

REM Check if we're in a git repository and get the root directory
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo Error: Not in a git repository
    echo Please run this script from the root of the PrismQ repository
    exit /b 1
)

REM Change to repository root to ensure correct relative paths
for /f "delims=" %%i in ('git rev-parse --show-toplevel') do set repo_root=%%i
REM Convert forward slashes to backslashes for Windows
set repo_root=!repo_root:/=\!
cd /d "!repo_root!"
if errorlevel 1 (
    echo Error: Failed to change to repository root
    exit /b 1
)

REM Prompt for input method
echo Choose input method:
echo   1. Enter GitHub repository URL (recommended)
echo   2. Enter module details manually
echo.
set /p input_method="Select option (1 or 2): "

if "!input_method!"=="1" (
    goto :github_url_input
) else if "!input_method!"=="2" (
    goto :manual_input
) else (
    echo Error: Invalid option. Please select 1 or 2
    exit /b 1
)

:github_url_input
echo.
echo Enter the GitHub repository URL (e.g., https://github.com/Nomoos/PrismQ.RepositoryTemplate.git):
echo This can be:
echo   - Full repository URL: https://github.com/Owner/PrismQ.Module.Name.git
echo   - Short format: Owner/PrismQ.Module.Name
set /p github_input="GitHub URL: "

if "!github_input!"=="" (
    echo Error: GitHub URL cannot be empty
    exit /b 1
)

REM Parse GitHub URL to extract owner and repository name
call :parse_github_url "!github_input!" github_owner repo_name

if "!github_owner!"=="" (
    echo Error: Failed to parse GitHub URL
    exit /b 1
)

if "!repo_name!"=="" (
    echo Error: Failed to parse repository name
    exit /b 1
)

REM Derive module name and path from repository name
call :derive_module_path "!repo_name!" module_name module_dir

echo.
echo Parsed from GitHub URL:
echo   Owner: !github_owner!
echo   Repository: !repo_name!
echo   Module Name: !module_name!
echo   Module Path: !module_dir!
echo.

REM Prompt for module description
echo Please enter a short description for the module (optional):
set /p module_description="Description: "

if "!module_description!"=="" (
    set module_description=A PrismQ module
)

REM Construct remote URL
set remote_url=https://github.com/!github_owner!/!repo_name!.git

goto :after_input

:manual_input
REM Prompt for module name
echo.
echo Please enter the module name (e.g., MyNewModule):
echo Note: This will be used as part of the repository name (PrismQ.ModuleName)
set /p module_name="Module name: "

if "!module_name!"=="" (
    echo Error: Module name cannot be empty
    exit /b 1
)

REM Prompt for module description
echo.
echo Please enter a short description for the module:
set /p module_description="Description: "

if "!module_description!"=="" (
    set module_description=A PrismQ module
)

REM Prompt for GitHub username/organization
echo.
echo Please enter your GitHub username or organization (default: Nomoos):
set /p github_owner="GitHub owner: "

if "!github_owner!"=="" (
    set github_owner=Nomoos
)

REM Construct paths and URLs
set module_dir=src/!module_name!
set repo_name=PrismQ.!module_name!
set remote_url=https://github.com/!github_owner!/!repo_name!.git

:after_input

REM Derive remote name
call :derive_remote_name "!remote_url!" remote_name

echo.
echo ========================================================
echo Module Configuration Summary
echo ========================================================
echo Module Name:        !module_name!
echo Module Directory:   !module_dir!
echo Description:        !module_description!
echo Repository Name:    !repo_name!
echo GitHub Owner:       !github_owner!
echo Remote URL:         !remote_url!
echo Remote Name:        !remote_name!
echo ========================================================
echo.

REM Confirm creation
set /p confirm="Create this module? (y/n): "
if /i not "!confirm!"=="y" (
    echo Module creation cancelled
    exit /b 0
)

echo.
echo Creating module structure...

REM Check if module directory already exists
if exist "!module_dir!" (
    echo Error: Module directory '!module_dir!' already exists
    exit /b 1
)

REM Create module directory structure (handling nested paths)
echo Creating directory: !module_dir!

REM Convert forward slashes to backslashes for Windows
set module_dir_win=!module_dir:/=\!

REM Create the directory and all parent directories
mkdir "!module_dir_win!" 2>nul
if errorlevel 1 (
    echo Error: Failed to create module directory
    exit /b 1
)

REM Check if RepositoryTemplate exists to use as template
set template_dir=src\RepositoryTemplate
if exist "!template_dir!" (
    echo Using RepositoryTemplate as base structure...
    
    REM Copy template structure
    xcopy "!template_dir!" "!module_dir_win!" /E /I /Q >nul 2>&1
    if errorlevel 1 (
        echo Warning: Failed to copy template structure, creating basic structure instead
        goto :create_basic_structure
    )
    
    REM Remove template-specific files
    if exist "!module_dir_win!\module.json" del "!module_dir_win!\module.json" >nul 2>&1
    if exist "!module_dir_win!\README.md" del "!module_dir_win!\README.md" >nul 2>&1
    if exist "!module_dir_win!\pyproject.toml" del "!module_dir_win!\pyproject.toml" >nul 2>&1
    
    REM Clean up git-related files if they exist
    if exist "!module_dir_win!\.git" (
        rmdir /s /q "!module_dir_win!\.git" >nul 2>&1
    )
    
    echo Template structure copied successfully
    goto :create_custom_files
) else (
    echo RepositoryTemplate not found, creating basic structure...
    goto :create_basic_structure
)

:create_basic_structure
REM Create subdirectories
mkdir "!module_dir_win!\src" 2>nul
mkdir "!module_dir_win!\tests" 2>nul
mkdir "!module_dir_win!\docs" 2>nul
mkdir "!module_dir_win!\scripts" 2>nul
mkdir "!module_dir_win!\issues" 2>nul
mkdir "!module_dir_win!\issues\new" 2>nul
mkdir "!module_dir_win!\issues\wip" 2>nul
mkdir "!module_dir_win!\issues\done" 2>nul
mkdir "!module_dir_win!\.github" 2>nul
mkdir "!module_dir_win!\.github\ISSUE_TEMPLATE" 2>nul

REM Create basic Python structure
echo Creating Python package structure...
(
echo """!module_name! - !module_description!"""
echo.
echo __version__ = "0.1.0"
) > "!module_dir_win!\src\__init__.py"

(
echo """Main entry point for !module_name!"""
echo.
echo def main^(^):
echo     """Main function"""
echo     print^("!module_name! module initialized"^)
echo.
echo if __name__ == "__main__":
echo     main^(^)
) > "!module_dir_win!\src\main.py"

REM Create .gitignore
(
echo # Python
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo *.so
echo .Python
echo venv/
echo env/
echo ENV/
echo .venv
echo.
echo # IDE
echo .vscode/
echo .idea/
echo *.swp
echo *.swo
echo *~
echo.
echo # Environment
echo .env
echo.
echo # Build
echo dist/
echo build/
echo *.egg-info/
echo.
echo # Tests
echo .pytest_cache/
echo .coverage
echo htmlcov/
) > "!module_dir_win!\.gitignore"

REM Create requirements.txt
(
echo # Core dependencies
echo # Add your dependencies here
) > "!module_dir_win!\requirements.txt"

REM Create LICENSE
(
echo MIT License
echo.
echo Copyright ^(c^) 2025 !github_owner!
echo.
echo Permission is hereby granted, free of charge, to any person obtaining a copy
echo of this software and associated documentation files ^(the "Software"^), to deal
echo in the Software without restriction, including without limitation the rights
echo to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
echo copies of the Software, and to permit persons to whom the Software is
echo furnished to do so, subject to the following conditions:
echo.
echo The above copyright notice and this permission notice shall be included in all
echo copies or substantial portions of the Software.
echo.
echo THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
echo IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
echo FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
echo AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
echo LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
echo OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
echo SOFTWARE.
) > "!module_dir_win!\LICENSE"

:create_custom_files
echo Creating configuration files...

REM Create module.json
echo Creating module.json...
(
echo {
echo   "remote": {
echo     "url": "!remote_url!"
echo   }
echo }
) > "!module_dir_win!\module.json"

REM Create README.md
echo Creating README.md...
(
echo # !repo_name!
echo.
echo !module_description!
echo.
echo ## Purpose
echo.
echo This module is part of the PrismQ ecosystem for AI-powered content generation.
echo.
echo ## Target Platform
echo.
echo - **Operating System**: Windows
echo - **GPU**: NVIDIA RTX 5090 ^(32GB VRAM^)
echo - **CPU**: AMD Ryzen processor
echo - **RAM**: 64GB DDR5
echo.
echo ## Quick Start
echo.
echo ### Setup
echo.
echo ```bash
echo # Windows
echo scripts\setup.bat
echo.
echo # Linux/macOS ^(development only^)
echo ./scripts/setup.sh
echo ```
echo.
echo ### Run
echo.
echo ```bash
echo # Windows
echo scripts\quickstart.bat
echo.
echo # Linux/macOS ^(development only^)
echo ./scripts/quickstart.sh
echo ```
echo.
echo ## Development
echo.
echo See [CONTRIBUTING.md](docs/CONTRIBUTING.md^) for development guidelines.
echo.
echo ## License
echo.
echo This project is licensed under the MIT License - see the LICENSE file for details.
) > "!module_dir_win!\README.md"

REM Create pyproject.toml
echo Creating pyproject.toml...
(
echo [tool.poetry]
echo name = "!module_name!"
echo version = "0.1.0"
echo description = "!module_description!"
echo authors = ["PrismQ ^<noreply@github.com^>"]
echo.
echo [tool.poetry.dependencies]
echo python = "^>=3.11"
echo.
echo [tool.poetry.dev-dependencies]
echo pytest = "^>=7.0"
echo.
echo [build-system]
echo requires = ["poetry-core^>=1.0.0"]
echo build-backend = "poetry.core.masonry.api"
) > "!module_dir_win!\pyproject.toml"

echo.
echo Initializing Git repository...

REM Change to module directory
pushd "!module_dir_win!"

REM Initialize git repository
git init >nul 2>&1
if errorlevel 1 (
    echo Warning: Failed to initialize git repository
    popd
    goto :skip_git
)

echo Setting up Git remote...
git remote add origin "!remote_url!" >nul 2>&1
if errorlevel 1 (
    echo Warning: Failed to add git remote
    echo You can add it manually later with:
    echo   cd !module_dir_win!
    echo   git remote add origin !remote_url!
)

REM Create initial commit
git add . >nul 2>&1
git commit -m "Initial commit: Create !module_name! module" >nul 2>&1
if errorlevel 1 (
    echo Warning: Failed to create initial commit
)

popd

:skip_git

echo.
echo ========================================================
echo Module created successfully!
echo ========================================================
echo.
echo Next steps:
echo   1. Review the generated files in !module_dir_win!
echo   2. Create the GitHub repository at:
echo      !remote_url!
echo   3. Push the initial commit:
echo      cd !module_dir_win!
echo      git push -u origin main
echo   4. Add the module to the main repository:
echo      git add !module_dir_win!
echo      git commit -m "Add !module_name! module"
echo   5. Use scripts\sync-modules.bat to sync the module
echo.

exit /b 0

:parse_github_url
REM Parse GitHub URL to extract owner and repository name
REM Supports formats:
REM   - https://github.com/Owner/RepoName.git
REM   - https://github.com/Owner/RepoName
REM   - git@github.com:Owner/RepoName.git
REM   - Owner/RepoName
set input_url=%~1
set owner_var=%~2
set repo_var=%~3

REM Remove .git suffix if present
set input_url=!input_url:.git=!

REM Handle different URL formats
echo !input_url! | findstr /C:"github.com/" >nul
if !errorlevel! equ 0 (
    REM Full URL format
    set input_url=!input_url:https://github.com/=!
    set input_url=!input_url:http://github.com/=!
    set input_url=!input_url:git@github.com:=!
)

REM Extract owner and repo from "Owner/RepoName" format
for /f "tokens=1,2 delims=/" %%a in ("!input_url!") do (
    set %owner_var%=%%a
    set %repo_var%=%%b
)

goto :eof

:derive_module_path
REM Derive module path from repository name
REM Converts repository name like "PrismQ.IdeaInspiration.Sources" 
REM to module name "IdeaInspiration.Sources" and path "src/IdeaInspiration/src/Sources"
set repo_full_name=%~1
set name_var=%~2
set path_var=%~3

REM Remove "PrismQ." prefix if present
set module_full_name=!repo_full_name:PrismQ.=!

REM Split by dots and build path
REM First component goes to src/, rest go to nested src/ folders
set first_component=
set remaining_components=
set component_count=0

REM Count components and split
for %%a in ("!module_full_name:.=" "!") do (
    set /a component_count+=1
    if !component_count! equ 1 (
        set first_component=%%~a
    ) else (
        if "!remaining_components!"=="" (
            set remaining_components=%%~a
        ) else (
            set remaining_components=!remaining_components!.%%~a
        )
    )
)

REM Build the module path
if "!remaining_components!"=="" (
    REM Single component: src/Component
    set %name_var%=!first_component!
    set %path_var%=src/!first_component!
) else (
    REM Multiple components: src/First/src/Second/src/Third...
    set module_path=src/!first_component!
    for %%a in ("!remaining_components:.=" "!") do (
        set module_path=!module_path!/src/%%~a
    )
    set %name_var%=!module_full_name!
    set %path_var%=!module_path!
)

goto :eof

:derive_remote_name
REM Derive remote name from repository URL
REM Converts URL like "https://github.com/Nomoos/PrismQ.RepositoryTemplate.git"
REM to "prismq-repositorytemplate"
set url=%~1
set result_var=%~2

REM Extract repo name from URL (remove .git and get last part)
set repo_name=!url:.git=!
for %%a in ("!repo_name!") do set repo_name=%%~nxa

REM Convert to lowercase and replace dots/underscores with hyphens
set repo_name=!repo_name:.=-!
set repo_name=!repo_name:_=-!

REM Simple lowercase conversion
set repo_name=!repo_name:A=a!
set repo_name=!repo_name:B=b!
set repo_name=!repo_name:C=c!
set repo_name=!repo_name:D=d!
set repo_name=!repo_name:E=e!
set repo_name=!repo_name:F=f!
set repo_name=!repo_name:G=g!
set repo_name=!repo_name:H=h!
set repo_name=!repo_name:I=i!
set repo_name=!repo_name:J=j!
set repo_name=!repo_name:K=k!
set repo_name=!repo_name:L=l!
set repo_name=!repo_name:M=m!
set repo_name=!repo_name:N=n!
set repo_name=!repo_name:O=o!
set repo_name=!repo_name:P=p!
set repo_name=!repo_name:Q=q!
set repo_name=!repo_name:R=r!
set repo_name=!repo_name:S=s!
set repo_name=!repo_name:T=t!
set repo_name=!repo_name:U=u!
set repo_name=!repo_name:V=v!
set repo_name=!repo_name:W=w!
set repo_name=!repo_name:X=x!
set repo_name=!repo_name:Y=y!
set repo_name=!repo_name:Z=z!

set %result_var%=!repo_name!
goto :eof
