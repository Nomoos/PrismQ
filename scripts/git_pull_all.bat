@echo off
setlocal ENABLEDELAYEDEXPANSION

REM === Git Pull All (Recursive mod/ directories) ===
REM This script:
REM  1) Recursively finds all directories named "mod" at any depth
REM  2) Checks if each "mod" directory contains a .git subdirectory
REM  3) Performs git fetch and pull (fast-forward only) for each repository
REM
REM Structure support:
REM   mod/
REM   mod/*/mod
REM   mod/*/mod/*/mod
REM   mod/*/mod/*/mod/*/mod
REM   (and so on, recursively)

REM Ensure Git is installed
where git >NUL 2>&1
if errorlevel 1 (
  echo [ERROR] Git is not installed or not in PATH.
  pause
  exit /b 1
)

REM Determine repo root (start from repository root, not script directory)
for /f "delims=" %%R in ('git rev-parse --show-toplevel 2^>NUL') do set REPO_ROOT=%%R
if not defined REPO_ROOT (
  echo [ERROR] This directory is not inside a Git repository.
  pause
  exit /b 1
)

echo Starting recursive pull from: %REPO_ROOT%
echo.

REM Find every folder named "mod" (any depth), then pull if it has a .git dir
for /f "delims=" %%D in ('dir "%REPO_ROOT%" /b /s /ad ^| findstr /r /c:"\\mod$"') do (
    if exist "%%D\.git" (
        echo ==============================================
        echo Repo: %%D
        pushd "%%D" >nul

        REM Ensure it's a git repo and we can run commands
        git rev-parse --is-inside-work-tree >nul 2>&1
        if errorlevel 1 (
            echo Not a valid git work tree, skipping.
        ) else (
            REM Prune stale remotes, then pull fast-forward only
            git fetch --all --prune
            if errorlevel 1 (
                echo Fetch failed, skipping pull.
            ) else (
                git pull --ff-only
            )
        )
        popd >nul
    ) else (
        REM It's a "mod" folder but not a repo
        REM echo Skipping %%D (no .git directory)
        rem (silent skip; uncomment the line above to see skipped folders)
    )
)

echo.
echo Done.
endlocal
pause
