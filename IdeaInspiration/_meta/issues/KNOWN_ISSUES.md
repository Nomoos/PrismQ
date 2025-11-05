# Known Issues

This document tracks known issues across the PrismQ.IdeaInspiration ecosystem.

## Current Issues

### Windows Subprocess Execution

**Issue**: Windows subprocess NotImplementedError with asyncio
- **Severity**: ✅ RESOLVED (as of commit 3b818c7)
- **Module**: Client/Backend
- **Description**: Windows users experienced `NotImplementedError` when running modules due to asyncio event loop policy issues. The default `SelectorEventLoop` on Windows doesn't support subprocess operations, requiring `WindowsProactorEventLoopPolicy`.
- **Affected Modules**: ALL modules (YouTube, reddit-posts, hacker-news, etc.)
- **Solution**: SubprocessWrapper now auto-detects Windows and uses THREADED mode by default, which works regardless of server startup method or event loop policy.
- **Status**: ✅ RESOLVED
- **References**: 
  - Issue #304: Windows Subprocess Deployment Fix
  - Issue #305: YouTube Module Verification
  - Issue #306: Complete Resolution Index
- **Verification**: All modules verified to use centralized SubprocessWrapper (Issue #305)
- **Impact**: Zero - fix is transparent to users and modules

### Configuration Management

**Issue**: Multiple .env file locations across modules
- **Severity**: Low
- **Module**: ConfigLoad, Model
- **Description**: Each module may create its own .env file, leading to configuration fragmentation
- **Workaround**: Use ConfigLoad's auto-discovery to find topmost PrismQ directory
- **Status**: Documented, not critical

### Database Schema

**Issue**: Limited database migration support
- **Severity**: Medium
- **Module**: Model
- **Description**: Schema changes require manual database recreation
- **Impact**: Development only, not production-ready
- **Planned Fix**: Issue #002 - Database Integration with Alembic migrations
- **Status**: Planned for Phase 1

### Performance

**Issue**: No GPU acceleration in current implementations
- **Severity**: Medium
- **Module**: Classification, Scoring
- **Description**: All processing is CPU-bound, not utilizing RTX 5090
- **Impact**: Slower processing for large batches
- **Planned Fix**: Issue #003 - Batch Processing Optimization, #009 - ML Enhanced Classification
- **Status**: Planned for Phase 2

**Issue**: No batch processing optimization
- **Severity**: Medium
- **Module**: All
- **Description**: Processing items one-by-one is inefficient
- **Impact**: Lower throughput than possible
- **Planned Fix**: Issue #003 - Batch Processing Optimization
- **Status**: Planned for Phase 2

### Sources Module

**Issue**: Limited source integrations
- **Severity**: Low
- **Module**: Sources
- **Description**: Many documented sources not yet implemented
- **Impact**: Limited content collection capabilities
- **Planned Fix**: Issue #008 - Advanced Source Integrations
- **Status**: Planned for Phase 4

**Issue**: No rate limiting implementation
- **Severity**: Medium
- **Module**: Sources
- **Description**: Could hit API rate limits without protection
- **Impact**: Collection failures, potential API bans
- **Planned Fix**: Issue #008 - Advanced Source Integrations
- **Status**: Planned for Phase 4

### Testing

**Issue**: No integration tests
- **Severity**: Medium
- **Module**: All
- **Description**: Only unit tests exist, no end-to-end testing
- **Impact**: Integration issues may not be caught early
- **Planned Fix**: Issue #001 - Unified Pipeline Integration
- **Status**: Planned for Phase 1

**Issue**: Missing test data for some scenarios
- **Severity**: Low
- **Module**: Classification, Scoring
- **Description**: Edge cases not fully covered in tests
- **Impact**: Potential issues with unusual content
- **Planned Fix**: Ongoing test improvements
- **Status**: Continuous improvement

### Documentation

**Issue**: API documentation incomplete
- **Severity**: Low
- **Module**: All
- **Description**: Some functions lack detailed docstrings
- **Impact**: Developer experience
- **Planned Fix**: Ongoing documentation improvements
- **Status**: Continuous improvement

### Monitoring

**Issue**: No production monitoring
- **Severity**: High (for production)
- **Module**: All
- **Description**: No metrics, logging aggregation, or alerting
- **Impact**: Cannot track system health in production
- **Planned Fix**: Issue #006 - Monitoring & Observability
- **Status**: Planned for Phase 2

---

## Reporting Issues

### GitHub Issues

Report new issues at: https://github.com/Nomoos/PrismQ.IdeaInspiration/issues

### Hardware-Specific Issues

When reporting issues on the target platform (Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM):
- Include GPU driver version
- Include CUDA/PyTorch version (if applicable)
- Include system memory usage
- Include GPU memory usage
- Include Windows version

### General Issue Template

```markdown
## Issue Title

**Type**: Bug / Feature / Enhancement
**Priority**: High / Medium / Low
**Module**: Classification / ConfigLoad / Model / Scoring / Sources / Other
**Status**: New / In Progress / Done

### Description
Brief description of the issue

### Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

### Expected Behavior
What should happen

### Actual Behavior
What actually happens

### Environment
- OS: Windows [version]
- GPU: NVIDIA RTX 5090
- Driver: [version]
- Python: [version]
- Module version: [version]

### Additional Context
Add any other context about the problem here
```

---

## Issue Lifecycle

1. **New**: Issue reported and triaged
2. **Acknowledged**: Issue confirmed and prioritized
3. **Planned**: Issue added to roadmap
4. **In Progress**: Issue being worked on (move to _meta/issues/wip/)
5. **Done**: Issue resolved (move to _meta/issues/done/)

---

**Last Updated**: 2025-11-04
