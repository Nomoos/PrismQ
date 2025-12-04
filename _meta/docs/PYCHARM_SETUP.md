# PyCharm Setup Guide

**Document Type**: Development Environment Setup  
**Scope**: PyCharm IDE Configuration  
**Last Updated**: 2025-12-04

## Overview

This guide explains how to set up PyCharm for PrismQ development. When opening the project for the first time, you may encounter an error:

> **Error running 'Run.bat Debug' – SDK is not defined for Run Configuration**

This occurs because PyCharm needs a Python interpreter to be configured for the project.

## Quick Setup

### 1. Open the Project

Open PrismQ in PyCharm:
- Launch PyCharm
- Select **File → Open** and navigate to the PrismQ repository folder
- Or use `Debug.bat` from any script folder to open PyCharm with that module

### 2. Configure Python Interpreter

1. Go to **File → Settings** (or **PyCharm → Preferences** on macOS)
2. Navigate to **Project: PrismQ → Python Interpreter**
3. Click the ⚙️ icon in the top right → **Add...**
4. Choose one of these options:

#### Option A: Use Existing Virtual Environment
If you've already run `Run.bat` or `Debug.bat` scripts:
- Select **Existing environment**
- Navigate to the `.venv` folder in the project root (e.g., `.venv/Scripts/python.exe` on Windows or `.venv/bin/python` on Unix)
- Click **OK**

#### Option B: Create New Virtual Environment
- Select **New environment**
- Choose **Virtualenv** as the environment type
- Set the location (e.g., `.venv` in the project root)
- Select your base Python interpreter (Python 3.9+ recommended)
- Click **OK**

### 3. Set as Project Default

After adding the interpreter:
1. Ensure the new interpreter is selected in the dropdown
2. Click **Apply** then **OK**

### 4. Install Dependencies

Open the terminal in PyCharm and run:

```bash
pip install -r requirements.txt
```

Or install dependencies for specific modules as needed.

## Run Configurations

### Using Batch Scripts

PrismQ includes batch scripts for running and debugging modules:

- **Run.bat**: Runs the module in production mode
- **Debug.bat**: Opens PyCharm with pre-configured debug settings
- **Preview.bat**: Preview mode for testing

These scripts are located in each module's `_meta/scripts/` folder.

### Creating Custom Run Configurations

1. Go to **Run → Edit Configurations**
2. Click **+** to add a new configuration
3. Select **Python**
4. Configure:
   - **Script path**: Point to the Python script you want to run
   - **Working directory**: Set to the appropriate module directory
   - **Python interpreter**: Select your configured interpreter
5. Click **Apply** and **OK**

## Troubleshooting

### "SDK is not defined for Run Configuration"

This error means the run configuration references a Python interpreter that doesn't exist on your system.

**Solution**: Follow the steps in "Configure Python Interpreter" above to add a valid Python interpreter, then:
1. Go to **Run → Edit Configurations**
2. Select the problematic configuration
3. Update the **Python interpreter** field to use your configured interpreter
4. Click **Apply** and **OK**

### "No Python interpreter configured for the project"

**Solution**: Add a Python interpreter using **File → Settings → Project: PrismQ → Python Interpreter**.

### Module not found errors

Ensure the module's source directory is marked as a source root:
1. Right-click on the `src` folder in the project tree
2. Select **Mark Directory as → Sources Root**

## Virtual Environment Management

### Recommended Structure

For whole-project development, create a single virtual environment in the project root:

```
PrismQ/
├── .venv/              # Project-wide virtual environment
├── T/
├── A/
├── V/
└── ...
```

For module-specific work, each module can have its own virtual environment:

```
T/Story/From/Idea/
├── .venv/              # Module-specific virtual environment
├── src/
└── requirements.txt
```

### Activating Virtual Environment

```bash
# Windows
.venv\Scripts\activate

# Unix/macOS
source .venv/bin/activate
```

## Related Documentation

- [src Configuration Guide](../../src/README.md) - Environment and configuration management
- [Module Structure](./MODULE_STRUCTURE.md) - Project organization
- [Architecture Overview](./ARCHITECTURE.md) - System architecture

---

**See Also**: [PrismQ README](../../README.md) | [Development Guide](../../Client/_meta/docs/development/DEVELOPMENT.md)
