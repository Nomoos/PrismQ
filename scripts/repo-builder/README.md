# PrismQ Repository Builder & Checker

A Python CLI tool that validates GitHub CLI authentication and derives the full module chain from deepest to root, given a PrismQ dotted name or GitHub URL.

## Features

1. **GitHub CLI Validation**: Automatically checks if GitHub CLI (`gh`) is installed and authenticated
2. **Module Chain Derivation**: Derives the full module hierarchy from deepest module to root
3. **Flexible Input**: Accepts both dotted module names and GitHub URLs
4. **Interactive Mode**: Prompts for input when no command-line argument is provided, repeating until valid input is given or the script is terminated

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
# Simple module
run.bat PrismQ

# Nested module
run.bat PrismQ.IdeaInspiration

# Deeply nested module
run.bat PrismQ.IdeaInspiration.SubModule

# Interactive mode
python repo_builder.py
# Then enter: PrismQ.IdeaInspiration.SubModule
```

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
2. Parse the input (URL or dotted name)
3. Display the module chain from deepest to root

Example output:

```
🚀 PrismQ Nested Repository Builder & Checker
==================================================

🔍 Validating GitHub CLI authentication...
✅ GitHub CLI is authenticated

🔍 Processing input: PrismQ.IdeaInspiration.SubModule

📦 Module Chain (deepest → root):
==================================================
🎯 PrismQ.IdeaInspiration.SubModule (depth: 3)
  📁 PrismQ.IdeaInspiration (depth: 2)
    🏠 PrismQ (depth: 1)
==================================================

✅ Analysis complete!
```

## Error Handling

The tool provides clear error messages for common issues:

- GitHub CLI not installed
- GitHub CLI not authenticated
- Invalid module name format
- Invalid GitHub URL format

## Development

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
