# Issue #111: Testing and Performance Optimization

**Type**: Testing & Performance  
**Priority**: High  
**Status**: New  
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM  
**Estimated Duration**: 2 weeks  
**Dependencies**: #110 (Integration)  
**Can be parallelized with**: #112 (Documentation)

---

## Description

Conduct comprehensive testing of the entire system and optimize performance. This includes unit tests, integration tests, E2E tests, load testing, and performance profiling.

## Testing Strategy

### 1. Backend Unit Tests (pytest)

```python
# Backend/tests/test_module_runner.py

import pytest
from src.core.module_runner import ModuleRunner
from src.core.run_registry import RunRegistry
from src.core.process_manager import ProcessManager

@pytest.fixture
def runner():
    registry = RunRegistry()
    process_manager = ProcessManager()
    return ModuleRunner(registry, process_manager)

@pytest.mark.asyncio
async def test_execute_module_success(runner):
    """Test successful module execution."""
    run = await runner.execute_module(
        module_id="test-module",
        script_path=Path("tests/fixtures/success.py"),
        parameters={}
    )
    
    assert run.run_id is not None
    assert run.status == "queued"

@pytest.mark.asyncio
async def test_concurrent_run_limit(runner):
    """Test concurrent run limit enforcement."""
    runner.max_concurrent_runs = 2
    
    # Start 2 runs
    run1 = await runner.execute_module(...)
    run2 = await runner.execute_module(...)
    
    # Third should fail
    with pytest.raises(RuntimeError, match="Max concurrent runs"):
        await runner.execute_module(...)

# Backend/tests/test_config_storage.py

def test_save_and_load_config(tmp_path):
    """Test configuration persistence."""
    storage = ConfigStorage(tmp_path)
    
    params = {"max_results": 100, "category": "Gaming"}
    storage.save_config("test-module", params)
    
    loaded = storage.get_config("test-module")
    assert loaded == params

# Run with: pytest Backend/tests/ -v --cov=src --cov-report=html
```

### 2. Frontend Unit Tests (Vitest)

```typescript
// Frontend/tests/unit/ModuleCard.spec.ts

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ModuleCard from '@/components/ModuleCard.vue'

describe('ModuleCard', () => {
  it('renders module information', () => {
    const module = {
      id: 'test',
      name: 'Test Module',
      description: 'Test description',
      category: 'Test',
      tags: ['tag1'],
      total_runs: 10,
      success_rate: 95
    }
    
    const wrapper = mount(ModuleCard, {
      props: { module }
    })
    
    expect(wrapper.text()).toContain('Test Module')
    expect(wrapper.text()).toContain('Test description')
  })
  
  it('emits launch event when button clicked', async () => {
    const wrapper = mount(ModuleCard, { props: { module } })
    
    await wrapper.find('button').trigger('click')
    
    expect(wrapper.emitted('launch')).toBeTruthy()
  })
})

// Run with: npm run test:unit
```

### 3. E2E Tests (Playwright)

```typescript
// Frontend/tests/e2e/module-launch.spec.ts

import { test, expect } from '@playwright/test'

test('launch module workflow', async ({ page }) => {
  // Navigate to dashboard
  await page.goto('http://localhost:5173')
  
  // Wait for modules to load
  await page.waitForSelector('.module-card')
  
  // Click first module's launch button
  await page.click('.module-card button:has-text("Launch")')
  
  // Modal should open
  await expect(page.locator('.modal-content')).toBeVisible()
  
  // Fill in parameters
  await page.fill('input[name="max_results"]', '50')
  await page.selectOption('select[name="category"]', 'Gaming')
  
  // Launch module
  await page.click('button:has-text("Launch")')
  
  // Should navigate to run details
  await expect(page).toHaveURL(/\/runs\/run_/)
  
  // Log viewer should be visible
  await expect(page.locator('.log-viewer')).toBeVisible()
  
  // Logs should start streaming
  await page.waitForSelector('.log-entry', { timeout: 10000 })
})

// Run with: npx playwright test
```

### 4. API Integration Tests

```python
# Backend/tests/test_api_integration.py

@pytest.mark.asyncio
async def test_api_workflow():
    """Test complete API workflow."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Health check
        response = await client.get("/api/health")
        assert response.status_code == 200
        
        # Get modules
        response = await client.get("/api/modules")
        assert response.status_code == 200
        
        # Get module config
        response = await client.get("/api/modules/test-module/config")
        assert response.status_code == 200
        
        # Save config
        response = await client.post(
            "/api/modules/test-module/config",
            json={"parameters": {"key": "value"}}
        )
        assert response.status_code == 200
```

### 5. Load Testing (Locust)

```python
# Backend/tests/load/locustfile.py

from locust import HttpUser, task, between

class WebClientUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def get_modules(self):
        self.client.get("/api/modules")
    
    @task(2)
    def get_runs(self):
        self.client.get("/api/runs")
    
    @task(1)
    def launch_module(self):
        self.client.post(
            "/api/modules/test-module/run",
            json={"parameters": {}, "save_config": False}
        )

# Run with: locust -f tests/load/locustfile.py
```

## Performance Optimization

### 1. Backend Optimizations

```python
# Use connection pooling for better performance
from functools import lru_cache

@lru_cache
def get_module_registry():
    """Cache module registry to avoid repeated file reads."""
    return ModuleRegistry()

# Optimize log retrieval
class OutputCapture:
    def get_logs(self, run_id: str, tail: int = 500):
        """Use deque for efficient tail retrieval."""
        logs = self.log_buffers.get(run_id, deque())
        return list(logs)[-tail:] if tail else list(logs)

# Add database indexes (if using DB later)
# CREATE INDEX idx_runs_status ON runs(status);
# CREATE INDEX idx_runs_module_id ON runs(module_id);
```

### 2. Frontend Optimizations

```typescript
// Use virtual scrolling for large log lists
import { useVirtualizer } from '@tanstack/vue-virtual'

// Debounce search input
import { debounce } from 'lodash-es'

const searchModules = debounce((query: string) => {
  // Perform search
}, 300)

// Lazy load components
const RunDetails = defineAsyncComponent(() => 
  import('@/views/RunDetails.vue')
)

// Optimize re-renders with computed properties
const filteredModules = computed(() => 
  modules.value.filter(m => 
    m.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
)
```

### 3. Bundle Optimization

```typescript
// vite.config.ts

export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router', 'pinia'],
          'charts': ['chart.js'], // if using charts
        }
      }
    },
    chunkSizeWarningLimit: 1000
  }
})
```

## Performance Targets

### Backend
- API response time: <100ms for GET requests
- Module launch time: <500ms
- Concurrent runs: Support 10+ without degradation
- Log capture rate: >10,000 lines/second
- Memory usage: <500MB for 10 concurrent runs
- CPU usage: <50% average

### Frontend
- Initial load: <2 seconds
- Bundle size: <500KB (gzipped)
- FPS: 60fps during log streaming
- Memory: <100MB in browser
- SSE latency: <100ms

## Testing Checklist

### Functional Tests
- [ ] All API endpoints work correctly
- [ ] Module discovery works
- [ ] Module launching works
- [ ] Log streaming works
- [ ] Configuration save/load works
- [ ] Multiple concurrent runs work
- [ ] Run cancellation works
- [ ] Error handling works

### Performance Tests
- [ ] Load test with 10 concurrent runs
- [ ] Load test with 100 API requests/second
- [ ] Log streaming with 1000+ lines
- [ ] Memory usage under load
- [ ] CPU usage under load

### UI/UX Tests
- [ ] All pages render correctly
- [ ] Navigation works
- [ ] Forms validate correctly
- [ ] Notifications display
- [ ] Responsive design (optional for desktop app)
- [ ] Accessibility (keyboard navigation, ARIA)

### Compatibility Tests
- [ ] Chrome browser
- [ ] Firefox browser
- [ ] Edge browser
- [ ] Windows 10/11

---

## Tasks

### Testing
- [ ] Write unit tests for all backend modules
- [ ] Write unit tests for all frontend components
- [ ] Create E2E test suite
- [ ] Set up CI/CD pipeline for tests
- [ ] Achieve >80% code coverage
- [ ] Run load tests
- [ ] Profile performance

### Optimization
- [ ] Optimize API response times
- [ ] Optimize frontend bundle size
- [ ] Optimize log streaming performance
- [ ] Add caching where appropriate
- [ ] Optimize database queries (if applicable)
- [ ] Profile and fix bottlenecks

### Documentation
- [ ] Document test procedures
- [ ] Document performance benchmarks
- [ ] Create testing guidelines

---

## Acceptance Criteria

- [x] Unit test coverage >80%
- [x] All E2E tests pass
- [x] Load tests meet performance targets
- [x] No memory leaks detected
- [x] API response times meet targets
- [x] Frontend bundle size optimized
- [x] All browsers supported
- [x] CI/CD pipeline runs tests automatically

## Tools

- **Backend Testing**: pytest, pytest-asyncio, pytest-cov
- **Frontend Testing**: Vitest, @vue/test-utils, Playwright
- **Load Testing**: Locust
- **Profiling**: cProfile (Python), Chrome DevTools
- **Coverage**: coverage.py, c8

## Related Issues

- **Depends on**: #110 (Integration)
- **Parallel**: #112 (Documentation)

## References

- [pytest Documentation](https://docs.pytest.org/)
- [Vitest](https://vitest.dev/)
- [Playwright](https://playwright.dev/)
- [Locust Load Testing](https://locust.io/)
