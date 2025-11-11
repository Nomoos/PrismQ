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
| **Parallel work assignments** | [WORKER_ALLOCATION_MATRIX.md](WORKER_ALLOCATION_MATRIX.md) | Team coordination |
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
  - **Infrastructure_DevOps/** - Development tooling and infrastructure (#200+)
- **backlog/** - Backlog items not currently planned for active work
- **wip/** - Issues currently being worked on (Work In Progress)
- **done/** - Recently completed issues, organized by year
  - **2024/** - Issues completed in 2024
  - **2025/** - Recent issues completed in 2025
  - *Note: Old completed issues are removed from the repository but remain accessible in git history*
- **templates/** - Issue templates for creating new issues
  - **feature_issue.md** - Template for feature requests
  - **bug_issue.md** - Template for bug reports
  - **infrastructure_issue.md** - Template for infrastructure/DevOps issues

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
- **WORKER_ALLOCATION_MATRIX.md** - At-a-glance parallel work assignments
- **PROGRESS_CHECKLIST.md** - Track your implementation progress

## Issue Workflow

### Creating New Issues

1. **Choose a Template** - Start with one of the templates in `templates/`:
   - `feature_issue.md` for new features
   - `bug_issue.md` for bug reports
   - `infrastructure_issue.md` for infrastructure/DevOps work

2. **Create New Issue** - Copy the appropriate template to the relevant EPIC folder within `new/` directory:
   - For Web Client issues → `new/Phase_0_Web_Client_Control_Panel/`
   - For Infrastructure/DevOps → `new/Infrastructure_DevOps/`
   - For other phases → corresponding Phase folder

3. **File Naming** - Use format: `NNN-descriptive-name.md` (e.g., `204-clean-up-issues-directory.md`)

### Issue Lifecycle

1. **New Issues** - Issues start in `new/` organized by category/phase
2. **Backlog** - Move to `backlog/` for items that are not currently planned but may be worked on later
3. **Work In Progress** - Move to `wip/` when work begins on an issue
4. **Completed** - Move to `done/YYYY/` (year subdirectory) when finished
   - Use `done/2025/` for current year
   - Group related issues in subdirectories as needed if there are many related issues
   - Remove old issues periodically (they remain in git history for reference)

### Archiving

- **Summary Documents** - Move to `_meta/docs/archive/summaries/`
- **Planning Documents** - Move to `_meta/docs/archive/planning/`
- **Old Completed Issues** - Remove from repository (accessible in git history for reference)
  - Keep only recent completed issues in `done/YYYY/`
  - Old issues can be referenced using git history: `git show <commit>:path/to/file.md`

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
- `NNN-feature-name.md` (e.g., `204-clean-up-issues-directory.md`)
- `NNN-bug-description.md`
- `NNN-enhancement-name.md`

Where NNN is the issue number (can be sequential or use GitHub issue numbers).

## Issue Templates

Issue templates are available in the `templates/` directory:

### Feature Issue Template (`templates/feature_issue.md`)
Use for new features, enhancements, or capabilities to add to the project.

### Bug Issue Template (`templates/bug_issue.md`)
Use for bug reports with reproduction steps and expected vs actual behavior.

### Infrastructure Issue Template (`templates/infrastructure_issue.md`)
Use for DevOps, tooling, build system, CI/CD, and infrastructure improvements.

### Template Fields

Each template includes:
- **Title** - Clear, descriptive title
- **Status** - New, WIP, Done, Blocked
- **Priority** - Critical, High, Medium, Low
- **Category** - Feature, Bug, Infrastructure_DevOps, etc.
- **Description** - Detailed description of the issue
- **Acceptance Criteria** - Checklist of requirements
- **Estimated Effort** - Time estimate
- **Dependencies** - Related issues or requirements
- **Target Platform** - Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

## Integration

GitHub Issues can also be used for tracking. This directory provides an alternative or supplementary tracking system.
