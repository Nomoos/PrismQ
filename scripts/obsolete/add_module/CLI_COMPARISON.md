# CLI Comparison: Legacy vs New

This document compares the two CLI interfaces available for the add_module package.

## Quick Comparison Table

| Feature | Legacy CLI | New CLI |
|---------|-----------|---------|
| **Command** | `python -m scripts.add_module` | `python -m scripts.add_module.add_module` |
| **Technology** | Click | argparse |
| **Interactive Mode** | ✅ Yes | ❌ No |
| **Required Arguments** | None (prompts) | `module` or URL (positional) |
| **GitHub URL Input** | As prompt or `--github-url` | ✅ **Now supported!** |
| **URL Auto-parsing** | ✅ Yes | ✅ **Yes (new!)** |
| **Best For** | Manual operations | Scripting/automation |
| **Tests** | 30 legacy tests | 52 comprehensive tests |
| **Architecture** | Monolithic | SOLID principles |
| **Type Safety** | Partial | Full (mypy-strict) |

## Usage Examples

### Legacy CLI - Interactive Mode

```bash
$ python -m scripts.add_module

========================================================
        PrismQ Module Creation Script
========================================================

Enter the GitHub repository URL (e.g., https://github.com/Nomoos/PrismQ.RepositoryTemplate.git): https://github.com/Nomoos/PrismQ.MyModule

Parsed from GitHub URL:
  Owner: Nomoos
  Repository: PrismQ.MyModule
  Module Name: MyModule
  Module Path: src/MyModule

Please enter a short description for the module (optional): My awesome module

========================================================
Module Configuration Summary
========================================================
Module Name:        MyModule
Module Directory:   src/MyModule
Description:        My awesome module
Repository Name:    PrismQ.MyModule
GitHub Owner:       Nomoos
Remote URL:         https://github.com/Nomoos/PrismQ.MyModule.git
Remote Name:        prismq-mymodule
========================================================

Create this module? [y/N]:
```

### Legacy CLI - Command Line Mode

```bash
$ python -m scripts.add_module --github-url "https://github.com/Nomoos/PrismQ.MyModule"

========================================================
        PrismQ Module Creation Script
========================================================

Parsed from GitHub URL:
  Owner: Nomoos
  Repository: PrismQ.MyModule
  Module Name: MyModule
  Module Path: src/MyModule
...
```

### New CLI - Command Line Only

```bash
# Using module name
$ python -m scripts.add_module.add_module PrismQ.MyModule --owner Nomoos --public

============================================================
        PrismQ Module Creation Script
============================================================

Configuration:
  Module Name:     MyModule
  Module Path:     src/MyModule
  Owner:           Nomoos
  Visibility:      Public
  Branch:          main

Creating GitHub repository hierarchy...
============================================================
Checking: PrismQ.MyModule
  ✓ Repository exists: PrismQ.MyModule
============================================================
...
```

### New CLI - With URL Parsing (New Feature!)

```bash
# Using GitHub URL directly - owner auto-detected!
$ python -m scripts.add_module.add_module https://github.com/Nomoos/PrismQ.MyModule

============================================================
        PrismQ Module Creation Script
============================================================

Detected GitHub URL input
  Parsed Owner:      Nomoos
  Parsed Repository: PrismQ.MyModule

Configuration:
  Module Name:     MyModule
  Module Path:     src/MyModule
  Owner:           Nomoos
  Visibility:      Public
  Branch:          main

Creating GitHub repository hierarchy...
...
```

**Nested modules also work** - path is auto-derived:

```bash
$ python -m scripts.add_module.add_module https://github.com/Nomoos/PrismQ.MyModule.SubModule

Detected GitHub URL input
  Parsed Owner:      Nomoos
  Parsed Repository: PrismQ.MyModule.SubModule

Configuration:
  Module Name:     MyModule.SubModule
  Module Path:     src/MyModule/src/SubModule  ← Auto-derived!
  Owner:           Nomoos
  Visibility:      Public
  Branch:          main
```

## When to Use Each

### Use Legacy CLI When:

1. **Learning the system** - Interactive prompts guide you through the process
2. **Creating modules occasionally** - Don't need to remember all the arguments
3. **Have a GitHub URL ready** - Just paste it in
4. **Prefer step-by-step confirmation** - Review configuration before proceeding

**Command:**
```bash
python -m scripts.add_module
```

### Use New CLI When:

1. **Automating module creation** - Scripts, CI/CD pipelines
2. **Creating multiple modules** - Batch operations
3. **Have a GitHub URL** - Now supports URL parsing with auto-detection!
4. **Need programmatic control** - Better for scripting

**Command:**
```bash
# With module name
python -m scripts.add_module.add_module PrismQ.MyModule --owner Nomoos

# With GitHub URL (new feature!)
python -m scripts.add_module.add_module https://github.com/Nomoos/PrismQ.MyModule
```

## Supported URL Formats (Legacy CLI Only)

The legacy CLI's interactive mode accepts various GitHub URL formats:

1. **Full HTTPS with .git**
   ```
   https://github.com/Nomoos/PrismQ.MyModule.git
   ```

2. **HTTPS without .git**
   ```
   https://github.com/Nomoos/PrismQ.MyModule
   ```

3. **HTTP Protocol**
   ```
   http://github.com/Nomoos/PrismQ.MyModule
   ```

4. **SSH Format**
   ```
   git@github.com:Nomoos/PrismQ.MyModule.git
   ```

5. **Short Format**
   ```
   Nomoos/PrismQ.MyModule
   ```

All formats are automatically parsed and normalized.

## Help Commands

### Legacy CLI Help

```bash
$ python -m scripts.add_module --help

Usage: python -m scripts.add_module [OPTIONS]

  PrismQ Module Creation Script - Create a new PrismQ module with GitHub
  integration.

Options:
  --github-url TEXT   GitHub repository URL or Owner/RepoName format
  --description TEXT  Module description
  --help              Show this message and exit.
```

### New CLI Help

```bash
$ python -m scripts.add_module.add_module --help

usage: add_module.py [-h] [--owner OWNER] [--branch BRANCH] [--public | --private]
                     [--remote-origin-prefix REMOTE_ORIGIN_PREFIX]
                     [--description DESCRIPTION] [--verbose]
                     module

Automate PrismQ module creation with nested git subtree hierarchy

positional arguments:
  module                PrismQ module name in dot-notation (e.g.,
                        PrismQ.IdeaInspiration.Sources)

options:
  -h, --help            show this help message and exit
  --owner OWNER         GitHub repository owner/organization (default: Nomoos)
  --branch BRANCH       Git branch name (default: main)
  --public              Create public repositories (default)
  --private             Create private repositories
  --remote-origin-prefix REMOTE_ORIGIN_PREFIX
                        Remote URL prefix (default: https://github.com)
  --description DESCRIPTION
                        Module description
  --verbose, -v         Enable verbose logging
```

## Migration Path

If you're currently using the legacy CLI interactively, you can continue to do so. There's no forced migration. Both CLIs will be maintained.

However, if you want to adopt the new CLI for automation:

**Legacy Interactive:**
```bash
python -m scripts.add_module
# Enter: https://github.com/Nomoos/PrismQ.MyModule
```

**Equivalent New CLI:**
```bash
python -m scripts.add_module.add_module PrismQ.MyModule --owner Nomoos
```

## Conclusion

Both CLIs serve different purposes:

- **Legacy CLI**: User-friendly, interactive, great for learning
- **New CLI**: Automation-friendly, testable, follows modern best practices

Choose the one that fits your workflow!
