# Manual Testing Issues Index

**Created**: 2025-12-04  
**Purpose**: Track manual testing of all PrismQ modules by human testers  
**Status**: 🧪 READY FOR TESTING

---

## Overview

This document indexes all manual testing issues for the PrismQ content production platform. Each module has a dedicated testing issue with checklists, test commands, and log submission formats.

---

## Testing Issues

| Issue | Module | Description | Priority | Status |
|-------|--------|-------------|----------|--------|
| [MANUAL-TEST-001](MANUAL-TEST-001-T-Module.md) | **T (Text)** | Text Generation Pipeline testing | High | 🧪 Ready |
| [MANUAL-TEST-002](MANUAL-TEST-002-A-Module.md) | **A (Audio)** | Audio Generation Pipeline testing | High | 🧪 Ready |
| [MANUAL-TEST-003](MANUAL-TEST-003-V-Module.md) | **V (Video)** | Video Generation Pipeline testing | High | 🧪 Ready |
| [MANUAL-TEST-004](MANUAL-TEST-004-P-Module.md) | **P (Publishing)** | Publishing Module testing | Medium | 🧪 Ready |
| [MANUAL-TEST-005](MANUAL-TEST-005-M-Module.md) | **M (Metrics)** | Metrics & Analytics testing | Medium | 🧪 Ready |
| [MANUAL-TEST-006](MANUAL-TEST-006-Client-Module.md) | **Client** | Web Management Interface testing | High | 🧪 Ready |

---

## Platform Workflow

```
T (Text)  →  A (Audio)  →  V (Video)  →  P (Publishing)  →  M (Metrics)
    ↑                                                          ↓
    └──────────────────← Feedback Loop ←───────────────────────┘
```

All modules are coordinated through the **Client** web management interface.

---

## Testing Priority

### Phase 1: Core Pipeline (High Priority)
1. **T Module** - Foundation of the content pipeline
2. **Client Module** - Task queue management
3. **A Module** - Audio generation

### Phase 2: Complete Workflow (High Priority)
4. **V Module** - Video generation

### Phase 3: Distribution & Analytics (Medium Priority)
5. **P Module** - Multi-platform publishing
6. **M Module** - Metrics and analytics

---

## General Test Commands

```bash
# Navigate to repository
cd /home/runner/work/PrismQ/PrismQ

# Run all Python tests
python -m pytest . -v

# Run specific module tests
python -m pytest T/ -v
python -m pytest A/ -v
python -m pytest V/ -v
python -m pytest P/ -v
python -m pytest M/ -v

# Run integration tests
python -m pytest tests/ -v
```

---

## Log Submission Instructions

When submitting test logs, please include:

1. **Environment Details**
   - Date and time
   - Python/Node.js versions
   - Operating system
   - Relevant libraries installed

2. **Test Execution Details**
   - What was tested
   - Test commands run
   - Duration of tests

3. **Logs**
   - Full console output
   - Error messages (if any)
   - Warnings

4. **Results**
   - Pass/fail status for each checklist item
   - Any unexpected behavior
   - Performance observations

5. **Recommendations**
   - Suggested fixes for failures
   - Improvement ideas
   - Questions for clarification

---

## Contact

For questions about testing, tag the relevant worker:
- **Worker01** - Project Manager
- **Worker04** - QA & Testing Specialist
- **Worker10** - Review Master

---

**Last Updated**: 2025-12-04
