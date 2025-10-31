# Issues

This directory contains issue tracking and project management files.

## 🎯 **START HERE: [INDEX.md](INDEX.md)** ⭐

The [INDEX.md](INDEX.md) document is your master guide. It will direct you to the right document based on your needs.

---

## 🚀 Quick Navigation

**Not sure where to start? Pick based on your need:**

| I need... | Go to... | Description |
|-----------|----------|-------------|
| **Quick answer - what to do now?** | [QUICK_START.md](QUICK_START.md) | 1-page action guide |
| **Complete understanding** | [NEXT_STEPS.md](NEXT_STEPS.md) | Comprehensive 627-line plan |
| **Visual timeline** | [IMPLEMENTATION_TIMELINE.md](IMPLEMENTATION_TIMELINE.md) | Diagrams and charts |
| **Parallel work assignments** | [PARALLELIZATION_MATRIX.md](PARALLELIZATION_MATRIX.md) | Team coordination |
| **Track progress** | [PROGRESS_CHECKLIST.md](PROGRESS_CHECKLIST.md) | Daily/weekly tracking |
| **Master overview** | [INDEX.md](INDEX.md) | Complete documentation index |

## Structure

### Directories
- **new/** - New issues and feature requests, organized by EPIC/Phase
  - **Phase_0_Web_Client_Control_Panel/** - Web client issues (#101-#112)
  - **Phase_1_Foundation_Integration/** - Pipeline and database issues
  - **Phase_2_Performance_Scale/** - Performance optimization issues
  - **Phase_3_Analytics_Insights/** - Analytics and reporting issues
  - **Phase_4_Advanced_Features/** - Advanced feature issues
  - **Infrastructure_DevOps/** - Development tooling and infrastructure (#113-#118)
- **backlog/** - Backlog items not currently planned for active work
- **wip/** - Issues currently being worked on (Work In Progress)
- **done/** - Completed issues and features

Each EPIC folder in `new/` contains:
- A `README.md` describing the phase objectives and success criteria
- Individual issue files for that phase
- `.gitkeep` to maintain the directory in version control

### Planning Documents
- **ROADMAP.md** - Project roadmap and future plans (all phases)
- **KNOWN_ISSUES.md** - List of known issues and bugs
- **NEXT_STEPS.md** - Detailed implementation guide with parallelization strategy
- **QUICK_START.md** - Quick reference for what to do next ⭐
- **IMPLEMENTATION_TIMELINE.md** - Visual timeline, dependency graphs, and resource allocation
- **PARALLELIZATION_MATRIX.md** - At-a-glance parallel work assignments
- **PROGRESS_CHECKLIST.md** - Track your implementation progress

### Review Documents
- **ISSUE_REVIEW_2025-10-30.md** - Review of all issues (no duplicates found)
- **WIP_STATUS_REVIEW_2025-10-30.md** - Review of WIP directory status

## Issue Workflow

1. **New Issues** - Create a new file in the appropriate EPIC folder within `new/` directory
   - For Web Client issues → `new/Phase_0_Web_Client_Control_Panel/`
   - For Infrastructure/DevOps → `new/Infrastructure_DevOps/`
   - For other phases → corresponding Phase folder
2. **Backlog** - Move to `backlog/` for items that are not currently planned but may be worked on later
3. **Work In Progress** - Move to `wip/` when work begins
4. **Completed** - Move to `done/` when finished

### EPIC Organization

Issues are organized into EPICs based on the project roadmap:
- **Phase 0**: Web Client Control Panel (Q1 2025) - Issues #101-#112
- **Phase 1**: Foundation & Integration (Q2 2025) - Issues #001, #002, #005
- **Phase 2**: Performance & Scale (Q3 2025) - Issues #003, #006, #009
- **Phase 3**: Analytics & Insights (Q4 2025) - Issues #004, #007
- **Phase 4**: Advanced Features (2026) - Issues #008, #010
- **Infrastructure**: Development tooling - Issues #113-#118 (Virtual Environment Management)

## File Naming

Use descriptive names for issue files:
- `001-feature-name.md`
- `002-bug-description.md`
- `003-enhancement-name.md`

## Template

Each issue file should include:
- **Title** - Clear, descriptive title
- **Description** - Detailed description of the issue
- **Type** - Bug, Feature, Enhancement, etc.
- **Priority** - High, Medium, Low
- **Status** - New, In Progress, Done
- **Assignee** - Who is working on it
- **Target Platform** - Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

## Integration

GitHub Issues can also be used for tracking. This directory provides an alternative or supplementary tracking system.
