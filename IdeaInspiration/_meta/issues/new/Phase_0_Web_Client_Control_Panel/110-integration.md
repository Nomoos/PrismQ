# Issue #110: Integrate Frontend with Backend Services

**Type**: Feature  
**Priority**: High  
**Status**: New  
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM  
**Estimated Duration**: 1 week  
**Dependencies**: All frontend and backend features  
**Can be parallelized with**: None (integration phase)

---

## Description

Bring together all frontend and backend components, replacing mocks with real API calls, testing end-to-end workflows, and ensuring smooth interaction between all parts of the system.

## Integration Tasks

### 1. Replace Mock Data

Remove all hardcoded/mock data from frontend:

```typescript
// Before (mock)
const modules = ref([
  { id: 'test', name: 'Test Module', ... }
])

// After (real API)
const modules = ref([])
onMounted(async () => {
  modules.value = await moduleService.getModules()
})
```

### 2. Configure CORS

```python
# src/main.py

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Environment Configuration

```typescript
// Frontend/src/config.ts

export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  apiPath: '/api',
  sseTimeout: 30000,
  pollInterval: 2000
}

// Update .env
VITE_API_BASE_URL=http://localhost:8000
```

```python
# Backend/src/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "PrismQ Web Client"
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173"]
    max_concurrent_runs: int = 10
    log_dir: str = "./logs"
    config_dir: str = "./configs"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 4. End-to-End Workflows

Test complete user journeys:

**Workflow 1: Launch Module**
1. Open dashboard
2. View available modules
3. Click "Launch" on a module
4. Fill in parameters
5. Click "Launch"
6. Redirect to run details
7. Watch logs stream in real-time
8. See completion status

**Workflow 2: Monitor Multiple Runs**
1. Launch module A
2. Navigate back to dashboard
3. Launch module B
4. View active runs
5. Switch between run logs
6. Cancel one run
7. Wait for other to complete

**Workflow 3: Configuration Management**
1. Launch module with custom parameters
2. Enable "Save configuration"
3. Complete run
4. Launch same module again
5. Verify parameters pre-filled
6. Modify parameters
7. Reset to defaults

### 5. API Integration Checklist

- [ ] GET `/api/modules` - List modules
- [ ] GET `/api/modules/{id}` - Module details
- [ ] GET `/api/modules/{id}/config` - Get config
- [ ] POST `/api/modules/{id}/config` - Save config
- [ ] DELETE `/api/modules/{id}/config` - Delete config
- [ ] POST `/api/modules/{id}/run` - Launch module
- [ ] GET `/api/runs` - List runs
- [ ] GET `/api/runs/{id}` - Run details
- [ ] DELETE `/api/runs/{id}` - Cancel run
- [ ] GET `/api/runs/{id}/logs` - Get logs
- [ ] GET `/api/runs/{id}/logs/stream` - Stream logs (SSE)
- [ ] GET `/api/health` - Health check
- [ ] GET `/api/system/stats` - System stats

### 6. Data Flow Validation

```
Frontend (Vue) ─┐
                ├──> POST /api/modules/youtube-shorts/run
Backend (API)  ─┘      │
                       ▼
                 ModuleRunner.execute_module()
                       │
                       ▼
                 ProcessManager.run_process()
                       │
                       ▼
                 OutputCapture.start_capture()
                       │
                       ▼
                 EventSource (SSE) ◄─── Frontend LogViewer
```

---

## Testing Integration

### Manual Testing Checklist

- [ ] Start backend server (port 8000)
- [ ] Start frontend server (port 5173)
- [ ] Open browser to http://localhost:5173
- [ ] Dashboard loads and displays modules
- [ ] Click module card shows details
- [ ] Launch modal opens with parameters
- [ ] Parameters validate correctly
- [ ] Module launches successfully
- [ ] Redirect to run details works
- [ ] Logs stream in real-time
- [ ] Status updates correctly
- [ ] Cancel button works
- [ ] Multiple runs work concurrently
- [ ] Configuration saves and loads
- [ ] Error notifications display
- [ ] All navigation works

### Integration Test Script

```python
# Backend/tests/test_integration.py

import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_full_workflow():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Get modules
        response = await client.get("/api/modules")
        assert response.status_code == 200
        modules = response.json()["modules"]
        assert len(modules) > 0
        
        module_id = modules[0]["id"]
        
        # 2. Launch module
        response = await client.post(
            f"/api/modules/{module_id}/run",
            json={"parameters": {}, "save_config": False}
        )
        assert response.status_code == 202
        run_id = response.json()["run_id"]
        
        # 3. Get run status
        response = await client.get(f"/api/runs/{run_id}")
        assert response.status_code == 200
        
        # 4. Get logs
        response = await client.get(f"/api/runs/{run_id}/logs")
        assert response.status_code == 200
```

---

## Debugging Common Issues

### Issue: CORS Errors

```
Access to fetch at 'http://localhost:8000/api/modules' from origin 
'http://localhost:5173' has been blocked by CORS policy
```

**Fix**: Ensure CORS middleware configured correctly in backend

### Issue: SSE Not Connecting

```
EventSource failed: network error
```

**Fix**: 
- Check SSE endpoint exists
- Verify no CORS issues
- Check firewall/antivirus blocking

### Issue: API Returns 404

```
GET http://localhost:8000/api/modules 404 (Not Found)
```

**Fix**:
- Verify backend is running
- Check API route registration
- Verify URL paths match

---

## Deployment Checklist

### Backend
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create `.env` file
- [ ] Initialize config directory
- [ ] Run migrations (if any)
- [ ] Start server: `uvicorn src.main:app --reload --host 127.0.0.1 --port 8000`

### Frontend
- [ ] Install dependencies: `npm install`
- [ ] Create `.env` file
- [ ] Configure API URL
- [ ] Start dev server: `npm run dev`
- [ ] Build for production: `npm run build`

---

## Tasks

- [ ] Configure CORS for local development
- [ ] Create environment configuration files
- [ ] Replace all mock data with API calls
- [ ] Test all API endpoints from frontend
- [ ] Verify SSE log streaming works
- [ ] Test all user workflows manually
- [ ] Write integration tests
- [ ] Fix any bugs found during integration
- [ ] Document known issues
- [ ] Create troubleshooting guide

---

## Acceptance Criteria

- [x] All API endpoints accessible from frontend
- [x] No CORS errors
- [x] All user workflows complete successfully
- [x] Real-time log streaming works
- [x] Multiple concurrent runs work
- [x] Configuration persistence works
- [x] Error handling works end-to-end
- [x] No console errors in browser
- [x] No server errors in logs
- [x] Performance is acceptable

## Related Issues

- **Depends on**: All other issues
- **Enables**: #111 (Testing), #112 (Documentation)

## References

- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
