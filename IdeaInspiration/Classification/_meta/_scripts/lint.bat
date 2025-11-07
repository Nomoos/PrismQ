@echo off
REM PrismQ Module Lint Script for Windows
REM Target: Windows with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

echo =====================================
echo PrismQ Module Lint
echo =====================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Running code quality checks...
echo Target: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM
echo.

REM Run flake8 check (PEP 8 linting)
echo Running Flake8 linting (PEP 8)...
flake8 prismq/

if errorlevel 1 (
    echo.
    echo =====================================
    echo Linting failed!
    echo =====================================
    echo.
    pause
    exit /b 1
)

echo.
echo Running MyPy type checking (PEP 484, 526, 544)...
mypy prismq/

if errorlevel 1 (
    echo.
    echo =====================================
    echo Type checking failed!
    echo =====================================
    echo.
    pause
    exit /b 1
)

echo.
echo =====================================
echo Linting Complete!
echo =====================================
echo All code quality checks passed.
echo.

pause
