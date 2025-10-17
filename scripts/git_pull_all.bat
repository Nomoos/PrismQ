@echo off
setlocal ENABLEDELAYEDEXPANSION

REM === Git Pull All (with submodules to latest remote commits) ===
REM This script:
REM  1) Jumps to the repo root (even if run from a subfolder)
REM  2) Fetches & pulls the main repo
REM  3) Syncs submodule URLs
REM  4) Fetches in every submodule
REM  5) Updates submodules to the latest commits on their configured remote branches

REM Ensure Git is installed
where git >NUL 2>&1
if errorlevel 1 (
  echo [ERROR] Git is not installed or not in PATH.
  pause
  exit /b 1
)

REM Determine repo root
for /f "delims=" %%R in ('git rev-parse --show-toplevel 2^>NUL') do set REPO_ROOT=%%R
if not defined REPO_ROOT (
  echo [ERROR] This directory is not inside a Git repository.
  pause
  exit /b 1
)

pushd "%REPO_ROOT%"
echo === Repository: %REPO_ROOT% ===

echo.
echo --- Fetching all remotes (main repo) ---
git fetch --all --prune
if errorlevel 1 (
  echo [WARN] Fetch failed in main repo.
)

echo.
echo --- Pulling main repo (rebase) ---
git pull --rebase
if errorlevel 1 (
  echo [WARN] Pull (rebase) failed in main repo. Trying plain pull...
  git pull
)

echo.
echo --- Syncing submodule URLs ---
git submodule sync --recursive

echo.
echo --- Fetching inside each submodule (recursive) ---
git submodule foreach --recursive "git fetch --all --prune || echo [WARN] Fetch failed in submodule: $name"

echo.
echo --- Initializing and updating submodules to latest remote branches ---
git submodule update --init --recursive --remote

echo.
echo === Done ===
popd
pause
