# PrismQ Web Client - Setup Guide

Complete installation and configuration guide for the PrismQ Web Client.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Hardware Requirements

**Minimum:**
- **CPU**: Multi-core processor (dual-core or better)
- **RAM**: 8GB
- **Disk**: 1GB free space
- **Network**: Internet connection for module data collection

**Recommended:**
- **CPU**: AMD Ryzen or Intel Core i5/i7
- **RAM**: 16GB or more
- **Disk**: 5GB free space (for logs and data)
- **GPU**: NVIDIA RTX 5090 (for GPU-accelerated PrismQ modules)

### Software Requirements

**Operating System:**
- Windows 10/11 (Primary platform)
- Linux (Ubuntu 20.04+, Debian 11+)
- macOS 11+ (Community support)

**Required Software:**
- **Python**: 3.10 or higher
- **Node.js**: 18.0 or higher
- **npm**: 8.0 or higher (comes with Node.js)
- **Git**: 2.30 or higher

**Supported Browsers:**
- Chrome 90+
- Firefox 88+
- Edge 90+

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/Nomoos/PrismQ.IdeaInspiration.git
cd PrismQ.IdeaInspiration/Client
```

### Step 2: Backend Setup

#### 2.1. Navigate to Backend Directory

```bash
cd Backend
```

#### 2.2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 2.3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- FastAPI 0.109.0 - Web framework
- Uvicorn - ASGI server
- Pydantic 2.5.0 - Data validation
- Other required dependencies

#### 2.4. Configure Backend Environment

Create a `.env` file from the example:

```bash
cp .env.example .env
```

**Windows:**
```bash
copy .env.example .env
```

Edit `.env` with your preferred settings (or use defaults):

```env
# Application Settings
APP_NAME=PrismQ Web Client
HOST=127.0.0.1
PORT=8000
DEBUG=true

# CORS Settings
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Module Execution Settings
MAX_CONCURRENT_RUNS=10

# Storage Settings
LOG_DIR=./logs
CONFIG_DIR=./configs
DATA_DIR=./data

# Logging
LOG_LEVEL=INFO
```

#### 2.5. Verify Backend Installation

```bash
python -c "import fastapi; import uvicorn; import pydantic; print('Backend dependencies OK')"
```

### Step 3: Frontend Setup

#### 3.1. Navigate to Frontend Directory

Open a new terminal and navigate:

```bash
cd PrismQ.IdeaInspiration/Client/Frontend
```

#### 3.2. Install Node Dependencies

```bash
npm install
```

This installs:
- Vue 3 - Frontend framework
- TypeScript - Type safety
- Vite - Build tool
- Tailwind CSS - Styling
- Axios - HTTP client
- Other required dependencies

#### 3.3. Configure Frontend Environment

Create a `.env` file from the example:

```bash
cp .env.example .env
```

**Windows:**
```bash
copy .env.example .env
```

Edit `.env` to point to your backend:

```env
VITE_API_BASE_URL=http://localhost:8000
```

#### 3.4. Verify Frontend Installation

```bash
npm run type-check
```

### Step 4: Module Configuration

#### 4.1. Configure Available Modules

The backend needs to know which PrismQ modules are available. Edit `Backend/configs/modules.json`:

```json
{
  "modules": [
    {
      "id": "youtube-shorts",
      "name": "YouTube Shorts Source",
      "description": "Collect trending YouTube Shorts videos",
      "category": "Sources/Content/Shorts",
      "script_path": "../../Sources/Content/Shorts/YouTubeShorts/src/main.py",
      "parameters": [
        {
          "name": "max_results",
          "type": "number",
          "default": 50,
          "required": true,
          "description": "Maximum number of videos to collect",
          "min": 1,
          "max": 500
        }
      ],
      "tags": ["youtube", "shorts", "video"]
    }
  ]
}
```

See [MODULES.md](MODULES.md) for detailed information on adding modules.

#### 4.2. Verify Module Paths

Ensure that the `script_path` in `modules.json` points to valid Python scripts in your repository.

## Configuration

### Backend Configuration Reference

All backend configuration is in `Backend/.env`:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application name | PrismQ Web Client | No |
| `HOST` | Server bind address | 127.0.0.1 | No |
| `PORT` | Server port | 8000 | No |
| `DEBUG` | Enable debug mode | true | No |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | http://localhost:5173 | Yes |
| `MAX_CONCURRENT_RUNS` | Max simultaneous module runs | 10 | No |
| `LOG_DIR` | Directory for logs | ./logs | No |
| `CONFIG_DIR` | Directory for configs | ./configs | No |
| `DATA_DIR` | Directory for runtime data | ./data | No |
| `LOG_LEVEL` | Logging level | INFO | No |

### Frontend Configuration Reference

All frontend configuration is in `Frontend/.env`:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `VITE_API_BASE_URL` | Backend API URL | http://localhost:8000 | Yes |

### Advanced Configuration

#### CORS Configuration

If you need to access the web client from a different domain or port:

1. Update `Backend/.env`:
   ```env
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://192.168.1.100:5173
   ```

2. Restart the backend server

#### Port Configuration

To run on different ports:

**Backend:**
```env
PORT=9000
```

**Frontend:**
Update `package.json` or use:
```bash
npm run dev -- --port 3000
```

Then update `Frontend/.env`:
```env
VITE_API_BASE_URL=http://localhost:9000
```

## Running the Application

### Development Mode

#### Option 1: Manual Start (Two Terminals)

**Terminal 1 - Backend:**
```bash
cd Backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd Frontend
npm run dev
```

#### Option 2: Using Development Scripts

**Windows:**
```powershell
# Backend
Client\_meta\scripts\run_dev.ps1

# Frontend (separate terminal)
cd Client\Frontend
npm run dev
```

**Linux/macOS:**
```bash
# Backend
Client/_meta/scripts/run_dev.sh

# Frontend (separate terminal)
cd Client/Frontend
npm run dev
```

### Accessing the Application

Once both servers are running:

- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Verification

### Backend Verification

1. **Check Health Endpoint:**
   ```bash
   curl http://localhost:8000/health
   ```
   Expected response:
   ```json
   {"status": "healthy", "version": "1.0.0"}
   ```

2. **Check Modules Endpoint:**
   ```bash
   curl http://localhost:8000/api/modules
   ```
   Should return list of configured modules.

3. **Check API Documentation:**
   Open http://localhost:8000/docs in your browser. You should see the Swagger UI with all API endpoints.

### Frontend Verification

1. **Open Frontend:**
   Navigate to http://localhost:5173 in your browser.

2. **Check Module Dashboard:**
   You should see a dashboard with all configured modules.

3. **Check Console:**
   Open browser DevTools (F12). Check for any errors in the console. There should be no errors on initial load.

### End-to-End Verification

1. **Launch a Module:**
   - Click "Launch" on any module card
   - Fill in required parameters
   - Click "Launch"
   - Verify you're redirected to run details page

2. **Check Log Streaming:**
   - Logs should appear in real-time
   - Status should update as the module runs

3. **Check Run History:**
   - Return to dashboard
   - Verify the run appears in active/completed runs

## Troubleshooting

### Common Issues

#### Backend Won't Start

**Error: "Address already in use"**

Another process is using port 8000.

**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:8000 | xargs kill -9
```

Or change the port in `Backend/.env`:
```env
PORT=8001
```

**Error: "Module 'fastapi' not found"**

Virtual environment not activated or dependencies not installed.

**Solution:**
```bash
cd Backend
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend Won't Start

**Error: "Cannot find module 'vue'"**

Dependencies not installed.

**Solution:**
```bash
cd Frontend
npm install
```

**Error: "EADDRINUSE: address already in use"**

Port 5173 is in use.

**Solution:**
```bash
npm run dev -- --port 3000
```

Then update `Backend/.env`:
```env
CORS_ORIGINS=http://localhost:3000
```

#### Frontend Can't Connect to Backend

**Error: "Network Error" or CORS errors in browser console**

**Solution:**
1. Verify backend is running: http://localhost:8000/health
2. Check `Frontend/.env` has correct API URL
3. Check `Backend/.env` has frontend origin in CORS_ORIGINS
4. Restart both servers after changing configuration

#### Module Won't Execute

**Error: "Script not found" or module execution fails**

**Solution:**
1. Verify `script_path` in `Backend/configs/modules.json` is correct
2. Check that the Python script exists at that path
3. Verify the module's dependencies are installed
4. Check backend logs in `Backend/logs/` for details

### Getting More Help

1. **Check Logs:**
   - Backend logs: `Backend/logs/app.log`
   - Run logs: `Backend/logs/runs/`
   - Browser console: F12 → Console tab

2. **Enable Debug Mode:**
   ```env
   # Backend/.env
   DEBUG=true
   LOG_LEVEL=DEBUG
   ```

3. **Consult Documentation:**
   - [User Guide](USER_GUIDE.md)
   - [API Reference](API.md)
   - [Troubleshooting Guide](TROUBLESHOOTING.md)

4. **Open an Issue:**
   Visit https://github.com/Nomoos/PrismQ.IdeaInspiration/issues

## Next Steps

After successful installation:

1. **Read the User Guide**: [USER_GUIDE.md](USER_GUIDE.md)
2. **Explore the API**: http://localhost:8000/docs
3. **Configure Your Modules**: [MODULES.md](MODULES.md)
4. **Learn the Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
5. **Start Developing**: [DEVELOPMENT.md](DEVELOPMENT.md)

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-31  
**Maintained by**: PrismQ Development Team
