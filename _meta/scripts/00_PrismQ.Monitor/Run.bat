@echo off
REM Run.bat - PrismQ Pipeline Monitor
REM Prints story state distribution every 30 seconds

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

title PrismQ Monitor

set PYTHONIOENCODING=utf-8
chcp 65001 >nul
"C:\Users\hittl\PROJECTS\VideoMaking\PrismQ\.python\python.exe" -X utf8 "%SCRIPT_DIR%monitor.py"

pause
exit /b 0
