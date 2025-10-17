# Fix for Absolute Path Issue

## Issue
Users encountered errors related to absolute paths when trying to use the PrismQ scripts:
```
No Python at 'C:\Python39\python.exe'
```

This was caused by IDE configuration files (`.idea` directory) being tracked in version control with user-specific absolute paths.

## Root Cause
The `scripts/.idea/` directory contained PyCharm/IntelliJ IDEA configuration files with hardcoded absolute paths:
- `misc.xml`: Contained Python interpreter path `C:\Users\hittl\PROJECTS\VideoMaking\PrismQ\scripts\repo-builder\.venv`
- `scripts.iml`: Contained Python SDK reference with same absolute path
- Other IDE-specific configuration files

When other users cloned the repository, these files would conflict with their local setup.

## Solution
1. **Removed IDE-specific files from version control:**
   - `scripts/.idea/misc.xml`
   - `scripts/.idea/scripts.iml`
   - `scripts/.idea/modules.xml`
   - `scripts/.idea/vcs.xml`
   - `scripts/.idea/inspectionProfiles/profiles_settings.xml`

2. **Enhanced `.gitignore`:**
   - Added comprehensive IDE settings section
   - Now properly excludes `.idea/`, `*.iml`, `.vscode/`, and editor temporary files
   - Prevents future IDE configuration files from being committed

3. **Kept useful files:**
   - Retained `scripts/.idea/.gitignore` as it helps configure IDE behavior within the project

## Impact
- ✅ No more absolute path conflicts between different users' environments
- ✅ Each user can configure their IDE independently
- ✅ Scripts work correctly regardless of Python installation location
- ✅ Better development experience for all contributors

## For Users
If you previously cloned the repository and have the old `.idea` files:
1. Pull the latest changes: `git pull`
2. The problematic files will be automatically removed
3. Your IDE will regenerate configuration files with your local paths

## For New Contributors
- Your IDE (PyCharm, VS Code, etc.) will create its own configuration files
- These files will be automatically ignored by git
- No need to worry about absolute paths in version control
