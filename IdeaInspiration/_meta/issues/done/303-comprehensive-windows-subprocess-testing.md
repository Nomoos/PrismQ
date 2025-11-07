# Issue #303: Add Comprehensive Testing for Windows Subprocess Execution

**Priority**: HIGH  
**Type**: Testing/Infrastructure  
**Module**: Client/Backend  
**Estimated**: 3-5 days  
**Assigned To**: Worker 04 - QA/Testing  
**Dependencies**: None

---

## Problem Statement

The problem statement highlighted that the Windows Event Loop Issue (async subprocess on Windows) was a critical problem that has been solved, but there is currently insufficient automated testing to ensure this fix remains working across different environments and future changes.

### Background

The PrismQ backend encountered a `NotImplementedError` when trying to create subprocesses on Windows because Python's asyncio uses `SelectorEventLoop` by default on Windows, which doesn't support asynchronous subprocess operations. The solution involved:

1. Setting `WindowsProactorEventLoopPolicy` in `uvicorn_runner.py`
2. Creating `SubprocessWrapper` with platform detection
3. Adding environment variable support (`PRISMQ_RUN_MODE`)

However, this fix is currently:
- Not comprehensively tested on Windows
- Could regress with Python version updates
- Could be broken by asyncio library changes
- Lacks integration tests for the complete subprocess flow

---

## Requirements

### Functional Requirements

1. **Unit Tests for Subprocess Wrapper**
   - Test platform detection (Windows vs. Unix)
   - Test run mode selection (asyncio vs. threaded)
   - Test environment variable override
   - Test fallback behavior

2. **Integration Tests for Module Execution**
   - Test complete module launch flow on Windows
   - Test subprocess creation with ProactorEventLoop
   - Test stdout/stderr capture
   - Test process completion handling
   - Test error scenarios

3. **Event Loop Policy Tests**
   - Test uvicorn_runner sets correct policy on Windows
   - Test warning when incorrect policy detected
   - Test multiple subprocess launches sequentially
   - Test concurrent subprocess execution

4. **Cross-Platform Tests**
   - Tests should pass on both Windows and Linux
   - Skip platform-specific tests appropriately
   - Mock platform-specific behavior when needed

### Non-Functional Requirements

1. **Coverage**: Achieve >90% coverage for subprocess-related code
2. **Reliability**: Tests should not be flaky
3. **Speed**: Test suite should complete in <2 minutes
4. **Maintainability**: Tests should be easy to understand and update

---

## Implementation Plan

### Phase 1: Unit Tests for SubprocessWrapper (1.5 days)

1. **Create Test File**
   - [ ] Create `Client/Backend/tests/core/test_subprocess_wrapper.py`
   - [ ] Set up test fixtures and mocks
   - [ ] Add platform detection tests

2. **Test Run Mode Selection**
   - [ ] Test auto-detection on Windows (should be ASYNCIO)
   - [ ] Test auto-detection on Unix (should be ASYNCIO)
   - [ ] Test manual mode override
   - [ ] Test environment variable override (`PRISMQ_RUN_MODE`)
   - [ ] Test invalid mode handling

3. **Test Subprocess Creation**
   - [ ] Test asyncio mode subprocess creation
   - [ ] Test threaded mode subprocess creation
   - [ ] Test command building
   - [ ] Test working directory handling
   - [ ] Test stdout/stderr pipe setup

**Example Tests:**

```python
# Client/Backend/tests/core/test_subprocess_wrapper.py
import pytest
import asyncio
import sys
from unittest.mock import patch, MagicMock
from src.core.subprocess_wrapper import SubprocessWrapper, RunMode

class TestSubprocessWrapper:
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_auto_detect_windows_mode(self):
        """Test that Windows auto-detects ASYNCIO mode."""
        wrapper = SubprocessWrapper()
        assert wrapper.mode == RunMode.ASYNCIO
    
    @pytest.mark.skipif(sys.platform == 'win32', reason="Unix-specific test")
    def test_auto_detect_unix_mode(self):
        """Test that Unix auto-detects ASYNCIO mode."""
        wrapper = SubprocessWrapper()
        assert wrapper.mode == RunMode.ASYNCIO
    
    def test_manual_mode_override(self):
        """Test manual run mode specification."""
        wrapper = SubprocessWrapper(mode=RunMode.THREADED)
        assert wrapper.mode == RunMode.THREADED
    
    @patch.dict('os.environ', {'PRISMQ_RUN_MODE': 'threaded'})
    def test_environment_variable_override(self):
        """Test PRISMQ_RUN_MODE environment variable."""
        wrapper = SubprocessWrapper()
        assert wrapper.mode == RunMode.THREADED
    
    @pytest.mark.asyncio
    async test_create_subprocess_asyncio_mode(self):
        """Test subprocess creation in ASYNCIO mode."""
        wrapper = SubprocessWrapper(mode=RunMode.ASYNCIO)
        
        # Create a simple echo process
        process, stdout, stderr = await wrapper.create_subprocess(
            'echo', 'test',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        assert process is not None
        assert stdout is not None
        assert stderr is not None
        
        # Wait for process
        exit_code = await process.wait()
        assert exit_code == 0
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    async def test_windows_subprocess_no_error(self):
        """Test that Windows subprocess creation doesn't raise NotImplementedError."""
        # This test verifies the fix for the Windows Event Loop Issue
        wrapper = SubprocessWrapper(mode=RunMode.ASYNCIO)
        
        # Should not raise NotImplementedError
        process, stdout, stderr = await wrapper.create_subprocess(
            'cmd', '/c', 'echo test',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        assert process is not None
        exit_code = await process.wait()
        assert exit_code == 0
```

### Phase 2: Integration Tests for Module Runner (1.5 days)

1. **Create Integration Test File**
   - [ ] Create `Client/Backend/tests/integration/test_module_execution_windows.py`
   - [ ] Set up test database and fixtures
   - [ ] Create test module scripts

2. **Test Complete Module Launch Flow**
   - [ ] Test module launch on Windows
   - [ ] Test subprocess spawning with ProactorEventLoop
   - [ ] Test log capture and streaming
   - [ ] Test run status updates
   - [ ] Test error handling

3. **Test Concurrent Execution**
   - [ ] Test multiple modules running simultaneously
   - [ ] Test process isolation
   - [ ] Test resource cleanup

**Example Integration Tests:**

```python
# Client/Backend/tests/integration/test_module_execution_windows.py
import pytest
import asyncio
import sys
from pathlib import Path
from src.core.module_runner import ModuleRunner
from src.core.run_registry import RunRegistry
from src.core.process_manager import ProcessManager
from src.core.output_capture import OutputCapture

@pytest.mark.integration
@pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
class TestWindowsModuleExecution:
    
    @pytest.mark.asyncio
    async def test_launch_module_on_windows(self, tmp_path):
        """Test complete module launch flow on Windows."""
        # Create test script
        test_script = tmp_path / "test_module.py"
        test_script.write_text("""
import sys
print("Module started")
print("Processing...", file=sys.stderr)
print("Module completed")
""")
        
        # Set up module runner with Windows event loop policy
        registry = RunRegistry()
        process_manager = ProcessManager()
        output_capture = OutputCapture()
        
        runner = ModuleRunner(
            registry=registry,
            process_manager=process_manager,
            output_capture=output_capture
        )
        
        # Launch module
        run = await runner.execute_module(
            module_id="test-module",
            module_name="Test Module",
            script_path=test_script,
            parameters={},
            save_config=False
        )
        
        # Wait for completion
        await asyncio.sleep(2)
        
        # Verify run completed successfully
        final_run = runner.get_run_status(run.run_id)
        assert final_run.status == "COMPLETED"
        assert final_run.exit_code == 0
        
        # Verify logs captured
        logs = output_capture.get_logs(run.run_id)
        assert any("Module started" in log.message for log in logs)
        assert any("Module completed" in log.message for log in logs)
    
    @pytest.mark.asyncio
    async def test_concurrent_modules_windows(self, tmp_path):
        """Test running multiple modules concurrently on Windows."""
        # Create two test scripts
        script1 = tmp_path / "module1.py"
        script1.write_text("import time; print('Module 1'); time.sleep(1); print('Done 1')")
        
        script2 = tmp_path / "module2.py"
        script2.write_text("import time; print('Module 2'); time.sleep(1); print('Done 2')")
        
        # Set up runner
        runner = ModuleRunner(
            registry=RunRegistry(),
            process_manager=ProcessManager(),
            output_capture=OutputCapture()
        )
        
        # Launch both modules
        run1 = await runner.execute_module("mod1", "Module 1", script1, {}, save_config=False)
        run2 = await runner.execute_module("mod2", "Module 2", script2, {}, save_config=False)
        
        # Wait for both to complete
        await asyncio.sleep(3)
        
        # Verify both completed
        assert runner.get_run_status(run1.run_id).status == "COMPLETED"
        assert runner.get_run_status(run2.run_id).status == "COMPLETED"
```

### Phase 3: Event Loop Policy Tests (1 day)

1. **Create Event Loop Test File**
   - [ ] Create `Client/Backend/tests/test_event_loop_policy.py`
   - [ ] Test uvicorn_runner policy setup
   - [ ] Test policy detection and warnings

2. **Test Policy Configuration**
   - [ ] Test ProactorEventLoopPolicy set on Windows
   - [ ] Test default policy on Unix
   - [ ] Test warning when incorrect policy detected
   - [ ] Test multiple subprocess launches work

**Example Event Loop Tests:**

```python
# Client/Backend/tests/test_event_loop_policy.py
import pytest
import sys
import asyncio
from unittest.mock import patch, MagicMock

@pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
class TestWindowsEventLoopPolicy:
    
    def test_proactor_event_loop_policy_set(self):
        """Test that ProactorEventLoopPolicy is set on Windows."""
        import src.uvicorn_runner
        
        # uvicorn_runner should have set the policy
        policy = asyncio.get_event_loop_policy()
        assert isinstance(policy, asyncio.WindowsProactorEventLoopPolicy)
    
    def test_subprocess_creation_works_with_proactor(self):
        """Test that subprocess creation works with ProactorEventLoop."""
        async def create_subprocess_test():
            # This should not raise NotImplementedError
            process = await asyncio.create_subprocess_exec(
                'cmd', '/c', 'echo test',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.wait()
            return True
        
        result = asyncio.run(create_subprocess_test())
        assert result is True
    
    @patch('sys.platform', 'win32')
    @patch('asyncio.get_event_loop_policy')
    def test_warning_on_incorrect_policy(self, mock_get_policy, caplog):
        """Test that warning is logged if incorrect policy detected."""
        # Mock incorrect policy
        mock_get_policy.return_value = asyncio.DefaultEventLoopPolicy()
        
        # Import should trigger warning check
        import importlib
        import src.core.module_runner
        importlib.reload(src.core.module_runner)
        
        # Check for warning in logs
        # (Implementation depends on how warnings are logged)
```

### Phase 4: CI/CD Integration (0.5 day)

1. **Add Windows CI Job**
   - [ ] Add Windows runner to GitHub Actions
   - [ ] Install Python 3.10 on Windows
   - [ ] Run full test suite on Windows
   - [ ] Report coverage separately for Windows

2. **Update CI Configuration**
   - [ ] Add `.github/workflows/test-windows.yml`
   - [ ] Configure matrix testing (Windows + Linux)
   - [ ] Set up test reporting
   - [ ] Configure coverage thresholds

**Example GitHub Actions Workflow:**

```yaml
# .github/workflows/test-windows.yml
name: Windows Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test-windows:
    runs-on: windows-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python 3.10
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          cd Client/Backend
          pip install -e .
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run tests
        run: |
          cd Client/Backend
          pytest tests/ -v --cov=src --cov-report=xml --cov-report=term
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./Client/Backend/coverage.xml
          flags: windows
```

### Phase 5: Documentation (0.5 day)

1. **Document Testing Strategy**
   - [ ] Add testing guide to `Client/Backend/_meta/docs/TESTING.md`
   - [ ] Document Windows-specific test requirements
   - [ ] Explain how to run tests on Windows
   - [ ] Document CI/CD setup

2. **Update README**
   - [ ] Add Windows testing badge
   - [ ] Document platform-specific testing
   - [ ] Link to testing guide

---

## Success Criteria

- [ ] >90% test coverage for subprocess-related code
- [ ] All Windows-specific tests passing on Windows CI
- [ ] All cross-platform tests passing on both Windows and Linux
- [ ] No flaky tests (100% pass rate over 10 runs)
- [ ] CI/CD pipeline includes Windows testing
- [ ] Documentation complete and accurate
- [ ] Event loop policy fix validated with tests
- [ ] Regression prevention for Windows subprocess issue

---

## Test Coverage Targets

### SubprocessWrapper
- [ ] 95% line coverage
- [ ] All run modes tested
- [ ] All platform variations tested
- [ ] Error cases handled

### ModuleRunner
- [ ] 90% line coverage for Windows-specific paths
- [ ] Subprocess creation tested
- [ ] Error handling tested
- [ ] Concurrent execution tested

### Event Loop Policy
- [ ] Policy setup tested
- [ ] Warning detection tested
- [ ] Multiple subprocess launches tested

---

## Related Issues

- **Issue #301**: Document YouTube Shorts Module Flow (references Windows fix)
- **Web Client #103**: Backend Module Runner (✅ Complete - needs testing)
- **Problem Statement**: Windows Event Loop Issue (already fixed, needs testing)

---

## References

### Code Locations

- **SubprocessWrapper**: `Client/Backend/src/core/subprocess_wrapper.py`
- **ModuleRunner**: `Client/Backend/src/core/module_runner.py`
- **Uvicorn Runner**: `Client/Backend/src/uvicorn_runner.py`
- **Existing Tests**: `Client/Backend/tests/`

### Documentation

- Python asyncio: https://docs.python.org/3/library/asyncio.html
- Windows ProactorEventLoop: https://docs.python.org/3/library/asyncio-platforms.html#windows
- pytest-asyncio: https://github.com/pytest-dev/pytest-asyncio

### Problem Statement Reference

The problem statement describes:
> "To solve this, the project introduced a custom Uvicorn runner that ensures the proper event loop policy is set on Windows. In src/uvicorn_runner.py, before starting the FastAPI server, it explicitly sets the ProactorEventLoop as the event loop policy for Windows"

This fix needs comprehensive testing to ensure it doesn't regress.

---

## Notes

- This is **critical infrastructure testing** to prevent regressions
- Tests validate the **Windows Event Loop fix** is working correctly
- Can be worked on **independently** without blocking feature development
- Provides **confidence** that subprocess execution works across platforms
- Sets up **CI/CD** for ongoing validation
- Estimated effort: **3-5 days** for complete test suite and CI setup

---

**Status**: Ready to Start  
**Created**: 2025-11-04  
**Last Updated**: 2025-11-04
