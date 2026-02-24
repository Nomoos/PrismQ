# Quick Reference - Project Organization

**Purpose**: Quick reference for navigating the PrismQ.T.Idea.Inspiration project  
**Last Updated**: 2025-11-13

---

## 🚀 Start Here

### New to the Project?
1. Read [README.md](../../README.md) - Project overview
2. Read [DEVELOPMENT_PLAN.md](../docs/development/DEVELOPMENT_PLAN.md) - Current status and plan
3. Check available issues in `_meta/issues/new/` or `Source/_meta/issues/new/`

### Looking for Current Status?
👉 **[DEVELOPMENT_PLAN.md](../docs/development/DEVELOPMENT_PLAN.md)**

### Want to Start Working?
1. Check `_meta/issues/new/WorkerXX/` or `Source/_meta/issues/new/DeveloperXX/`
2. Pick an issue matching your skills
3. Read [ISSUE_MANAGEMENT.md](ISSUE_MANAGEMENT.md) for workflow
4. Move issue to `wip/` when starting

---

## 📂 Key Directories

```
PrismQ.T.Idea.Inspiration/
├── README.md                    # Project overview (START HERE)
├── DEVELOPMENT_PLAN.md          # Current development plan ⭐
│
├── Classification/              # Content classification module
├── EnvLoad/                  # Configuration management
├── Model/                       # Core data model (IdeaInspiration)
├── Scoring/                     # Content scoring module
├── Source/                      # Source modules (Video, Text, Audio, etc.)
│   └── _meta/issues/           # Module-specific issues (Developers)
│
└── _meta/                       # Repository metadata
    ├── docs/                    # Documentation
    │   ├── ARCHITECTURE.md      # System architecture
    │   ├── ISSUE_MANAGEMENT.md  # Issue workflow guide
    │   ├── QUICK_REFERENCE.md   # This file
    │   └── archive/             # Historical documentation
    │       ├── phase-0/         # Web Client (complete)
    │       └── phase-1/         # Foundation (complete)
    │
    └── issues/                  # Repository-level issues (Workers)
        ├── ROADMAP.md           # Long-term roadmap
        ├── INDEX.md             # Issue tracking index
        ├── new/                 # Ready to start
        ├── wip/                 # In progress
        └── done/                # Completed
```

---

## 👥 Team Structure

### Repository Team (Workers 01-10)
**Focus**: Infrastructure, cross-cutting concerns

| Worker | Role | Folder |
|--------|------|--------|
| Worker01 | Planning | `_meta/issues/new/Worker01/` |
| Worker02 | Infrastructure | `_meta/issues/new/Worker02/` |
| Worker03 | CLI & Integration | `_meta/issues/new/Worker03/` |
| Worker04 | Testing | `_meta/issues/new/Worker04/` |
| Worker05 | DevOps | `_meta/issues/new/Worker05/` |
| Worker06 | Database | `_meta/issues/new/Worker06/` |
| Worker07 | Security | `_meta/issues/new/Worker07/` |
| Worker08 | Data Integration | `_meta/issues/new/Worker08/` |
| Worker09 | Documentation | `_meta/issues/new/Worker09/` |
| Worker10 | Code Review | `_meta/issues/new/Worker10/` |

### Source Module Team (Developers 01-10)
**Focus**: Source module implementations

| Developer | Role | Folder |
|-----------|------|--------|
| Developer01 | SCRUM Master | `Source/_meta/issues/new/Developer01/` |
| Developer02 | Backend | `Source/_meta/issues/new/Developer02/` |
| Developer03 | Full-Stack | `Source/_meta/issues/new/Developer03/` |
| Developer04 | QA/Testing | `Source/_meta/issues/new/Developer04/` |
| Developer05 | DevOps | `Source/_meta/issues/new/Developer05/` |
| Developer06 | Database | `Source/_meta/issues/new/Developer06/` |
| Developer07 | Security | `Source/_meta/issues/new/Developer07/` |
| Developer08 | Data Integration | `Source/_meta/issues/new/Developer08/` |
| Developer09 | Documentation | `Source/_meta/issues/new/Developer09/` |
| Developer10 | Code Review | `Source/_meta/issues/new/Developer10/` |

---

## 📊 Current Status (Phase 2)

### Completed ✅
- **Phase 0**: Web Client Control Panel (moved to separate repo)
- **Phase 1**: Foundation & Integration
  - TaskManager Python Client
  - Video Module Infrastructure (BaseVideoWorker)
  - Text Module Infrastructure (BaseTextWorker)

### Active 🔄
- **Phase 2 Batch 2**: Core Module Implementations
  - 6 issues ready to start (3 Video, 3 Text)
  - All can run in parallel

### Planned 📅
- **Phase 2 Batch 3**: Audio & Other modules
- **Phase 2 Batch 4**: Polish & testing
- **Phase 3**: Analytics & Performance

---

## 🎯 Quick Commands

### Find Available Issues
```bash
# Repository level
ls _meta/issues/new/Worker*/

# Module level
ls Source/_meta/issues/new/Developer*/
```

### Check Current Work
```bash
# What's in progress?
ls _meta/issues/wip/
ls Source/_meta/issues/wip/
```

### See Completed Work
```bash
# Repository level
ls _meta/issues/done/Worker*/

# Module level
ls Source/_meta/issues/done/Developer*/
```

### Issue Status Report
```bash
echo "Repository Issues:"
echo "  New: $(find _meta/issues/new -name "*.md" -type f | wc -l)"
echo "  WIP: $(ls _meta/issues/wip/*.md 2>/dev/null | wc -l)"
echo "  Done: $(find _meta/issues/done -name "*.md" -type f | wc -l)"

echo "Module Issues:"
echo "  New: $(find Source/_meta/issues/new -name "*.md" -type f | wc -l)"
echo "  WIP: $(ls Source/_meta/issues/wip/*.md 2>/dev/null | wc -l)"
echo "  Done: $(find Source/_meta/issues/done -name "*.md" -type f | wc -l)"
```

---

## 📚 Essential Documentation

### Planning & Status
- **[DEVELOPMENT_PLAN.md](../docs/development/DEVELOPMENT_PLAN.md)** ⭐ START HERE
- **[ROADMAP.md](../issues/ROADMAP.md)** - Long-term vision
- **[INDEX.md](../issues/INDEX.md)** - Issue tracking

### Development Guides
- **[ISSUE_MANAGEMENT.md](ISSUE_MANAGEMENT.md)** - Issue workflow
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute
- **[PYTHON_PACKAGING_STANDARD.md](PYTHON_PACKAGING_STANDARD.md)** - Package standards

### Module-Specific
- **[Source Module Index](../../Source/_meta/issues/new/INDEX.md)** - Module planning
- **[TaskManager Guide](../../Source/TaskManager/_meta/docs/WORKER_IMPLEMENTATION_GUIDE.md)** - Worker patterns

### Historical
- **[Archive](archive/)** - Completed phases
  - [Phase 0 Archive](archive/phase-0/) - Web Client
  - [Phase 1 Archive](archive/phase-1/) - Foundation

---

## 🔗 External Links

- **Repository**: https://github.com/Nomoos/PrismQ.T.Idea.Inspiration
- **Related Projects**:
  - [PrismQ.IdeaCollector](https://github.com/Nomoos/PrismQ.IdeaCollector)
  - [StoryGenerator](https://github.com/Nomoos/StoryGenerator)
  - [PrismQ.RepositoryTemplate](https://github.com/Nomoos/PrismQ.RepositoryTemplate)

---

## ❓ Common Questions

### Where do I find issues to work on?
- Repository level: `_meta/issues/new/WorkerXX/`
- Module level: `Source/_meta/issues/new/DeveloperXX/`

### What's the difference between Worker and Developer?
- **Workers**: Repository-level infrastructure
- **Developers**: Source module implementations

### How do I start working on an issue?
1. Find issue in `new/` folder
2. Read thoroughly
3. Move to `wip/` folder
4. Update status in issue file
5. Start implementation

### Where do I put completed work?
- Move from `wip/` to `done/WorkerXX/` or `done/DeveloperXX/`
- Update issue status to "Complete"
- Add completion summary

### What's the current phase?
Phase 2 - Source Module Implementations (Batch 2 starting)

### Where's the overall plan?
**[DEVELOPMENT_PLAN.md](../docs/development/DEVELOPMENT_PLAN.md)** - The single source of truth

---

## 🆘 Need Help?

1. **Documentation not clear?** → Ask Worker09 or Developer09
2. **Architecture questions?** → Ask Worker10 or Developer10  
3. **Can't find something?** → Check [INDEX.md](../issues/INDEX.md)
4. **General questions?** → Check [DEVELOPMENT_PLAN.md](../docs/development/DEVELOPMENT_PLAN.md)

---

## 📝 Document Navigation

```
You are here: _meta/docs/QUICK_REFERENCE.md

Related:
├── DEVELOPMENT_PLAN.md (../../)     ← Overall plan
├── ISSUE_MANAGEMENT.md (.//)        ← Issue workflow
├── ARCHITECTURE.md (.//)            ← System design
└── archive/ (.//)                   ← Historical docs
```

---

**Maintained By**: Worker01 & Worker09  
**Last Updated**: 2025-11-13  
**Purpose**: Quick navigation and reference
