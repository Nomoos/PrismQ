# New Issues Directory

> ℹ️ **For issue workflow and management, see**: [ISSUE_MANAGEMENT.md](../../docs/ISSUE_MANAGEMENT.md)
> 
> **For current planning and priorities, see**: [DEVELOPMENT_PLAN.md](../../../DEVELOPMENT_PLAN.md)

---

**Purpose**: Storage for new issues awaiting prioritization and assignment  
**Last Updated**: 2025-11-13  
**Status**: Active issue tracking - See DEVELOPMENT_PLAN.md for current priorities

**Workflow**: See [ISSUE_MANAGEMENT.md](../../docs/ISSUE_MANAGEMENT.md) for complete issue workflow (new → wip → done)

---

## ⚠️ Recent Updates (2025-11-13)

### Worker10 Quality Review Complete

Worker10 completed comprehensive quality review of YouTube Worker Refactor issues (25 total).

**Key Findings**:
- Overall quality: 63% (below 80% target)
- High-quality issues: Worker02 (95%), Worker06 (98%), Worker03 (85%)
- Low-quality issues: Worker04 (25%), Worker10 (30%), Worker05 (45%)
- SOLID analysis coverage: 44% (11/25 issues)

**Action Required**: Worker01 must decide:
- **Option A**: Expand low-quality issues before implementation (3-4 days)
- **Option B**: Fix issues during implementation (risky)
- **Option C**: Accept quality gaps (high risk)

**Documents**:
- Review findings: `Source/Video/YouTube/_meta/issues/new/Worker10/REVIEW_FINDINGS.md`
- Updated: `Source/_meta/issues/new/NEXT_PARALLEL_RUN.md`

---

## Directory Structure

### Worker-Based Organization (Issues #300-303)

Issues organized by worker for **parallel development**:

- **[Worker01/](./Worker01/)** - Backend/Source Development
  - [#300 - Implement YouTube Shorts Keyword Search Mode](./Worker01/300-implement-youtube-keyword-search.md)

- **[Worker02/](./Worker02/)** - Documentation/Technical Writing
  - [#301 - Document YouTube Shorts Module Flow and Architecture](./Worker02/301-document-module-flow-architecture.md)

- **[Worker03/](./Worker03/)** - Full Stack Development
  - [#302 - Improve Module Parameter Validation and Mode Switching](./Worker03/302-improve-parameter-validation-mode-switching.md)

- **[Worker04/](./Worker04/)** - QA/Testing
  - [#303 - Add Comprehensive Testing for Windows Subprocess Execution](./Worker04/303-comprehensive-windows-subprocess-testing.md)

- **[Worker05/](./Worker05/)** - Reserved (Empty)
- **[Worker06/](./Worker06/)** - Reserved (Empty)

**📖 See [README-WORKER-ORGANIZATION.md](./README-WORKER-ORGANIZATION.md) for complete worker-based parallelization strategy**

---

### Infrastructure & DevOps (Issues #200-207)

Repository cleanup and standardization initiatives:

- **[Infrastructure_DevOps/](./Infrastructure_DevOps/)** - Infrastructure improvements
  - See [Infrastructure_DevOps/README.md](./Infrastructure_DevOps/README.md) for all issues

---

## Issue Sources

### Research Flow Analysis (Issues #300-303)

These issues were identified from a comprehensive research flow analysis of the **YouTube Shorts Source module** launch process, which revealed:

1. **Missing Feature**: Keyword search mode not implemented (#300)
2. **Missing Documentation**: Complex flow not documented (#301)
3. **UX Improvement**: Parameter validation can be enhanced (#302)
4. **Testing Gap**: Windows subprocess fix not tested (#303)

The analysis examined:
- Web Client → Backend → Subprocess → CLI execution flow
- Windows Event Loop Issue and its resolution
- Frontend parameter handling and validation
- YouTube Shorts CLI behavior with different modes
- Known limitations and workarounds

---

## Parallelization Potential

### Maximum Parallel Workers: 4+

All current worker-based issues can be developed **simultaneously** with zero dependencies:

| Issue | Worker | Duration | Can Start | Dependencies |
|-------|--------|----------|-----------|--------------|
| #300 | Worker 01 | 1-2 weeks | ✅ Now | None |
| #301 | Worker 02 | 3-5 days | ✅ Now | None |
| #302 | Worker 03 | 1 week | ✅ Now | None |
| #303 | Worker 04 | 3-5 days | ✅ Now | None |

**Timeline**: All can complete in **1-2 weeks** with parallel development

---

## How to Use This Directory

### For Individual Contributors

1. **Browse worker folders** to find issues matching your skills
2. **Read the complete issue** including requirements and implementation plan
3. **Move issue to WIP** when you start working:
   ```bash
   mv _meta/issues/new/Worker01/300-*.md _meta/issues/wip/
   ```
4. **Create feature branch** and implement
5. **Move to done** after merge:
   ```bash
   mv _meta/issues/wip/300-*.md _meta/issues/done/
   ```

### For Team Leads

1. **Review worker folders** for skill-appropriate assignments
2. **Assign issues** based on team member expertise
3. **Track progress** by monitoring WIP folder
4. **Coordinate** integration of completed issues

---

## Issue Numbering

### Current Ranges

- **#100-#199**: Reserved for Web Client issues (Phase 0 - Complete ✅)
- **#200-#299**: Infrastructure & DevOps issues
- **#300-#399**: Source module enhancements and fixes
- **#400-#499**: Reserved for future categories
- **#500-#599**: Database and ORM patterns (in backlog)

---

## Issue Lifecycle

```
new/ → wip/ → done/
 ↓      ↓       ↓
Read  Work   Archive
```

1. **new/**: Issues awaiting assignment (you are here)
2. **wip/**: Issues being actively worked on
3. **done/**: Completed and merged issues

---

## Priority Levels

### Worker-Based Issues (High Priority)

All worker issues are **HIGH priority** and ready to start:

- ⭐⭐⭐ **#300**: HIGH - Completes YouTube Shorts feature set
- ⭐⭐ **#301**: MEDIUM - Important documentation
- ⭐⭐ **#302**: MEDIUM - Improves user experience
- ⭐⭐⭐ **#303**: HIGH - Ensures system reliability

### Infrastructure Issues (Medium Priority)

See [Infrastructure_DevOps/README.md](./Infrastructure_DevOps/README.md) for priorities.

---

## Success Criteria

### Phase 0 (Complete ✅)
- [x] All Web Client issues (#101-#112) complete
- [x] All 38 sources implemented

### Current Focus (Worker Issues #300-303)
- [ ] Keyword search implementation complete (#300)
- [ ] Module flow documented (#301)
- [ ] Parameter validation improved (#302)
- [ ] Windows subprocess testing comprehensive (#303)

### Next Phase
- [ ] Infrastructure improvements (#200-#207)
- [ ] Database integration (backlog)
- [ ] Pipeline integration (backlog)

---

## Related Documentation

- **Worker Organization**: [README-WORKER-ORGANIZATION.md](./README-WORKER-ORGANIZATION.md)
- **Next Steps**: `_meta/issues/NEXT_STEPS.md`
- **Worker Allocation Matrix**: `_meta/issues/WORKER_ALLOCATION_MATRIX.md`
- **Roadmap**: `_meta/issues/ROADMAP.md`
- **Issue Tracking**: `_meta/issues/README.md`

---

## Quick Stats

**Total Issues in new/**: 12+  
**Worker Issues (Ready)**: 4 (#300-#303)  
**Infrastructure Issues**: 8 (#200-#207)  
**Can Start Immediately**: 4 (all worker issues)  
**Estimated Completion**: 1-2 weeks (with 4 parallel workers)

---

## Contact

- **Issue Questions**: See individual issue files for details
- **Assignment Questions**: Contact project manager
- **Process Questions**: See `_meta/issues/README.md`

---

**Status**: ⚠️ Worker10 Review Complete - Awaiting Worker01 Decision  
**Last Updated**: 2025-11-13  
**Next Review**: After Worker01 decision on quality gaps
