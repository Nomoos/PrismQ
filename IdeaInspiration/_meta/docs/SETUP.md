# Setup Guide

This guide covers setting up the PrismQ.IdeaInspiration development environment.

## Prerequisites

- Python 3.10+
- Windows 10/11 (primary platform)
- NVIDIA RTX 5090 with latest drivers (recommended)
- AMD Ryzen processor
- 64GB RAM
- Git

## Quick Setup

### For Users

1. Choose the module you need (Classification, Scoring, Sources, etc.)
2. Navigate to its directory
3. Follow the module-specific README for installation and usage

### For Developers

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Nomoos/PrismQ.IdeaInspiration.git
   cd PrismQ.IdeaInspiration
   ```

2. **Set up virtual environments (recommended):**
   
   **Windows PowerShell:**
   ```powershell
   .\_meta\_scripts\setup_all_envs.ps1
   ```
   
   **Linux/macOS/WSL:**
   ```bash
   ./_meta/_scripts/setup_all_envs.sh
   ```
   
   This creates isolated virtual environments for each project. See [Virtual Environment Guide](./_meta/docs/development/VIRTUAL_ENVIRONMENTS.md) for details.

3. **(Optional) Install direnv for automatic environment activation:**
   
   See detailed guide: [DIRENV Setup](./_meta/docs/development/DIRENV_SETUP.md)
   
   **Ubuntu/Debian:**
   ```bash
   # Install direnv
   sudo apt install direnv
   
   # Configure shell (~/.bashrc)
   eval "$(direnv hook bash)"
   
   # Allow each project (one-time)
   cd Classification && direnv allow
   ```
   
   With direnv, environments activate automatically when you `cd` into a project!

4. **Work on a specific module:**
   ```bash
   cd Classification
   # If using direnv: environment activates automatically!
   # Otherwise activate manually:
   #   Linux/macOS/WSL: source venv/bin/activate
   #   Windows PowerShell: .\venv\Scripts\Activate.ps1
   
   # Follow module-specific development instructions
   ```

## Target Platform

All modules are optimized for:
- **Operating System**: Windows
- **GPU**: NVIDIA RTX 5090 (32GB VRAM)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

## Module Setup

Each module has its own setup requirements. Refer to the module-specific documentation:

- **[Client Setup](../Client/docs/SETUP.md)** - Web control panel setup
- **[Classification Setup](../Classification/README.md)** - Content classification setup
- **[Scoring Setup](../Scoring/README.md)** - Scoring engine setup
- **[Sources Setup](../Sources/README.md)** - Source integrations setup
- **[Model Setup](../Model/README.md)** - Data model setup

## Development Environment

### Virtual Environments

For detailed information on virtual environment strategy and setup, see:
- [Virtual Environment Guide](./_meta/docs/development/VIRTUAL_ENVIRONMENTS.md)

### Database Setup

For database integration and setup:
- [Database Guide](./_meta/docs/development/DATABASE.md)

### Testing

For running tests and checking coverage:
- [Testing Guide](./_meta/docs/development/TESTING.md)

## Troubleshooting

### Common Issues

**Virtual environment not activating:**
- Make sure you're using the correct activation command for your OS
- Check that Python is in your PATH
- See [Virtual Environment Guide](./_meta/docs/development/VIRTUAL_ENVIRONMENTS.md)

**Module not found errors:**
- Ensure you've activated the correct virtual environment
- Run `pip install -e .` in the module directory

**GPU not detected:**
- Install latest NVIDIA drivers
- Verify CUDA installation
- Check PyTorch GPU support: `python -c "import torch; print(torch.cuda.is_available())"`

## Next Steps

After setup, refer to:
- [Architecture Documentation](./_meta/docs/ARCHITECTURE.md) - Understand the system design
- [Contributing Guide](./_meta/docs/CONTRIBUTING.md) - Start contributing
- Module-specific user guides for usage instructions

## Support

For issues and questions:
- Check module-specific troubleshooting guides
- See [GitHub Issues](https://github.com/Nomoos/PrismQ.IdeaInspiration/issues)
