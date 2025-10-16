# PrismQ Repository Builder & Checker

A Python CLI tool that validates GitHub CLI authentication and derives the full module chain from root to deepest, given a PrismQ dotted name or GitHub URL.

## Features

1. **GitHub CLI Validation**: Automatically checks if GitHub CLI (`gh`) is installed and authenticated
2. **Module Chain Derivation**: Derives the full module hierarchy from root to deepest for subtree building
3. **Input Parsing & Normalization**: 
   - Accepts dotted module names starting with `PrismQ.` and at least one more segment
   - Accepts GitHub URLs (HTTPS or SSH) pointing to `Nomoos/<Repo>` where `<Repo>` starts with `PrismQ.`
   - Normalizes to repository name strings like `PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeSource`
4. **Strict Validation**: 
   - Must start with `PrismQ.` and have only alphanumeric segments separated by dots
   - GitHub URLs must be from the Nomoos organization
   - Repository names must have at least one segment after `PrismQ`
5. **Interactive Mode**: Prompts for input when no command-line argument is provided, repeating until valid input is given or the script is terminated

## Prerequisites

- Python 3.8 or higher
- GitHub CLI (`gh`) installed and authenticated
  - Install from: https://cli.github.com/
  - Authenticate with: `gh auth login`

## Setup

### Windows

1. Run the setup script to create a virtual environment:
   ```batch
   setup_env.bat
   ```

2. The script will:
   - Check for Python installation
   - Create a virtual environment in `.venv/`
   - Install dependencies (currently none required)

### Linux/Mac

1. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Usage

### Windows (using batch script)

```batch
run.bat <module_name_or_url>
# Or run without arguments for interactive mode
run.bat
```

### Direct Python execution

```bash
# Activate virtual environment first
.venv\Scripts\activate.bat  # Windows
source .venv/bin/activate   # Linux/Mac

# Run the script with command-line argument
python repo_builder.py <module_name_or_url>

# Or run without arguments for interactive mode
python repo_builder.py
```

### Interactive Mode

If you run the script without any arguments, it will enter interactive mode and prompt you for input:

```bash
python repo_builder.py
```

The script will:
- Display usage instructions and examples
- Prompt you to enter a module name or URL
- Repeat the prompt if you provide empty input
- Continue until you provide valid input or press Ctrl+C to exit

## Examples

### Using dotted module names

```batch
# Nested module (minimum requirement: PrismQ. + at least one segment)
run.bat PrismQ.IdeaInspiration

# Deeply nested module
run.bat PrismQ.IdeaInspiration.SubModule

# Very deeply nested module
run.bat PrismQ.IdeaInspiration.Sources.Content.Shorts.YouTubeSource

# Interactive mode
python repo_builder.py
# Then enter: PrismQ.IdeaInspiration.SubModule
```

**Note**: Module name must start with `PrismQ.` and have at least one additional segment. Just `PrismQ` alone is not accepted.

### Using GitHub URLs

```batch
# HTTPS URL
run.bat https://github.com/Nomoos/PrismQ.IdeaInspiration

# SSH URL
run.bat git@github.com:Nomoos/PrismQ.IdeaInspiration.git

# Interactive mode with URL
python repo_builder.py
# Then enter: https://github.com/Nomoos/PrismQ.IdeaInspiration
```

## Output

The tool will:

1. Validate GitHub CLI authentication
2. Parse and normalize the input (URL or dotted name)
3. Validate the module name meets requirements
4. Display the module chain from root to deepest

Example output:

```
🚀 PrismQ Nested Repository Builder & Checker
==================================================

🔍 Validating GitHub CLI authentication...
✅ GitHub CLI is authenticated

🔍 Processing input: PrismQ.IdeaInspiration.SubModule

📦 Module Chain (root → deepest):
==================================================
🏠 PrismQ (depth: 1)
  📁 PrismQ.IdeaInspiration (depth: 2)
    🎯 PrismQ.IdeaInspiration.SubModule (depth: 3)
==================================================

✅ Analysis complete!
```

## Error Handling

The tool provides clear error messages for common issues:

- GitHub CLI not installed
- GitHub CLI not authenticated
- Invalid module name format (must be alphanumeric segments separated by dots)
- Module name not starting with `PrismQ.`
- Module name without at least one segment after `PrismQ`
- Invalid GitHub URL format
- GitHub URL not from Nomoos organization
- Repository name not starting with `PrismQ.`
- Non-alphanumeric characters in module segments (hyphens, underscores, etc.)

## Validation Rules

### Module Names
- Must start with `PrismQ.`
- Must have at least one segment after `PrismQ` (e.g., `PrismQ.IdeaInspiration`)
- Segments must be alphanumeric only (no hyphens, underscores, or special characters)
- Segments are separated by dots (`.`)
- Each segment must start with a letter (not a number)

### GitHub URLs
- Must be from the `Nomoos` organization
- Repository name must start with `PrismQ.`
- Repository name must follow the same validation rules as module names
- Supports both HTTPS and SSH formats

## Development

### Project Structure

The repository builder has been modularized for better maintainability. The code is split into the following modules:

- **`exceptions.py`**: Custom exception classes (`RepoBuilderError`, `GitHubCLIError`, `ModuleParseError`)
- **`validation.py`**: GitHub CLI validation functions
- **`parsing.py`**: URL and module name parsing logic
- **`display.py`**: Output formatting and display functions
- **`repository.py`**: Repository operations (exists check, path mapping, git operations)
- **`cli.py`**: CLI interface and main entry point functions
- **`__init__.py`**: Package initialization with exports for importing as a package
- **`__main__.py`**: Entry point when running as a module with `python -m`
- **`repo_builder.py`**: Backward compatibility wrapper that re-exports all functions

All modules use a try/except pattern internally to support both relative imports (when used as a package) and absolute imports (when used as standalone scripts from the directory).

### Running Tests

```bash
# Install pytest
pip install pytest

# Run all tests
python -m pytest test_repo_builder.py -v

# Run specific test class
python -m pytest test_repo_builder.py::TestParseGitHubUrl -v
```

### Running without virtual environment

```bash
python repo_builder.py <module_name_or_url>
```

### Testing different inputs

```bash
# Test with valid dotted name
python repo_builder.py PrismQ.IdeaInspiration

# Test with GitHub URL
python repo_builder.py https://github.com/Nomoos/PrismQ.IdeaInspiration

# Test error handling
python repo_builder.py invalid..name
```

### Using as a Library

The repository builder can be imported and used programmatically when running from the `repo-builder` directory or when the directory is in your Python path:

```python
# Import specific functions
# Note: Run this from the repo-builder directory or ensure it's in PYTHONPATH
from repo_builder import (
    parse_github_url, 
    derive_module_chain,
    validate_github_cli,
    ModuleParseError
)

# Parse a GitHub URL
try:
    module_name = parse_github_url("https://github.com/Nomoos/PrismQ.IdeaInspiration")
    print(f"Module name: {module_name}")  # PrismQ.IdeaInspiration
except ModuleParseError as e:
    print(f"Error: {e}")

# Derive module chain
chain = derive_module_chain("PrismQ.IdeaInspiration.SubModule")
print(chain)  # ['PrismQ', 'PrismQ.IdeaInspiration', 'PrismQ.IdeaInspiration.SubModule']

# Validate GitHub CLI
try:
    validate_github_cli()
    print("GitHub CLI is authenticated")
except GitHubCLIError as e:
    print(f"Error: {e}")
```

