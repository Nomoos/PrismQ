# New Feature: GitHub URL Parsing in New CLI

## What Was Added

The new CLI (`add_module.py`) now supports GitHub URL parsing with automatic owner detection!

## How to Use

Simply pass a GitHub URL as the module argument:

```bash
python -m scripts.add_module.add_module https://github.com/Nomoos/PrismQ.MyModule
```

## Supported URL Formats

All standard GitHub URL formats are supported:

1. **HTTPS with .git**
   ```bash
   python -m scripts.add_module.add_module https://github.com/Nomoos/PrismQ.Module.git
   ```

2. **HTTPS without .git**
   ```bash
   python -m scripts.add_module.add_module https://github.com/Nomoos/PrismQ.Module
   ```

3. **SSH format**
   ```bash
   python -m scripts.add_module.add_module git@github.com:Nomoos/PrismQ.Module.git
   ```

4. **Short format (Owner/Repo)**
   ```bash
   python -m scripts.add_module.add_module Nomoos/PrismQ.Module
   ```

## What Gets Auto-Detected

When you provide a GitHub URL, the following values are automatically detected and derived:

| Parameter | Value | Can Override? |
|-----------|-------|---------------|
| `--owner` | Extracted from URL (e.g., "Nomoos") | ✅ Yes with `--owner` flag |
| **Module Path** | **Auto-derived from repository name** | ❌ No (automatic) |
| `--branch` | Default: "main" | ✅ Yes with `--branch` flag |
| `--public/--private` | Default: public | ✅ Yes with `--private` flag |
| `--description` | Empty | ✅ Yes with `--description` flag |

### Module Path Derivation

The module path is automatically derived from the repository name:

- `PrismQ.MyModule` → `src/MyModule`
- `PrismQ.MyModule.SubModule` → `src/MyModule/src/SubModule`
- `PrismQ.Deep.Nested.Path` → `src/Deep/src/Nested/src/Path`

This follows PrismQ's nested module structure convention where each level after the first is prefixed with `src/`.

## Example Output

### Single-level Module

```
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
```

### Nested Module (Auto-derived Path)

```
$ python -m scripts.add_module.add_module https://github.com/Nomoos/PrismQ.MyModule.SubModule

============================================================
        PrismQ Module Creation Script
============================================================

Detected GitHub URL input
  Parsed Owner:      Nomoos
  Parsed Repository: PrismQ.MyModule.SubModule

Configuration:
  Module Name:     MyModule.SubModule
  Module Path:     src/MyModule/src/SubModule
  Owner:           Nomoos
  Visibility:      Public
  Branch:          main
```

## Overriding Defaults

You can override any auto-detected value:

```bash
# Override owner
python -m scripts.add_module.add_module https://github.com/Nomoos/PrismQ.Module --owner CustomOrg

# Make it private
python -m scripts.add_module.add_module https://github.com/Nomoos/PrismQ.Module --private

# Add description
python -m scripts.add_module.add_module https://github.com/Nomoos/PrismQ.Module --description "My module"

# Override multiple
python -m scripts.add_module.add_module https://github.com/Nomoos/PrismQ.Module \
  --owner CustomOrg \
  --private \
  --branch develop \
  --description "Private module"
```

## Benefits

1. **Convenience**: Just paste a GitHub URL - no need to extract parts manually
2. **Consistency**: Works like the legacy CLI's interactive mode
3. **Flexibility**: Can still override any value with command-line flags
4. **Automation-friendly**: Perfect for scripts that have URLs stored

## Comparison

| Before | After |
|--------|-------|
| `python -m scripts.add_module.add_module PrismQ.MyModule --owner Nomoos` | `python -m scripts.add_module.add_module https://github.com/Nomoos/PrismQ.MyModule` |
| Need to know module name format | Just paste the GitHub URL |
| Must specify owner separately | Owner auto-detected from URL |

## Implementation Details

- Detects URLs by checking for `/` or `github.com` in the module argument
- Uses existing `parse_github_url()` function from `url_parser.py`
- Preserves backward compatibility - regular module names still work
- Falls back to command-line `--owner` if URL parsing fails
- Shows parsed information to user for transparency

## Testing

All 82 tests pass:
- ✅ 30 legacy tests (backward compatibility)
- ✅ 52 new comprehensive tests
- ✅ URL parsing verified with all formats
- ✅ Regular module names still work correctly
