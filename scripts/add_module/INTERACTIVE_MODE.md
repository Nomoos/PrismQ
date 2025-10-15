# Interactive Mode Support in Add Module

## Summary

**Yes**, the add_module script **still supports interactive mode** with pasting just a GitHub URL.

## How to Use Interactive Mode

### Legacy CLI (Supports Interactive Mode)

Run the script without any arguments:

```bash
python -m scripts.add_module
```

You will be prompted to enter the GitHub repository URL:

```
========================================================
        PrismQ Module Creation Script
========================================================

Enter the GitHub repository URL (e.g., https://github.com/Nomoos/PrismQ.RepositoryTemplate.git): 
```

Simply paste your GitHub URL and press Enter:

```
Enter the GitHub repository URL (e.g., https://github.com/Nomoos/PrismQ.RepositoryTemplate.git): https://github.com/Nomoos/PrismQ.MyModule

Parsed from GitHub URL:
  Owner: Nomoos
  Repository: PrismQ.MyModule
  Module Name: MyModule
  Module Path: src/MyModule

Please enter a short description for the module (optional): My awesome module
```

### Supported URL Formats

The interactive mode accepts various GitHub URL formats:

1. **Full HTTPS URL with .git**
   ```
   https://github.com/Nomoos/PrismQ.MyModule.git
   ```

2. **HTTPS URL without .git**
   ```
   https://github.com/Nomoos/PrismQ.MyModule
   ```

3. **SSH Format**
   ```
   git@github.com:Nomoos/PrismQ.MyModule.git
   ```

4. **Short Format (Owner/Repo)**
   ```
   Nomoos/PrismQ.MyModule
   ```

## Two CLI Interfaces

The add_module package provides two CLI interfaces:

### 1. Legacy CLI (`__main__.py`)

- **Location:** `scripts/add_module/__main__.py`
- **Command:** `python -m scripts.add_module`
- **Technology:** Click library
- **Interactive Mode:** ✅ **Supported**
- **Best For:** Manual, one-off module creation

**Usage:**
```bash
# Interactive mode (no arguments)
python -m scripts.add_module

# Or with command-line arguments
python -m scripts.add_module --github-url "https://github.com/Nomoos/PrismQ.MyModule"
```

### 2. New CLI (`add_module.py`)

- **Location:** `scripts/add_module/add_module.py`
- **Command:** `python -m scripts.add_module.add_module`
- **Technology:** argparse
- **Interactive Mode:** ❌ **Not Supported**
- **Best For:** Scripting, automation, CI/CD pipelines

**Usage:**
```bash
# Requires module name as positional argument
python -m scripts.add_module.add_module PrismQ.MyModule --owner Nomoos --public
```

## Why Two CLIs?

The repository underwent a refactoring that introduced a new CLI with:
- Better architecture (SOLID principles)
- Comprehensive test coverage (52+ tests)
- Full type safety (mypy-strict compliant)
- Command-line focused (better for automation)

However, the **legacy CLI was preserved for backward compatibility** and continues to support the **interactive mode** that many users prefer for manual operations.

## Recommendations

- **For Manual/Interactive Use:** Use the legacy CLI with interactive mode
  ```bash
  python -m scripts.add_module
  ```

- **For Scripting/Automation:** Use the new CLI with explicit arguments
  ```bash
  python -m scripts.add_module.add_module PrismQ.MyModule --owner Nomoos
  ```

## Testing Interactive Mode

You can verify interactive mode works by running:

```bash
cd /path/to/PrismQ
python -m scripts.add_module
```

Then paste a test URL when prompted (e.g., `https://github.com/Nomoos/PrismQ.TestModule`).

Press Ctrl+C to cancel if you don't want to actually create the module.

## Related Documentation

- [README.md](README.md) - Package overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture
- [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) - Refactoring details
- [../../scripts/README.md](../../scripts/README.md) - Scripts documentation
