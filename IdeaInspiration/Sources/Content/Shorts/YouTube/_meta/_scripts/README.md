# Quick Start Scripts

This directory contains quick start and setup scripts for the YouTube Shorts Source module.

## Scripts

### Setup Scripts

**Windows (PowerShell): `setup_module.ps1` (Recommended)**
- Creates Python virtual environment
- Installs all dependencies from requirements.txt
- Optionally creates .env file from .env.example
- Enhanced error handling and colored output
- Better for AI assistants (GitHub Copilot/ChatGPT)

**Windows (Batch): `setup_module.bat`**
- Legacy batch script with same functionality as setup_module.ps1
- Use if you cannot run PowerShell scripts

**Linux: `setup_module.sh`**
- Creates Python virtual environment
- Installs all dependencies from requirements.txt
- Optionally creates .env file from .env.example
- Note: Linux support is for testing purposes only; Windows is the primary target platform

### Run Scripts

**Windows (PowerShell): `run_module.ps1` (Recommended)**
- Activates virtual environment
- Creates .env from .env.example if .env doesn't exist
- Prompts to open .env in notepad for configuration (first run only)
- Runs the YouTube Shorts scraper CLI with help and examples
- Enhanced error handling and colored output
- Better for AI assistants (GitHub Copilot/ChatGPT)

**Windows (Batch): `run_module.bat`**
- Legacy batch script with same functionality as run_module.ps1
- Use if you cannot run PowerShell scripts

**Linux: `run_module.sh`**
- Activates virtual environment
- Creates .env from .env.example if .env doesn't exist
- Prompts user to configure .env (first run only)
- Runs the YouTube Shorts scraper CLI with help and examples
- Note: Linux support is for testing purposes only; Windows is the primary target platform

## Why PowerShell?

For Windows users, PowerShell scripts (`.ps1`) are **recommended** over batch scripts (`.bat`) because:

1. **Better Error Handling**: PowerShell provides structured error handling with try/catch blocks
2. **Colored Output**: Enhanced readability with color-coded status messages
3. **Modern Windows Standard**: PowerShell is the modern scripting standard for Windows
4. **AI Assistant Friendly**: Better structured syntax for GitHub Copilot and ChatGPT to understand and modify
5. **More Powerful**: Advanced features like object manipulation, better string handling, and integrated .NET access
6. **Cross-Version Compatible**: Works on PowerShell 5.1+ (built into Windows) and PowerShell 7+

### Enabling PowerShell Scripts

If you get an error about script execution being disabled, run this once:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

This allows locally created scripts to run while still protecting against untrusted remote scripts. Note: This does not require administrator privileges as it only affects the current user.

## Usage

### First Time Setup

**Windows (PowerShell - Recommended):**
```powershell
cd Sources\Content\Shorts\YouTube
.\_meta\_scripts\setup_module.ps1
.\_meta\_scripts\run_module.ps1
```

**Windows (Batch - Legacy):**
```cmd
cd Sources\Content\Shorts\YouTube
_meta\_scripts\setup_module.bat
_meta\_scripts\run_module.bat
```

**Linux:**
```bash
cd Sources/Content/Shorts/YouTube
_meta/_scripts/setup_module.sh
_meta/_scripts/run_module.sh
```

### Subsequent Runs

After initial setup, you can just run:

**Windows (PowerShell - Recommended):**
```powershell
.\_meta\_scripts\run_module.ps1
```

**Windows (Batch - Legacy):**
```cmd
_meta\_scripts\run_module.bat
```

**Linux:**
```bash
_meta/_scripts/run_module.sh
```

## Configuration

The run scripts will automatically:
1. Check for virtual environment (prompt to run setup if missing)
2. Check for .env file
3. Copy .env.example to .env if .env doesn't exist
4. On Windows (PowerShell): Prompt to open .env in notepad for editing (first run only)
5. On Windows (Batch): Open .env in notepad automatically (first run only)
6. On Linux: Prompt user to edit .env manually (first run only)

### Required .env Configuration

At minimum, configure these in your .env file:
- `DATABASE_URL`: Database connection string (default: `sqlite:///db.s3db`)
- `YOUTUBE_API_KEY`: Your YouTube API key (for API-based scraping)
- `YOUTUBE_CHANNEL_URL`: Channel URL for channel-based scraping (optional)

See `.env.example` for all available configuration options.

## Available Commands

After running the scripts, you can use these CLI commands:

- `scrape-channel` - Scrape from a specific channel (recommended)
- `scrape-trending` - Scrape from trending page
- `scrape-keyword` - Search by keywords
- `stats` - View database statistics
- `export` - Export data to JSON

For detailed help on any command:
```bash
python -m src.cli [command] --help
```

## Target Platform

- **Primary**: Windows with NVIDIA RTX 5090, AMD Ryzen, 64GB RAM
- **Secondary**: Linux (for testing and CI/CD only)
- **Not Supported**: macOS

## Troubleshooting

### PowerShell Script Execution Policy

If you get an error like "cannot be loaded because running scripts is disabled":

1. Open PowerShell (no admin privileges needed)
2. Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. Type 'Y' to confirm

This allows locally created scripts to run while maintaining security. Using `-Scope CurrentUser` means you don't need administrator privileges.

### Virtual Environment Not Found
Run the setup script first:
- Windows (PowerShell): `.\_meta\_scripts\setup_module.ps1`
- Windows (Batch): `_meta\_scripts\setup_module.bat`
- Linux: `_meta/_scripts/setup_module.sh`

### Module Not Found Errors
The virtual environment may not have all dependencies. Run:
```powershell
# PowerShell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# or Batch
venv\Scripts\activate.bat
pip install -r requirements.txt

# or Linux
source venv/bin/activate
pip install -r requirements.txt
```

### .env File Issues
Ensure your .env file exists and contains valid configuration:
```bash
# Check if .env exists
ls -la .env

# If missing, copy from example
cp .env.example .env  # Linux
copy .env.example .env  # Windows
```

## Notes

- Scripts automatically navigate to the YouTube module root directory
- All paths are relative to the module root (Sources/Content/Shorts/YouTube)
- The setup script can be run multiple times safely
- The run script will pause after showing help and examples
