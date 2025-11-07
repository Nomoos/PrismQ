# Scripts

This directory contains utility scripts for the PrismQ module.

## Why PowerShell?

For Windows users, **PowerShell scripts (.ps1) are recommended** over batch scripts (.bat) because:

1. **Better Error Handling**: PowerShell provides structured error handling with try/catch blocks
2. **Colored Output**: Enhanced readability with color-coded status messages
3. **Modern Windows Standard**: PowerShell is the modern scripting standard for Windows
4. **AI Assistant Friendly**: Better structured syntax for GitHub Copilot and ChatGPT to understand and modify
5. **More Powerful**: Advanced features like object manipulation and better string handling

### Enabling PowerShell Scripts

If you get an error about script execution being disabled, run this once:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

This allows locally created scripts to run while still protecting against untrusted remote scripts.

## Available Scripts

### Setup Scripts

**Windows (PowerShell - Recommended):**
```powershell
.\scripts\setup.ps1
```

**Windows (Batch - Legacy):**
```batch
scripts\setup.bat
```

**Linux (development only):**
```bash
bash scripts/setup.sh
```

### Quick Start Scripts

**Windows (PowerShell - Recommended):**
```powershell
.\scripts\quickstart.ps1
```

**Windows (Batch - Legacy):**
```batch
scripts\quickstart.bat
```

**Linux (development only):**
```bash
bash scripts/quickstart.sh
```

## Target Platform

These scripts are optimized for:
- **OS**: Windows (required)
- **GPU**: NVIDIA RTX 5090
- **CPU**: AMD Ryzen
- **RAM**: 64GB

> **Note**: Linux support is provided for development purposes only. macOS is not supported.

## Creating New Scripts

When adding new scripts:
1. Create PowerShell scripts (.ps1) as the primary implementation (recommended)
2. Create Windows batch files (.bat) for compatibility
3. Add clear comments explaining what the script does
4. Include error handling and colored output (PowerShell)
5. Update this README
