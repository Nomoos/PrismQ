# Scripts

This directory contains utility scripts for the PrismQ module.

## Available Scripts

### Setup Scripts

- **setup.bat** - Windows setup script (primary)
- **setup.sh** - Linux setup script (development only)

### Quick Start Scripts

- **quickstart.bat** - Quick start for Windows (primary)
- **quickstart.sh** - Quick start for Linux (development only)

## Usage

### Windows

Run the setup script to install dependencies:
```batch
scripts\setup.bat
```

Run the quick start script to test the module:
```batch
scripts\quickstart.bat
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
1. Create Windows batch files (.bat) as the primary implementation
2. Add clear comments explaining what the script does
3. Include error handling
4. Update this README
