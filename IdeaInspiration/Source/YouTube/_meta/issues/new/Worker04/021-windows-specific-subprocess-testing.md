# Issue #021: Windows-Specific Subprocess Testing

**Parent Issue**: #001  
**Worker**: Worker 04 - QA/Testing Specialist  
**Status**: New  
**Priority**: High  
**Duration**: 1-2 days  
**Dependencies**: #020

---

## Objective

Ensure worker system works correctly on Windows, especially subprocess management, file paths, and SQLite operations.

---

## Windows-Specific Tests

1. **File Path Handling**
   - Windows path separators
   - Long paths (>260 chars)
   - Special characters

2. **SQLite on Windows**
   - WAL mode performance
   - File locking behavior
   - Concurrent access

3. **Process Management**
   - Worker subprocess spawning
   - Process termination
   - Signal handling

4. **yt-dlp Integration**
   - Downloads on Windows
   - Path handling
   - Proxy settings

---

## Acceptance Criteria

- [ ] All tests pass on Windows
- [ ] Windows-specific issues identified
- [ ] Fixes applied where needed
- [ ] Documentation for Windows quirks

---

**Assignee**: Worker04  
**Timeline**: Week 4, Days 3-4
