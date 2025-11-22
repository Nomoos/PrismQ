# Issue Management Guide

**Purpose**: Guide for managing issues across the PrismQ.T.Idea.Inspiration repository  
**Last Updated**: 2025-11-13  
**Version**: 1.0

---

## 📋 Overview

This repository uses a structured issue management system with two parallel tracks:
1. **Repository-level issues** (`_meta/issues/`) - Infrastructure, coordination, cross-cutting concerns
2. **Source module issues** (`Source/_meta/issues/`) - Module-specific implementations

---

## 🗂️ Directory Structure

### Repository Level (_meta/issues/)

```
_meta/issues/
├── new/                    # New issues awaiting triage/clarification
│   ├── Worker01/          # Planning & coordination
│   ├── Worker02/          # Infrastructure
│   ├── Worker03/          # CLI & integration
│   ├── Worker04/          # Testing
│   ├── Worker05/          # DevOps
│   ├── Worker06/          # Database
│   ├── Worker07/          # Security
│   ├── Worker08/          # Data integration
│   ├── Worker09/          # Documentation
│   ├── Worker10/          # Code review
│   └── [planning docs]    # Cross-cutting planning
├── ready/                 # Fully specified, ready to implement now
├── wip/                   # Work in progress (active development)
├── review/                # Code complete, awaiting review
├── blocked/               # Cannot proceed (dependencies, clarification needed)
├── done/                  # Completed issues
│   ├── Worker09/         # Completed work by worker
│   └── investigations/   # Completed investigations
└── templates/            # Issue templates
```

### Source Module Level (Source/_meta/issues/)

```
Source/_meta/issues/
├── new/                    # New module issues awaiting triage
│   ├── Developer01/       # SCRUM master & planning
│   ├── Developer02/       # Backend development
│   ├── Developer03/       # Full-stack development
│   ├── Developer04/       # QA/Testing
│   ├── Developer05/       # DevOps
│   ├── Developer06/       # Database
│   ├── Developer07/       # Security
│   ├── Developer08/       # Data integration
│   ├── Developer09/       # Documentation
│   ├── Developer10/       # Code review
│   └── [planning docs]    # Module planning
├── ready/                 # Fully specified, ready to implement now
├── wip/                   # Work in progress (active development)
├── review/                # Code complete, awaiting review
├── blocked/               # Cannot proceed (dependencies, clarification needed)
├── done/                  # Completed module issues
│   ├── Developer01/      # Completed work by developer
│   ├── Developer09/
│   └── Developer10/
└── obsolete/             # Archived obsolete plans
```

---

## 👥 Team Structure

### Repository Team (Workers 01-10)
Focus: Repository-level infrastructure and cross-cutting concerns

| Worker | Role | Issues Prefix |
|--------|------|---------------|
| Worker01 | Planning & Coordination | W01-xxx |
| Worker02 | Infrastructure | W02-xxx |
| Worker03 | CLI & Integration | W03-xxx |
| Worker04 | Testing | W04-xxx |
| Worker05 | DevOps | W05-xxx |
| Worker06 | Database | W06-xxx |
| Worker07 | Security | W07-xxx |
| Worker08 | Data Integration | W08-xxx |
| Worker09 | Documentation | W09-xxx |
| Worker10 | Code Review | W10-xxx |

### Source Module Team (Developers 01-10)
Focus: Source module implementations

| Developer | Role | Issues Prefix |
|-----------|------|---------------|
| Developer01 | SCRUM Master | D01-xxx |
| Developer02 | Backend | D02-xxx |
| Developer03 | Full-Stack | D03-xxx |
| Developer04 | QA/Testing | D04-xxx |
| Developer05 | DevOps | D05-xxx |
| Developer06 | Database | D06-xxx |
| Developer07 | Security | D07-xxx |
| Developer08 | Data Integration | D08-xxx |
| Developer09 | Documentation | D09-xxx |
| Developer10 | Code Review | D10-xxx |

---

## 📝 Issue Workflow

### Standard Workflow States

Issues progress through the following states:

```
new → ready → wip → review → done
  ↓                    ↓
blocked ←──────────────┘
  ↓
ready (when unblocked)
```

**State Definitions**:
- **new**: Issues awaiting triage, clarification, or specification
- **ready**: Fully specified issues ready to implement now (all dependencies resolved)
- **wip**: Active development in progress
- **review**: Code complete, awaiting peer review
- **blocked**: Cannot proceed due to dependencies or missing information
- **done**: Complete, tested, reviewed, and merged

---

### 1. Issue Creation (→ New)

**Location**: Place in appropriate `new/` folder
- Repository-level: `_meta/issues/new/WorkerXX/`
- Module-level: `Source/_meta/issues/new/DeveloperXX/`

**Naming Convention**:
```
[ID]-[short-description].md
Examples:
- 001-taskmanager-api-foundation.md
- 002-reddit-posts-integration.md
```

**Required Sections**:
```markdown
# [Title]

**Issue ID**: [WXX-NNN or DXX-NNN]
**Assignee**: [WorkerXX or DeveloperXX]
**Priority**: [High/Medium/Low]
**Status**: New
**Estimated Duration**: [X days/weeks]

## Overview
Brief description of the issue

## Objectives
- Clear, measurable goals

## Acceptance Criteria
- [ ] Specific, testable criteria

## Dependencies
- List any blocking issues

## Implementation Steps
1. Detailed steps

## Testing Requirements
- Unit tests
- Integration tests
- Performance tests

## Documentation Requirements
- What needs to be documented

## Success Metrics
- How to measure success
```

### 2. Triage and Specification (New → Ready)

**When to move**:
- All requirements clarified
- Dependencies identified and resolved
- Acceptance criteria defined
- Ready to be picked up by any team member

**How to move**:
```bash
# Repository level
mv _meta/issues/new/Worker01/001-issue.md _meta/issues/ready/

# Module level
mv Source/_meta/issues/new/Developer02/001-issue.md Source/_meta/issues/ready/
```

**Update issue**:
- Change `**Status**: New` to `**Status**: Ready`
- Add `**Ready Date**: YYYY-MM-DD`
- Ensure all dependencies are listed and clear

**Purpose**: The `ready/` folder contains issues that can be implemented immediately. Team members can browse this folder to find work that is fully specified and unblocked.

### 3. Starting Work (Ready → WIP)

**When to move**:
- When actively starting implementation
- Developer has committed time to complete it
- Issue picked from ready/ folder

**How to move**:
```bash
# Repository level
mv _meta/issues/ready/001-issue.md _meta/issues/wip/

# Module level
mv Source/_meta/issues/ready/001-issue.md Source/_meta/issues/wip/
```

**Update issue**:
- Change `**Status**: Ready` to `**Status**: In Progress`
- Add `**Started**: YYYY-MM-DD`
- Add `**Assignee**: [Worker/Developer name]` if not already set
- Add progress notes as work proceeds

### 4. Code Review (WIP → Review)

**When to move**:
- Implementation complete
- All tests passing locally
- Code ready for peer review
- Documentation drafted

**How to move**:
```bash
# Repository level
mv _meta/issues/wip/001-issue.md _meta/issues/review/

# Module level
mv Source/_meta/issues/wip/001-issue.md Source/_meta/issues/review/
```

**Update issue**:
- Change `**Status**: In Progress` to `**Status**: In Review`
- Add `**Review Requested**: YYYY-MM-DD`
- Add `**Reviewer**: [Worker10 or Developer10]`
- Link to PR or commit

**Note**: For small changes, you may skip `review/` and go directly from `wip/` to `done/` after self-review.

### 5. Completing Work (Review → Done)

**When to move**:
- Code reviewed and approved
- All tests passing in CI
- Documentation updated
- Changes merged

**How to move**:
```bash
# Repository level
mv _meta/issues/review/001-issue.md _meta/issues/done/Worker01/

# Module level
mv Source/_meta/issues/review/001-issue.md Source/_meta/issues/done/Developer02/
```

**Update issue**:
- Change `**Status**: In Review` to `**Status**: Complete`
- Add `**Completed**: YYYY-MM-DD`
- Add `**Review Approved By**: [Reviewer name]`
- Add completion summary
- Link to merged PR/commit
- Add `**Started**: YYYY-MM-DD`
- Add progress notes

### 3. Completing Work (WIP → Done)

**When to move**:
- Implementation complete
- All tests passing
- Code reviewed and approved
- Documentation updated

**How to move**:
```bash
# Repository level
mv _meta/issues/wip/001-issue.md _meta/issues/done/Worker01/

# Module level
mv Source/_meta/issues/wip/001-issue.md Source/_meta/issues/done/Developer02/
```

**Update issue**:
- Change `**Status**: In Progress` to `**Status**: Complete`
- Add `**Completed**: YYYY-MM-DD`
- Add completion summary
- Link to PR/commit

**Create completion summary** (optional for major issues):
```markdown
# [Issue ID] - Completion Summary

**Completed**: YYYY-MM-DD
**Duration**: X days/weeks

## What Was Delivered
- Deliverable 1
- Deliverable 2

## Files Changed
- List of key files

## Tests Added
- Test coverage details

## Documentation Updated
- Documentation changes

## Lessons Learned
- What went well
- What could improve

## Next Steps
- Related work
- Future enhancements
```

### 6. Handling Blocked Issues (Any State → Blocked)

**When to move**:
- Missing required information or clarification
- Waiting on external dependency
- Blocked by another issue
- Technical blocker requiring investigation

**How to move**:
```bash
# From any state (new, ready, wip, review)
# Repository level
mv _meta/issues/[current-state]/001-issue.md _meta/issues/blocked/

# Module level
mv Source/_meta/issues/[current-state]/001-issue.md Source/_meta/issues/blocked/
```

**Update issue**:
- Change `**Status**: [current]` to `**Status**: Blocked`
- Add `**Blocked Date**: YYYY-MM-DD`
- Add `**Blocked Reason**: [Detailed explanation]`
- Add `**Blocking Issue**: [Issue ID if applicable]`
- Add `**Action Needed**: [What's needed to unblock]`

**Unblocking (Blocked → Ready)**:

Once the blocker is resolved:
```bash
# Repository level
mv _meta/issues/blocked/001-issue.md _meta/issues/ready/

# Module level
mv Source/_meta/issues/blocked/001-issue.md Source/_meta/issues/ready/
```

**Update issue**:
- Change `**Status**: Blocked` to `**Status**: Ready`
- Add `**Unblocked Date**: YYYY-MM-DD`
- Add `**Resolution**: [How blocker was resolved]`
- Remove or update blocking reason

**Purpose**: The `blocked/` folder keeps the active workflow (ready/wip/review) clean and focused on actionable work. Team members can periodically review blocked issues to help resolve blockers.

### 7. Obsolete Issues

**When to obsolete**:
- Requirements changed
- Superseded by different approach
- No longer relevant

**How to handle**:
```bash
# Move to obsolete folder (Source module only)
mv Source/_meta/issues/new/Developer01/001-issue.md Source/_meta/issues/obsolete/Developer01/

# Repository level: Delete or move to done with "Obsolete" note
```

**Mark clearly**:
```markdown
**Status**: ⚠️ OBSOLETE - [Reason]
**Replaced By**: [New issue or approach]
```

---

## 🏷️ Issue Categories

### Repository Level

**Infrastructure (Worker02)**
- Core system components
- Shared utilities
- Build and deployment tools

**Database (Worker06)**
- Schema design
- Migrations
- Query optimization

**Testing (Worker04)**
- Test frameworks
- CI/CD pipelines
- Quality assurance

**Documentation (Worker09)**
- API documentation
- User guides
- Architecture docs

**DevOps (Worker05)**
- Deployment
- Monitoring
- Performance

**Security (Worker07)**
- Security audits
- Authentication
- Authorization

### Module Level

**Module Implementation (Developer02, 03, 08)**
- Source integrations
- Workers
- Data transformation

**Module Testing (Developer04)**
- Unit tests
- Integration tests
- Performance tests

**Module Documentation (Developer09)**
- Module README
- API docs
- Usage guides

**Code Review (Developer10)**
- Architecture review
- SOLID validation
- Quality gates

---

## 📊 Issue Tracking

### Progress Tracking

Use checklist format in issue files:
```markdown
## Progress
- [x] Phase 1: Planning
- [x] Phase 2: Implementation
- [ ] Phase 3: Testing
- [ ] Phase 4: Documentation
```

### Status Updates

Update issues regularly:
```markdown
## Status Updates

### 2025-11-13
- Completed initial implementation
- Tests passing
- Ready for review

### 2025-11-12
- Started implementation
- Created basic structure
```

### Linking Issues

Reference related issues:
```markdown
## Related Issues
- Blocks: #D02-003
- Depends on: #D01-001
- Related to: #W06-008
```

---

## 🔍 Finding Issues

### By Status
```bash
# Find all new issues (awaiting triage)
find _meta/issues/new -name "*.md" -type f
find Source/_meta/issues/new -name "*.md" -type f

# Find all ready issues (ready to implement now)
ls _meta/issues/ready/*.md 2>/dev/null || echo "No ready issues"
ls Source/_meta/issues/ready/*.md 2>/dev/null || echo "No ready issues"

# Find all WIP issues (in progress)
ls _meta/issues/wip/*.md 2>/dev/null || echo "No WIP issues"
ls Source/_meta/issues/wip/*.md 2>/dev/null || echo "No WIP issues"

# Find all review issues (awaiting review)
ls _meta/issues/review/*.md 2>/dev/null || echo "No issues in review"
ls Source/_meta/issues/review/*.md 2>/dev/null || echo "No issues in review"

# Find all blocked issues
ls _meta/issues/blocked/*.md 2>/dev/null || echo "No blocked issues"
ls Source/_meta/issues/blocked/*.md 2>/dev/null || echo "No blocked issues"

# Find all done issues
find _meta/issues/done -name "*.md" -type f
find Source/_meta/issues/done -name "*.md" -type f
```

### By Worker/Developer
```bash
# Find issues for Worker01
ls _meta/issues/new/Worker01/*.md
ls _meta/issues/done/Worker01/*.md

# Find issues for Developer02
ls Source/_meta/issues/new/Developer02/*.md
ls Source/_meta/issues/done/Developer02/*.md
```

### By Priority
```bash
# Search for high priority issues in ready/ folder
grep -r "Priority: High" _meta/issues/ready/
grep -r "Priority: High" Source/_meta/issues/ready/

# Search for high priority issues awaiting triage
grep -r "Priority: High" _meta/issues/new/
grep -r "Priority: High" Source/_meta/issues/new/
```

### Finding Work to Do
```bash
# Quick way to find ready-to-implement issues
echo "=== Repository Issues Ready to Implement ==="
ls -1 _meta/issues/ready/*.md 2>/dev/null | wc -l
ls -1 _meta/issues/ready/*.md 2>/dev/null

echo "=== Source Module Issues Ready to Implement ==="
ls -1 Source/_meta/issues/ready/*.md 2>/dev/null | wc -l
ls -1 Source/_meta/issues/ready/*.md 2>/dev/null
```

---

## 🎯 Best Practices

### For Issue Creators (Worker01, Developer01)

1. **Clear Objectives**: Define specific, measurable goals
2. **Acceptance Criteria**: Make them testable and specific
3. **Dependencies**: Document all blocking issues
4. **Right Size**: Issues should be 1-5 days of work
5. **SOLID Review**: Ensure Worker10/Developer10 reviews architecture

### For Implementers (Worker02-09, Developer02-09)

1. **Read Thoroughly**: Understand requirements before starting
2. **Update Status**: Keep issue file current with progress
3. **Ask Questions**: Comment in issue if unclear
4. **Test First**: Write tests alongside implementation
5. **Document**: Update docs as you implement

### For Reviewers (Worker10, Developer10)

1. **Architecture First**: Review design before deep dive
2. **SOLID Principles**: Validate adherence
3. **Constructive**: Provide specific, actionable feedback
4. **Timely**: Review within 1-2 days
5. **Approve Explicitly**: Mark issue as reviewed

---

## 📈 Metrics & Reporting

### Issue Velocity

Track completion rate:
```bash
# Count issues by status
echo "New (awaiting triage): $(find _meta/issues/new -name "*.md" -type f | wc -l)"
echo "Ready (can implement now): $(ls _meta/issues/ready/*.md 2>/dev/null | wc -l)"
echo "WIP (in progress): $(ls _meta/issues/wip/*.md 2>/dev/null | wc -l)"
echo "Review (awaiting review): $(ls _meta/issues/review/*.md 2>/dev/null | wc -l)"
echo "Blocked: $(ls _meta/issues/blocked/*.md 2>/dev/null | wc -l)"
echo "Done: $(find _meta/issues/done -name "*.md" -type f | wc -l)"
```

### Team Performance

Monitor per worker/developer:
```bash
# Worker01 completion
ls _meta/issues/done/Worker01/*.md | wc -l

# Developer02 completion
ls Source/_meta/issues/done/Developer02/*.md | wc -l
```

### Time Tracking

Include in issue completion:
```markdown
**Estimated**: 3 days
**Actual**: 4 days
**Variance**: +1 day
```

---

## 🔧 Issue Management Tools

### Quick Commands

Add to your shell profile:
```bash
# Move issue to ready (after triage)
issue_ready() {
    mv "_meta/issues/new/$1" "_meta/issues/ready/"
}

# Move issue to WIP (start work)
issue_wip() {
    mv "_meta/issues/ready/$1" "_meta/issues/wip/"
}

# Move issue to review
issue_review() {
    mv "_meta/issues/wip/$1" "_meta/issues/review/"
}

# Move issue to done
issue_done() {
    WORKER=$(echo $1 | cut -d'-' -f1)
    mkdir -p "_meta/issues/done/${WORKER}"
    mv "_meta/issues/review/$1" "_meta/issues/done/${WORKER}/"
}

# Move issue to blocked
issue_block() {
    # Can be called from any state
    CURRENT_DIR=$(dirname $(find _meta/issues -name "$1" -type f | head -1))
    mv "${CURRENT_DIR}/$1" "_meta/issues/blocked/"
}

# Unblock issue (move to ready)
issue_unblock() {
    mv "_meta/issues/blocked/$1" "_meta/issues/ready/"
}

# Find issue by ID
issue_find() {
    find _meta/issues -name "$1*" -type f
}
```

### Status Report Script

Create `scripts/issue_status.sh`:
```bash
#!/bin/bash
echo "=== Repository Issues ==="
echo "New (triage): $(find _meta/issues/new -name "*.md" -type f | wc -l)"
echo "Ready: $(ls _meta/issues/ready/*.md 2>/dev/null | wc -l)"
echo "WIP: $(ls _meta/issues/wip/*.md 2>/dev/null | wc -l)"
echo "Review: $(ls _meta/issues/review/*.md 2>/dev/null | wc -l)"
echo "Blocked: $(ls _meta/issues/blocked/*.md 2>/dev/null | wc -l)"
echo "Done: $(find _meta/issues/done -name "*.md" -type f | wc -l)"
echo ""
echo "=== Source Module Issues ==="
echo "New (triage): $(find Source/_meta/issues/new -name "*.md" -type f | wc -l)"
echo "Ready: $(ls Source/_meta/issues/ready/*.md 2>/dev/null | wc -l)"
echo "WIP: $(ls Source/_meta/issues/wip/*.md 2>/dev/null | wc -l)"
echo "Review: $(ls Source/_meta/issues/review/*.md 2>/dev/null | wc -l)"
echo "Blocked: $(ls Source/_meta/issues/blocked/*.md 2>/dev/null | wc -l)"
echo "Done: $(find Source/_meta/issues/done -name "*.md" -type f | wc -l)"
```

---

## 📚 Related Documentation

- **[DEVELOPMENT_PLAN.md](../../DEVELOPMENT_PLAN.md)** - Overall development plan
- **[ROADMAP.md](../issues/ROADMAP.md)** - Long-term roadmap
- **[INDEX.md](../issues/INDEX.md)** - Issue tracking index
- **[Source Module Index](../../Source/_meta/issues/new/INDEX.md)** - Module planning

---

## ❓ FAQ

### Q: When should I use Worker vs Developer?
**A**: Workers handle repository-level infrastructure. Developers handle Source module implementations.

### Q: Can one person be both a Worker and Developer?
**A**: Yes! The roles are organizational. One person can work on both tracks.

### Q: What if an issue spans both tracks?
**A**: Create separate issues in each track and link them.

### Q: When should I move an issue to ready/?
**A**: When all requirements are clear, dependencies resolved, and it's ready for anyone to pick up and implement.

### Q: Can I skip the ready/ state?
**A**: Yes, for urgent issues you can go directly from new/ to wip/, but document why in the issue.

### Q: What's the difference between blocked/ and new/?
**A**: new/ is for unspecified issues; blocked/ is for fully specified issues that hit an impediment during execution.

### Q: How do I handle urgent issues?
**A**: Mark as "Priority: High", move to ready/ immediately, and notify team. For hotfixes, can go directly to wip/.

### Q: Should I delete completed issues?
**A**: No! Move to `done/` folder for historical reference.

### Q: What about issues that are partially complete?
**A**: Keep in WIP with progress notes. Update checklist as you go.

### Q: When should I use review/ vs going straight to done/?
**A**: Use review/ for significant changes requiring peer review. Small fixes can go directly to done/ after self-review.

---

## 📊 Workflow Visualization

```
┌─────────────────────────────────────────────────────────────┐
│                     Issue Lifecycle                          │
└─────────────────────────────────────────────────────────────┘

  CREATE
    ↓
  [new/]  ← Issues awaiting triage/specification
    ↓
    ↓ (triage & clarify requirements)
    ↓
  [ready/]  ← Fully specified, ready to implement NOW
    ↓
    ↓ (developer picks up work)
    ↓
  [wip/]  ← Active development
    ↓
    ↓ (implementation complete)
    ↓
  [review/]  ← Code review (optional for small changes)
    ↓
    ↓ (approved & merged)
    ↓
  [done/]  ← Complete ✓

┌──────────────────────────────────────────────────────────────┐
│                  Blocking Path (Side Channel)                 │
└──────────────────────────────────────────────────────────────┘

From any state (new/, ready/, wip/, review/):
    ↓ (dependency discovered or clarification needed)
  [blocked/]  ← Temporarily blocked
    ↓
    ↓ (blocker resolved)
    ↓
  [ready/]  ← Returns to ready state

Key Principles:
• ready/ = "Can start implementation right now"
• blocked/ = "Keeps active workflow clean"
• review/ = "Optional for complex changes"
• done/ = "Preserves history"
```

---

## 🆘 Troubleshooting

### Issue in wrong folder
```bash
# Move from Worker to Developer track
mv _meta/issues/new/Worker02/001-issue.md Source/_meta/issues/new/Developer02/
```

### Duplicate issue IDs
- Update issue ID in file
- Ensure unique IDs per worker/developer
- Use format: WXX-NNN or DXX-NNN

### Missing issue template
- Copy from `_meta/issues/templates/`
- Or use format from this guide

---

**Maintained By**: Worker01 & Developer01  
**Last Updated**: 2025-11-13  
**Version**: 2.0 - Enhanced workflow with ready, review, and blocked states
