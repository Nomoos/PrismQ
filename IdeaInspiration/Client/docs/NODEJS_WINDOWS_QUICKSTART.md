# Node.js Installation - Windows Quick Start

**Recommended Version**: Node.js 24.11.0 or higher (LTS)

## Fastest Method (5 minutes)

### Option 1: Official Installer (Recommended for Most Users)

1. **Download Node.js**
   - Go to: https://nodejs.org/
   - Click the **green "LTS" button** (Long Term Support)
   - This downloads the recommended version (24.11.0 or higher)

2. **Run the Installer**
   - Find the downloaded file (e.g., `node-v24.11.0-x64.msi`)
   - Double-click to run
   - Click "Next" through the wizard
   - **IMPORTANT**: Make sure "Add to PATH" is **CHECKED** ✅
   - Click "Install"
   - Wait for installation to complete
   - Click "Finish"

3. **Verify Installation**
   - **Close any open PowerShell or Command Prompt windows**
   - Open a **NEW** PowerShell window
   - Type these commands:
   ```powershell
   node -v
   npm -v
   ```
   - You should see:
   ```
   v24.11.0  (or higher)
   10.2.4    (or higher)
   ```

4. **Start Using PrismQ**
   ```powershell
   cd C:\Users\hittl\PROJECTS\VideoMaking\PrismQ\IdeaInspiration\Client\Frontend
   npm install
   npm run dev
   ```

## Troubleshooting

### Still Getting "npm is not recognized"?

**Solution 1: Restart PowerShell**
- Close ALL PowerShell/Command Prompt windows
- Open a NEW PowerShell window
- Try `node -v` again

**Solution 2: Check if Node.js is Installed**
```powershell
# Check if Node.js exists
Test-Path "C:\Program Files\nodejs\node.exe"
```
If it says `False`, Node.js didn't install correctly. Try reinstalling.

**Solution 3: Add to PATH Manually**
1. Press `Win + R`
2. Type `sysdm.cpl` and press Enter
3. Click "Advanced" tab
4. Click "Environment Variables"
5. Under "System variables", find "Path"
6. Click "Edit"
7. Click "New"
8. Add: `C:\Program Files\nodejs\`
9. Click "OK" on all windows
10. **Restart PowerShell**

**Solution 4: Reinstall Node.js**
1. Go to Control Panel → Programs → Uninstall a program
2. Find "Node.js" and uninstall it
3. Download fresh installer from https://nodejs.org/
4. Run installer again, making sure "Add to PATH" is checked
5. Restart PowerShell after installation

## Alternative Methods

### Option 2: NVM for Windows (For Developers)

If you need to manage multiple Node.js versions:

1. **Download NVM for Windows**
   - Go to: https://github.com/coreybutler/nvm-windows/releases
   - Download `nvm-setup.exe`
   - Run the installer

2. **Install Node.js via NVM**
   ```powershell
   # Install Node.js 24.11.0
   nvm install 24.11.0
   
   # Use this version
   nvm use 24.11.0
   
   # Verify
   node -v
   npm -v
   ```

### Option 3: Chocolatey (If You Have It)

```powershell
# Run PowerShell as Administrator
choco install nodejs-lts

# Verify
node -v
npm -v
```

### Option 4: Winget (Windows 10/11)

```powershell
# Run PowerShell as Administrator
winget install OpenJS.NodeJS.LTS

# Verify
node -v
npm -v
```

## What Version Should I Install?

| Version | Status | Recommendation |
|---------|--------|----------------|
| **24.11.0+** | ✅ LTS (Krypton) | **Recommended** - Current LTS, well-supported |
| 20.x | ✅ LTS (Iron) | Previous LTS, still supported |
| 18.x | ✅ OK | Minimum supported version |
| 25.x or newer | ⚠️ Current | May work but not tested with PrismQ |
| 16.x or older | ❌ Too old | Not supported |

**For PrismQ, install Node.js 24.11.0 or higher (current LTS recommended).**

## Need More Help?

See the full **[Node.js Installation Guide](NODEJS_INSTALLATION.md)** for:
- Detailed troubleshooting steps
- Linux and macOS instructions
- Advanced configuration
- Permission issues
- Multiple version management

## Quick Links

- **Download Node.js**: https://nodejs.org/
- **NVM for Windows**: https://github.com/coreybutler/nvm-windows
- **Full Installation Guide**: [NODEJS_INSTALLATION.md](NODEJS_INSTALLATION.md)
- **Setup Guide**: [SETUP.md](SETUP.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**Having the exact error from the issue?**

```
npm : The term 'npm' is not recognized...
node : The term 'node' is not recognized...
```

→ **This means Node.js is not installed.** Follow Option 1 above (Official Installer).
