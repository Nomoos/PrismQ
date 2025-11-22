# Node.js Installation Guide

Complete guide for installing Node.js for the PrismQ Web Client.

## Quick Answer

**Recommended Version**: Node.js 24.11.0 or higher (LTS)

**Minimum Version**: Node.js 18.0 or higher

## Table of Contents

- [Windows Installation](#windows-installation)
- [Linux Installation](#linux-installation)
- [macOS Installation](#macos-installation)
- [Using NVM (Recommended)](#using-nvm-recommended)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Windows Installation

### Method 1: Official Installer (Easiest)

1. **Download Node.js**
   - Visit: https://nodejs.org/
   - Download **LTS** version (24.11.0 or higher)
   - Choose Windows Installer (.msi)
   - Select appropriate architecture:
     - **64-bit** (most common): `node-v24.11.0-x64.msi`
     - 32-bit: `node-v24.11.0-x86.msi`
     - ARM: `node-v24.11.0-arm64.msi`

2. **Run Installer**
   - Double-click the downloaded `.msi` file
   - Click "Next" to start installation
   - Accept the license agreement
   - Choose installation location (default: `C:\Program Files\nodejs\`)
   - **Important**: Keep "Add to PATH" checkbox **CHECKED**
   - Click "Install"
   - Click "Finish" when complete

3. **Verify Installation**
   - Open **NEW** PowerShell or Command Prompt window
   - Run:
     ```powershell
     node -v
     npm -v
     ```
   - Expected output:
     ```
     v24.11.0  (or higher)
     10.2.4    (or higher)
     ```

### Method 2: Chocolatey Package Manager

If you have Chocolatey installed:

```powershell
# Run PowerShell as Administrator
choco install nodejs-lts

# Verify
node -v
npm -v
```

### Method 3: Winget (Windows 10/11)

```powershell
# Run PowerShell as Administrator
winget install OpenJS.NodeJS.LTS

# Verify
node -v
npm -v
```

### Method 4: NVM for Windows (Recommended for Developers)

NVM allows you to install and switch between multiple Node.js versions.

1. **Download NVM for Windows**
   - Visit: https://github.com/coreybutler/nvm-windows/releases
   - Download `nvm-setup.exe` (latest release)
   - Run installer

2. **Install Node.js via NVM**
   ```powershell
   # List available versions
   nvm list available
   
   # Install Node.js 24.11.0
   nvm install 24.11.0
   
   # Use this version
   nvm use 24.11.0
   
   # Verify
   node -v
   npm -v
   ```

3. **Set Default Version**
   ```powershell
   nvm alias default 24.11.0
   ```

## Linux Installation

### Method 1: NodeSource Repository (Recommended)

**Ubuntu/Debian:**

```bash
# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify
node -v
npm -v
```

**RHEL/CentOS/Fedora:**

```bash
# Install Node.js 20.x
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo yum install -y nodejs

# Verify
node -v
npm -v
```

### Method 2: NVM (Recommended for Developers)

```bash
# Install NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Reload shell
source ~/.bashrc  # or ~/.zshrc

# Install Node.js 24.11.0
nvm install 24.11.0

# Use this version
nvm use 24.11.0

# Set as default
nvm alias default 24.11.0

# Verify
node -v
npm -v
```

### Method 3: Package Manager

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install nodejs npm

# May install older version, verify with:
node -v
```

**Arch Linux:**
```bash
sudo pacman -S nodejs npm
```

## macOS Installation

### Method 1: Official Installer

1. Download from https://nodejs.org/
2. Download LTS version (24.11.0 or higher)
3. Run the `.pkg` installer
4. Verify:
   ```bash
   node -v
   npm -v
   ```

### Method 2: Homebrew (Recommended)

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Node.js
brew install node@20

# Verify
node -v
npm -v
```

### Method 3: NVM (Recommended for Developers)

```bash
# Install NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Reload shell
source ~/.bash_profile  # or ~/.zshrc

# Install Node.js 24.11.0
nvm install 24.11.0

# Use this version
nvm use 24.11.0

# Set as default
nvm alias default 24.11.0

# Verify
node -v
npm -v
```

## Using NVM (Recommended)

### What is NVM?

NVM (Node Version Manager) allows you to:
- Install multiple Node.js versions
- Switch between versions easily
- Isolate versions per project
- Test across different Node.js versions

### Installing the Right Version for This Project

This project includes an `.nvmrc` file that specifies the recommended Node.js version.

```bash
# Navigate to project directory
cd PrismQ.T.Idea.Inspiration/Client/Frontend

# Install and use the version specified in .nvmrc
nvm install
nvm use

# Verify
node -v  # Should show v24.11.0 or higher
```

### NVM Quick Reference

```bash
# List installed versions
nvm list

# List available versions
nvm list available  # Windows
nvm ls-remote       # Linux/macOS

# Install specific version
nvm install 24.11.0

# Use specific version
nvm use 24.11.0

# Use version from .nvmrc
nvm use

# Set default version
nvm alias default 24.11.0

# Show current version
nvm current
```

## Verification

After installation, verify Node.js and npm are working:

```bash
# Check Node.js version
node -v
# Expected: v24.11.0 or higher

# Check npm version
npm -v
# Expected: 10.2.4 or higher

# Check installation path
where node     # Windows
which node     # Linux/macOS

# Run a simple test
node -e "console.log('Node.js is working!')"
# Expected output: Node.js is working!

# Check npm can install packages (create temp directory)
mkdir -p /tmp/npm-test
cd /tmp/npm-test
npm init -y
npm install lodash
# Should complete without errors
```

## Troubleshooting

### "npm is not recognized" or "node is not recognized"

**Cause**: Node.js is not in your system PATH.

**Solution (Windows):**

1. **Restart PowerShell/Command Prompt**
   - Close and open a NEW window
   - PATH is only updated in new sessions

2. **Check Installation**
   ```powershell
   # Check if Node.js is installed
   Test-Path "C:\Program Files\nodejs\node.exe"
   # Should return: True
   ```

3. **Add to PATH Manually**
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Go to "Advanced" tab → "Environment Variables"
   - Under "System variables", find "Path"
   - Click "Edit" → "New"
   - Add: `C:\Program Files\nodejs\`
   - Click "OK" on all dialogs
   - **Restart PowerShell/Command Prompt**

4. **Reinstall Node.js**
   - Uninstall current installation
   - Download fresh installer from https://nodejs.org/
   - Run installer with "Add to PATH" checked

**Solution (Linux/macOS):**

```bash
# Check if installed
which node
which npm

# If using NVM, reload shell
source ~/.bashrc  # or ~/.zshrc

# If installed via package manager
export PATH=$PATH:/usr/local/bin
```

### "Permission Denied" Errors

**Linux/macOS:**

```bash
# Don't use sudo with npm if using NVM
# If you installed via package manager:
sudo chown -R $(whoami) ~/.npm
sudo chown -R $(whoami) /usr/local/lib/node_modules
```

### Wrong Version Installed

```bash
# Check current version
node -v

# If using NVM, switch to correct version
nvm install 24.11.0
nvm use 24.11.0
nvm alias default 24.11.0

# If using system installation, uninstall and reinstall
```

### npm Commands Fail

```bash
# Clear npm cache
npm cache clean --force

# Update npm
npm install -g npm@latest

# Verify npm configuration
npm config list
```

### Installation Fails on Windows

**Error**: "Installation directory is not writable"

**Solution**:
- Run installer as Administrator
- Right-click installer → "Run as administrator"

**Error**: "Cannot find module"

**Solution**:
```powershell
# Repair Node.js installation
# Download installer again from nodejs.org
# Run installer → Choose "Repair"
```

### Still Having Issues?

1. **Uninstall Completely**
   - **Windows**: Control Panel → Programs → Uninstall Node.js
   - **Linux**: `sudo apt remove nodejs npm` or equivalent
   - **macOS**: `brew uninstall node` or delete from Applications

2. **Clean Residual Files**
   - **Windows**: Delete `C:\Program Files\nodejs\` and `C:\Users\<YourName>\AppData\Roaming\npm`
   - **Linux/macOS**: Delete `~/.npm` and `/usr/local/lib/node_modules`

3. **Fresh Install**
   - Follow installation steps above
   - Use official installer or NVM

## Recommended Setup for PrismQ

For the best development experience with PrismQ:

1. **Install NVM** (Windows: nvm-windows, Linux/macOS: nvm)
2. **Install Node.js 24.11.0 or higher** via NVM
3. **Set as default** version
4. **Navigate to project** directory
5. **Run `nvm use`** to ensure correct version
6. **Run `npm install`** to install dependencies

```bash
# Complete setup example
nvm install 24.11.0
nvm use 24.11.0
nvm alias default 24.11.0
cd PrismQ.T.Idea.Inspiration/Client/Frontend
npm install
npm run dev
```

## Additional Resources

- **Node.js Official**: https://nodejs.org/
- **NVM (Linux/macOS)**: https://github.com/nvm-sh/nvm
- **NVM for Windows**: https://github.com/coreybutler/nvm-windows
- **NodeSource**: https://github.com/nodesource/distributions
- **npm Documentation**: https://docs.npmjs.com/

## Need More Help?

- Check [SETUP.md](SETUP.md) for general setup instructions
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Open an issue: https://github.com/Nomoos/PrismQ.T.Idea.Inspiration/issues

---

**Last Updated**: 2025-11-03  
**Node.js Version**: 24.11.0 or higher (LTS)  
**Maintained by**: PrismQ Development Team
