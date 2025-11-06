# Quick Start Guide - Running PrismQ Web Client

This guide shows you the easiest way to run the PrismQ Web Client on Windows.

## 🚀 One-Click Start (Recommended)

The fastest way to get started:

1. **Double-click** `_meta\_scripts\run_both.bat`

That's it! The script will:
- ✅ Start the Backend server (http://localhost:8000)
- ✅ Start the Frontend server (http://localhost:5173)
- ✅ Open your browser automatically to http://localhost:5173

You'll see **two new console windows** open - one for Backend and one for Frontend. Keep them open while using the application.

### What You'll See

1. **This launcher window** - Shows progress and then closes automatically
2. **PrismQ Backend Server** window - Shows Backend logs (keep open)
3. **PrismQ Frontend Server** window - Shows Frontend logs (keep open)
4. **Your browser** - Opens to the application at http://localhost:5173

### Stopping the Servers

Simply **close the two server console windows** (Backend and Frontend).

## 🔧 Running Components Separately

If you need to run only one component:

### Backend Only
```cmd
_meta\_scripts\run_backend.bat
```
- Starts Backend on http://localhost:8000
- API docs at http://localhost:8000/docs

### Frontend Only
```cmd
_meta\_scripts\run_frontend.bat
```
- Starts Frontend on http://localhost:5173
- Requires Backend to be running separately

## 📋 Prerequisites

Before running for the first time:

### Backend Requirements
1. **Python 3.10+** installed and in PATH
   - The script will automatically create the virtual environment
   - Dependencies will be installed automatically

**First-time setup is now automatic!** Just run the script and it will:
- Create the virtual environment at `Client\Backend\venv\`
- Install all dependencies from `Client\Backend\requirements.txt`

**Manual setup (optional):**
If you prefer to set up manually:
```cmd
cd Client\Backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Requirements
1. **Node.js 18+** (24.11.0+ recommended)
2. **Dependencies** will be installed automatically if missing

**First-time setup (automatic):**
The script will install npm dependencies automatically if needed.

## 🆘 Troubleshooting

### Script Says "Backend directory not found"
- Make sure you're running the script from the repository root
- The script should be at `_meta\_scripts\run_both.bat`

### Script Says "Python is not installed"
- Install Python 3.10 or higher from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation
- Restart your terminal/command prompt after installation

### Script Says "Virtual environment exists but appears broken"
- The script will automatically recreate the virtual environment
- This can happen if Python was reinstalled at a different location
- Just run the script again and it will fix itself

### Script Says "Node.js is not installed"
- Install Node.js from https://nodejs.org/
- Or see the guide at `Client\docs\NODEJS_INSTALLATION.md`

### Browser Opens But Shows Error
- Wait a few more seconds - servers take 10-15 seconds to fully start
- Check the server console windows for error messages
- Make sure ports 8000 and 5173 are not in use

### Port Already in Use
Kill the process using the port:
```cmd
netstat -ano | findstr :8000
taskkill /PID <pid_from_above> /F
```

## 📚 More Information

- **Full Setup Guide**: `Client\docs\SETUP.md`
- **User Guide**: `Client\docs\USER_GUIDE.md`
- **Troubleshooting**: `Client\docs\TROUBLESHOOTING.md`
- **API Documentation**: http://localhost:8000/docs (when running)

## 💡 Tips

- **First time?** Make sure to complete the Prerequisites section above
- **Development work?** The servers have auto-reload enabled - changes will update automatically
- **Testing?** You can run the Backend and Frontend tests separately (see test documentation)
- **Multiple runs?** You can run multiple instances by changing the ports in `.env` files

---

**Need help?** Check the [Troubleshooting Guide](Client/_meta/docs/TROUBLESHOOTING.md) or open an issue on GitHub.
