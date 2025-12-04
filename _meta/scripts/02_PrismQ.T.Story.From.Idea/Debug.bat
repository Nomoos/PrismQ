@echo off
REM Debug.bat - PrismQ.T.Story.From.Idea
REM Sets up virtual environment and opens project in PyCharm for debugging
REM
REM Usage: Debug.bat

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM PyCharm executable path
set PYCHARM_EXE=C:\Program Files\JetBrains\PyCharm 2025.2.3\bin\pycharm64.exe

REM Check if PyCharm exists
if not exist "%PYCHARM_EXE%" (
    echo ERROR: PyCharm not found at: %PYCHARM_EXE%
    echo Please update PYCHARM_EXE path in this script.
    pause
    exit /b 1
)

call :setup_env
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

call :setup_pycharm
if %ERRORLEVEL% NEQ 0 ( pause & exit /b 1 )

echo ========================================
echo PrismQ.T.Story.From.Idea - DEBUG MODE
echo ========================================
echo.
echo Opening project in PyCharm...
echo.

REM Open PyCharm with the module directory
start "" "%PYCHARM_EXE%" "%MODULE_DIR%"

echo PyCharm is starting with the project.
echo.
echo Run configuration 'Run.bat Debug' has been created.
echo Use it to debug story_from_idea_interactive.py
echo.
pause
exit /b 0

:setup_env
setlocal enabledelayedexpansion
set MODULE_DIR=%SCRIPT_DIR%..\..\..\..\T\Story\From\Idea
set VENV_DIR=%MODULE_DIR%\.venv
set REQUIREMENTS=%MODULE_DIR%\requirements.txt
set VENV_MARKER=%VENV_DIR%\pyvenv.cfg
echo [INFO] Setting up Python environment...
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 ( echo ERROR: Python not found & exit /b 1 )
if not exist "%VENV_MARKER%" (
    echo [INFO] Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if %ERRORLEVEL% NEQ 0 exit /b 1
)
call "%VENV_DIR%\Scripts\activate.bat"
if exist "%REQUIREMENTS%" if not exist "%VENV_DIR%\.requirements_installed" (
    echo [INFO] Installing dependencies...
    pip install -r "%REQUIREMENTS%" --quiet
    echo Installed > "%VENV_DIR%\.requirements_installed"
)
echo [INFO] Environment ready
endlocal & (
    set "MODULE_DIR=%MODULE_DIR%"
    set "VENV_DIR=%VENV_DIR%"
    call "%VENV_DIR%\Scripts\activate.bat"
)
exit /b 0

:setup_pycharm
echo [INFO] Setting up PyCharm configuration...

REM Create .idea directory if it doesn't exist
if not exist "%MODULE_DIR%\.idea" mkdir "%MODULE_DIR%\.idea"

REM Create misc.xml with Python interpreter configuration
echo ^<?xml version="1.0" encoding="UTF-8"?^> > "%MODULE_DIR%\.idea\misc.xml"
echo ^<project version="4"^> >> "%MODULE_DIR%\.idea\misc.xml"
echo   ^<component name="ProjectRootManager" version="2" project-jdk-name="Python 3 (.venv)" project-jdk-type="Python SDK" /^> >> "%MODULE_DIR%\.idea\misc.xml"
echo ^</project^> >> "%MODULE_DIR%\.idea\misc.xml"

REM Create modules.xml
echo ^<?xml version="1.0" encoding="UTF-8"?^> > "%MODULE_DIR%\.idea\modules.xml"
echo ^<project version="4"^> >> "%MODULE_DIR%\.idea\modules.xml"
echo   ^<component name="ProjectModuleManager"^> >> "%MODULE_DIR%\.idea\modules.xml"
echo     ^<modules^> >> "%MODULE_DIR%\.idea\modules.xml"
echo       ^<module fileurl="file://$PROJECT_DIR$/.idea/PrismQ.T.Story.From.Idea.iml" filepath="$PROJECT_DIR$/.idea/PrismQ.T.Story.From.Idea.iml" /^> >> "%MODULE_DIR%\.idea\modules.xml"
echo     ^</modules^> >> "%MODULE_DIR%\.idea\modules.xml"
echo   ^</component^> >> "%MODULE_DIR%\.idea\modules.xml"
echo ^</project^> >> "%MODULE_DIR%\.idea\modules.xml"

REM Create .iml file
echo ^<?xml version="1.0" encoding="UTF-8"?^> > "%MODULE_DIR%\.idea\PrismQ.T.Story.From.Idea.iml"
echo ^<module type="PYTHON_MODULE" version="4"^> >> "%MODULE_DIR%\.idea\PrismQ.T.Story.From.Idea.iml"
echo   ^<component name="NewModuleRootManager"^> >> "%MODULE_DIR%\.idea\PrismQ.T.Story.From.Idea.iml"
echo     ^<content url="file://$MODULE_DIR$"^> >> "%MODULE_DIR%\.idea\PrismQ.T.Story.From.Idea.iml"
echo       ^<sourceFolder url="file://$MODULE_DIR$/src" isTestSource="false" /^> >> "%MODULE_DIR%\.idea\PrismQ.T.Story.From.Idea.iml"
echo     ^</content^> >> "%MODULE_DIR%\.idea\PrismQ.T.Story.From.Idea.iml"
echo     ^<orderEntry type="inheritedJdk" /^> >> "%MODULE_DIR%\.idea\PrismQ.T.Story.From.Idea.iml"
echo     ^<orderEntry type="sourceFolder" forTests="false" /^> >> "%MODULE_DIR%\.idea\PrismQ.T.Story.From.Idea.iml"
echo   ^</component^> >> "%MODULE_DIR%\.idea\PrismQ.T.Story.From.Idea.iml"
echo ^</module^> >> "%MODULE_DIR%\.idea\PrismQ.T.Story.From.Idea.iml"

REM Create runConfigurations directory
if not exist "%MODULE_DIR%\.idea\runConfigurations" mkdir "%MODULE_DIR%\.idea\runConfigurations"

REM Create run configuration for debugging
echo ^<?xml version="1.0" encoding="UTF-8"?^> > "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo ^<component name="ProjectRunConfigurationManager"^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo   ^<configuration default="false" name="Run.bat Debug" type="PythonConfigurationType" factoryName="Python"^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo     ^<module name="PrismQ.T.Story.From.Idea" /^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo     ^<option name="INTERPRETER_OPTIONS" value="" /^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo     ^<option name="PARENT_ENVS" value="true" /^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo     ^<option name="SDK_HOME" value="$PROJECT_DIR$/.venv/Scripts/python.exe" /^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo     ^<option name="WORKING_DIRECTORY" value="$PROJECT_DIR$/src" /^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo     ^<option name="IS_MODULE_SDK" value="false" /^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo     ^<option name="ADD_CONTENT_ROOTS" value="true" /^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo     ^<option name="ADD_SOURCE_ROOTS" value="true" /^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo     ^<option name="SCRIPT_NAME" value="$PROJECT_DIR$/src/story_from_idea_interactive.py" /^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo     ^<option name="PARAMETERS" value="" /^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo     ^<option name="SHOW_COMMAND_LINE" value="true" /^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo     ^<option name="EMULATE_TERMINAL" value="true" /^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo     ^<option name="MODULE_MODE" value="false" /^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo     ^<option name="REDIRECT_INPUT" value="false" /^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo     ^<option name="INPUT_FILE" value="" /^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo     ^<method v="2" /^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo   ^</configuration^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"
echo ^</component^> >> "%MODULE_DIR%\.idea\runConfigurations\Run_bat_Debug.xml"

echo [INFO] PyCharm configuration created
exit /b 0
