# Issue Tracking Index

**Created**: 2025-10-31  
**Updated**: 2025-11-17 (Documentation cleanup and SOLID restructure)
**Purpose**: Master index for issue tracking and workflow

> **Important**: For current development status and overall plan, see [DEVELOPMENT_PLAN.md](../../DEVELOPMENT_PLAN.md)

> **Note**: The Client/Backend module for web-based control panel (Phase 0) has been completed and moved to a separate repository.
> See [_meta/docs/archive/phase-0/](../_meta/docs/archive/phase-0/) for historical context.

---

## 🎯 Quick Navigation

### "I want to understand the overall project status"
👉 **[DEVELOPMENT_PLAN.md](../../DEVELOPMENT_PLAN.md)** (Unified development plan)
- Current phase and progress
- Team structure and roles
- Completed and planned work
- Success criteria and metrics

---

### "I want to know what to work on next"
👉 **[ROADMAP.md](ROADMAP.md)** + **[Issue Folders](#issue-folders)**
- Check `new/` folders for available issues
- Review issue assignment by Worker/Developer
- Start with highest priority issues

---

### "I need detailed planning documents"
👉 **Legacy Planning Documents** (See below)
- Historical planning documents preserved for reference
- Current planning is in DEVELOPMENT_PLAN.md
- Phase-specific archives in `_meta/docs/archive/`

---

## 📂 Issue Folders

### Directory Structure

```
_meta/issues/
├── new/          # New issues ready to start
│   ├── Worker01-10/       # Issues by worker role
│   ├── Infrastructure_DevOps/  # Infrastructure issues
│   ├── Reddit/            # Reddit-specific issues
│   └── planning docs      # Active planning documents
├── ready/        # Fully specified, ready to implement
├── wip/          # Work in progress
├── review/       # Code complete, awaiting review
├── blocked/      # Cannot proceed (dependencies/clarification)
├── done/         # Completed issues
├── archive/      # Archived planning and historical docs
└── templates/    # Issue templates
```

### Issue Workflow

1. **New**: Issue created in `new/{Worker}/`, ready to start
2. **WIP**: Moved to `wip/` when work begins
3. **Done**: Moved to `done/` when complete, tested, documented

### Current Status

See [DEVELOPMENT_PLAN.md](../../DEVELOPMENT_PLAN.md) for:
- Current phase status
- Available issues
- Team assignments
- Progress tracking

---

## 🎓 Legacy Planning Documents

The following comprehensive planning documents were created for Phase 0 (Web Client).
They are preserved for reference but have been superseded by [DEVELOPMENT_PLAN.md](../../DEVELOPMENT_PLAN.md).

### Phase 0 Planning (Archived)
- **QUICK_START.md** - One-page action guide
- **NEXT_STEPS.md** - Comprehensive implementation plan
- **IMPLEMENTATION_TIMELINE.md** - Visual timeline and diagrams
- **WORKER_ALLOCATION_MATRIX.md** - Parallel work assignments
- **PROGRESS_CHECKLIST.md** - Progress tracking

**Status**: Phase 0 complete. Documents preserved for historical reference.
**Archive**: See `_meta/docs/archive/phase-0/` for completion reports.

### Current Planning
All current planning is now consolidated in:
- **[DEVELOPMENT_PLAN.md](../../DEVELOPMENT_PLAN.md)** - Unified plan covering all phases
- **[ROADMAP.md](ROADMAP.md)** - Long-term vision
- **[Source Module Planning](../../Source/_meta/issues/new/INDEX.md)** - Source module details

---

## 🎯 Current Status (2025-11-13)

### Overall Progress
- **Phase 0**: ✅ 100% Complete (Web Client Control Panel)
- **Phase 1**: ✅ 100% Complete (Foundation & Integration)
- **Phase 2**: 🔄 20% Complete (Source Module Implementations)
- **Phase 3**: 📅 Planned (Analytics & Performance)

### Active Work (Phase 2)
- **Batch 1**: ✅ Complete (Infrastructure)
- **Batch 2**: 🔄 Ready to Start (6 parallel issues)
  - Video module implementations (3 issues)
  - Text module implementations (3 issues)

### Next Actions
1. Start Phase 2 Batch 2 implementations
2. Assign issues from `new/` folders
3. Track progress via `wip/` and `done/` folders

For detailed status, see [DEVELOPMENT_PLAN.md](../../DEVELOPMENT_PLAN.md)

---

## 🔗 Quick Links

### Primary Documentation
- **[DEVELOPMENT_PLAN.md](../../DEVELOPMENT_PLAN.md)** - Start here for complete overview
- **[ROADMAP.md](ROADMAP.md)** - Long-term vision and phases
- **[KNOWN_ISSUES.md](KNOWN_ISSUES.md)** - Current limitations and bugs

### Issue Management
- **New Issues**: `_meta/issues/new/` (Ready to start)
- **WIP Issues**: `_meta/issues/wip/` (Currently being worked on)
- **Done Issues**: `_meta/issues/done/` (Completed work)

### Source Module Issues
- **[Source Module Index](../../Source/_meta/issues/new/INDEX.md)** - Developer team and planning
- **Source New**: `Source/_meta/issues/new/` (Module-specific issues)
- **Source Done**: `Source/_meta/issues/done/` (Completed module work)

### Archives
- **[Archive Index](../_meta/docs/archive/)** - Historical documentation
- **[Phase 0 Archive](../_meta/docs/archive/phase-0/)** - Web Client completion
- **[Phase 1 Archive](../_meta/docs/archive/phase-1/)** - Foundation completion

---

## 📞 For More Information

### By Role
- **Contributors**: See [DEVELOPMENT_PLAN.md](../../DEVELOPMENT_PLAN.md) → "For New Contributors"
- **Team Leads**: See [DEVELOPMENT_PLAN.md](../../DEVELOPMENT_PLAN.md) → "For Team Leads"
- **Project Managers**: See [DEVELOPMENT_PLAN.md](../../DEVELOPMENT_PLAN.md) → "For Project Managers"

### By Need
- **Current Status**: [DEVELOPMENT_PLAN.md](../../DEVELOPMENT_PLAN.md) → "Progress Tracking"
- **What to Work On**: Check `_meta/issues/new/` or `Source/_meta/issues/new/`
- **Historical Context**: See `_meta/docs/archive/`

---

**Last Updated**: 2025-11-13  
**Next Review**: After Phase 2 Batch 2 completion  
**Status**: Active - Phase 2 in progress
