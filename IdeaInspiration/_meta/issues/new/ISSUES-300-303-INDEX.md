# Issue #300-303 Index - Worker-Based Parallelization

**Created**: 2025-11-04  
**Source**: Research flow analysis of YouTube Shorts Source module  
**Purpose**: Quick reference for all worker-based issues

---

## Issue Overview

| # | Title | Priority | Worker | Estimated | Status |
|---|-------|----------|--------|-----------|--------|
| **300** | Implement YouTube Shorts Keyword Search Mode | HIGH | Worker 01 | 1-2 weeks | 🟢 Ready |
| **301** | Document YouTube Shorts Module Flow and Architecture | MEDIUM | Worker 02 | 3-5 days | 🟢 Ready |
| **302** | Improve Module Parameter Validation and Mode Switching | MEDIUM | Worker 03 | 1 week | 🟢 Ready |
| **303** | Add Comprehensive Testing for Windows Subprocess Execution | HIGH | Worker 04 | 3-5 days | 🟢 Ready |

---

## Issue #300: Implement YouTube Shorts Keyword Search Mode

**Worker**: Worker 01 (Backend/Source Development)  
**File**: [Worker01/300-implement-youtube-keyword-search.md](./Worker01/300-implement-youtube-keyword-search.md)

### Summary
Implement true keyword search functionality for the YouTube Shorts Source module. Currently, keyword mode falls back to showing trending results instead of actual search results.

### Why It Matters
- Enables content discovery by specific topics/keywords
- Completes the YouTube Shorts module feature set
- Improves user value proposition

### Key Tasks
- Research yt-dlp vs YouTube API search capabilities
- Create YouTubeSearchPlugin with keyword search
- Update CLI to use search plugin for keyword mode
- Remove "not implemented" warnings
- Add comprehensive tests

### Success Criteria
- Keyword search returns relevant Shorts for given keywords
- Results filtered to only Shorts (duration < 60s)
- Web client can launch keyword search successfully
- >80% test coverage

---

## Issue #301: Document YouTube Shorts Module Flow and Architecture

**Worker**: Worker 02 (Documentation/Technical Writing)  
**File**: [Worker02/301-document-module-flow-architecture.md](./Worker02/301-document-module-flow-architecture.md)

### Summary
Create comprehensive documentation of the YouTube Shorts Source module execution flow, from web client UI launch through CLI execution and database storage.

### Why It Matters
- Onboarding for new developers
- Debugging reference when issues occur
- Architecture pattern used across all source modules
- Platform-specific considerations need clear documentation

### Key Tasks
- Create EXECUTION_FLOW.md with sequence diagrams
- Create ARCHITECTURE.md with component diagrams
- Create KNOWN_ISSUES.md documenting limitations
- Create TROUBLESHOOTING.md for common problems
- Update main READMEs with links

### Success Criteria
- Complete flow documentation with diagrams
- Architecture patterns clearly explained
- Known issues and limitations documented
- Troubleshooting guide with common errors

---

## Issue #302: Improve Module Parameter Validation and Mode Switching

**Worker**: Worker 03 (Full Stack Development)  
**File**: [Worker03/302-improve-parameter-validation-mode-switching.md](./Worker03/302-improve-parameter-validation-mode-switching.md)

### Summary
Enhance the web client to show/hide parameters dynamically based on selected mode, provide mode-specific validation, and improve user guidance.

### Why It Matters
- Prevents user errors (invalid parameter combinations)
- Improves user experience with clear guidance
- Makes limitations visible (keyword mode warning)
- Reduces support burden

### Key Tasks
- Add conditional parameter display to module schema
- Implement dynamic form in frontend (show/hide fields)
- Add mode-aware validation (backend + frontend)
- Show warnings for known limitations
- Add tooltips and help text

### Success Criteria
- Parameters show/hide based on selected mode
- Required parameters clearly indicated
- Real-time validation feedback
- Warning shown for keyword mode limitation
- Backend rejects invalid combinations

---

## Issue #303: Add Comprehensive Testing for Windows Subprocess Execution

**Worker**: Worker 04 (QA/Testing)  
**File**: [Worker04/303-comprehensive-windows-subprocess-testing.md](./Worker04/303-comprehensive-windows-subprocess-testing.md)

### Summary
Create comprehensive automated tests for the Windows subprocess execution fix (ProactorEventLoop policy) to prevent regressions and ensure reliability.

### Why It Matters
- Validates critical Windows Event Loop fix
- Prevents regression of subprocess functionality
- Ensures cross-platform compatibility
- Provides CI/CD validation

### Key Tasks
- Create unit tests for SubprocessWrapper
- Create integration tests for module execution on Windows
- Test event loop policy configuration
- Add Windows CI/CD job to GitHub Actions
- Document testing strategy

### Success Criteria
- >90% test coverage for subprocess code
- All Windows-specific tests passing on Windows CI
- Cross-platform tests passing on Windows and Linux
- No flaky tests
- CI/CD includes Windows testing

---

## Parallelization Strategy

### Can All Start Immediately ✅

```
Worker 01 (Backend)    ─────────────────→  #300 (1-2 weeks)
                      
Worker 02 (Docs)       ─────────→  #301 (3-5 days)

Worker 03 (Full Stack) ──────────────→  #302 (1 week)

Worker 04 (QA)         ─────────→  #303 (3-5 days)
```

**Dependencies**: NONE - All can work in parallel  
**Timeline**: 1-2 weeks for all issues  
**Time Savings**: 60-70% vs sequential development

---

## Code Areas Affected

### No Conflicts ✅

| Issue | Primary Files | Potential Conflicts |
|-------|--------------|---------------------|
| #300 | `Sources/Content/Shorts/YouTube/src/plugins/youtube_search_plugin.py` (new) | ❌ None |
| #301 | `Sources/Content/Shorts/YouTube/docs/` (new), `Client/_meta/docs/ARCHITECTURE.md` | ❌ None |
| #302 | `Client/Frontend/src/components/ModuleLaunchModal.vue`, `Client/Backend/src/api/modules.py` | ❌ None |
| #303 | `Client/Backend/tests/` (new), `.github/workflows/test-windows.yml` (new) | ❌ None |

---

## Integration Points

While issues are independent, they have **logical connections**:

### #300 ↔️ #301
- #300 implements keyword search feature
- #301 documents the implementation
- **Integration**: Documentation updated after feature complete

### #300 ↔️ #302
- #300 adds keyword search backend
- #302 improves keyword mode frontend validation
- **Integration**: Both improve keyword mode from different angles

### #302 ↔️ #303
- #302 adds validation logic
- #303 adds testing infrastructure
- **Integration**: Both improve system reliability

### #301 ↔️ #303
- #301 documents Windows subprocess fix
- #303 tests Windows subprocess fix
- **Integration**: Documentation and tests validate same behavior

---

## Source of Issues

These issues were identified from a **research flow analysis** that examined:

1. **Web Client Module Launch Flow**
   - POST request from frontend → backend API
   - ModuleRunner execution → subprocess spawning
   - Log streaming and status tracking

2. **Windows Event Loop Issue**
   - NotImplementedError with default event loop
   - ProactorEventLoopPolicy solution in uvicorn_runner
   - Need for comprehensive testing → Issue #303

3. **Frontend Launch Confirmation**
   - Parameter passing from UI to backend
   - Need for better validation → Issue #302

4. **YouTube Shorts CLI Behavior**
   - Three modes: trending, channel, keyword
   - Keyword mode not implemented → Issue #300
   - Complex flow needs documentation → Issue #301

---

## Success Metrics

### Individual Metrics

- **#300**: Keyword search functional, >80% coverage
- **#301**: Complete documentation with diagrams
- **#302**: Dynamic validation working, UX improved
- **#303**: >90% test coverage, Windows CI passing

### Overall Metrics

- All 4 issues complete in 1-2 weeks
- Zero merge conflicts
- Smooth integration of features
- System more robust and feature-complete

---

## Next Actions

### For Team Lead

1. **Assign workers** based on skill match
2. **Set up weekly check-ins** for progress tracking
3. **Plan integration meeting** for end of Week 2
4. **Prepare for code reviews** by worker area

### For Individual Contributors

1. **Read your assigned issue** completely
2. **Ask questions** before starting
3. **Create feature branch** following naming convention
4. **Update progress** in daily standups
5. **Request code review** when ready

---

## Related Documentation

- **Main README**: [README.md](./README.md)
- **Worker Organization**: [README-WORKER-ORGANIZATION.md](./README-WORKER-ORGANIZATION.md)
- **Worker Allocation Matrix**: `_meta/issues/WORKER_ALLOCATION_MATRIX.md`
- **Next Steps**: `_meta/issues/NEXT_STEPS.md`

---

**Status**: ✅ All Issues Ready for Parallel Development  
**Created**: 2025-11-04  
**Last Updated**: 2025-11-04
