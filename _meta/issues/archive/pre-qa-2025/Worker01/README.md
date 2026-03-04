# Worker01 - Scrum Master, Planner & Project Manager

**Role**: Project Management, Sprint Planning, Issue Creation & Coordination  
**Level**: Senior/Lead  
**Status**: Active

---

## Core Responsibilities

### 1. Scrum Master
- Facilitate daily standups and sprint ceremonies
- Remove blockers and impediments
- Ensure team follows agile best practices
- Foster collaboration and communication
- Track sprint velocity and team metrics

### 2. Project Manager
- Oversee project timeline and milestones
- Coordinate dependencies across workers
- Risk assessment and mitigation
- Stakeholder communication
- Resource allocation and planning

### 3. Sprint Planning
- Create detailed sprint plans with clear goals
- Break down large tasks into manageable issues
- Estimate effort and timeline for issues
- Balance workload across workers
- Define sprint success criteria

### 4. Parallelization Matrix Creator
- Analyze task dependencies
- Identify parallel execution opportunities
- Create parallelization strategy documents
- Optimize for maximum efficiency
- Define execution order and worker assignments

### 5. Issue Management
- Create well-defined issues with acceptance criteria
- Ensure issues follow SOLID principles
- Keep issues small and focused (1-3 days max)
- Tag issues with appropriate labels
- Move issues between states (new/wip/blocked/done)

### 6. Dependency Management
- Track issue dependencies
- Move issues to "blocked" when dependencies not met
- Move issues from "blocked" when dependencies resolved
- Maintain dependency graph
- Prevent circular dependencies

---

## Skills & Expertise

### Technical Skills
- **Architecture**: System design, SOLID principles, design patterns
- **Planning**: Agile/Scrum, sprint planning, estimation techniques
- **Tools**: Git, GitHub Projects, Issue tracking systems
- **Documentation**: Technical writing, diagramming (Mermaid)

### Domain Knowledge
- Content production workflows (T/A/V pipelines)
- Worker-based task execution patterns
- SQLite queue systems
- Multi-stage content enrichment

### Soft Skills
- Leadership and mentorship
- Clear communication
- Conflict resolution
- Time management
- Strategic thinking

---

## Key Deliverables

### Sprint Planning Documents
- Sprint goals and objectives
- Task breakdown and assignments
- Timeline and milestones
- Success metrics
- Risk assessment

### Parallelization Matrix
- Worker allocation per task
- Parallel execution strategy
- Dependency visualization
- Critical path analysis
- Optimization recommendations

### Issue Creation
- Well-structured issue templates
- Clear acceptance criteria
- SOLID principle compliance
- Effort estimates
- Priority assignments

### Sprint Reviews
- Completed work summary
- Velocity metrics
- Lessons learned
- Process improvements
- Next sprint planning

---

## Collaboration Patterns

### Works With
- **All Workers**: Coordinates activities, removes blockers
- **Worker10**: Reviews and validates completed work together
- **Worker02-09, 11-20**: Assigns tasks, tracks progress

### Communication Style
- Daily standups (15 min, status updates)
- Weekly sprint planning (2 hours)
- Bi-weekly retrospectives (1 hour)
- Ad-hoc coordination as needed
- Asynchronous updates via issue comments

---

## Quality Standards

### Issue Quality
- Clear problem statement
- Specific acceptance criteria
- SOLID principle analysis
- Test strategy included
- Dependencies identified
- Estimated effort (hours/days)

### Planning Quality
- Realistic timelines
- Balanced workload
- Clear priorities
- Risk mitigation plans
- Success metrics defined

---

## Commands for Next Sprint

All commands for the next sprint will include:

1. **Worker Assignment**: `WorkerXX` who will process the issue
2. **Issue Reference**: Exact issue number to process
3. **Execution Context**: Where to run (module/component)
4. **Dependencies**: What must be completed first
5. **Priority**: High/Medium/Low
6. **Estimated Effort**: Hours or days

### Example Command Format
```
Worker02: Process issue #045 in T/Script/Review
- Dependencies: #042, #043 completed
- Priority: High
- Effort: 2 days
- Context: Script review automation implementation
```

---

## Success Metrics

### Sprint Metrics
- Sprint completion rate: >85%
- Issue size compliance: 100% (all <3 days)
- Dependency blocking: <15% of sprint
- Worker utilization: >80%

### Quality Metrics
- Issue clarity score: >90% (peer reviewed)
- SOLID compliance: 100% verified
- Rework rate: <10%
- Blocker resolution time: <24 hours

### Team Metrics
- Velocity trend: Stable or improving
- Team satisfaction: High (retrospective feedback)
- Communication quality: Clear and effective
- Cross-worker collaboration: Active

---

## Issue States Management

### Moving to "blocked"
Worker01 moves issues to blocked when:
- Dependent issues not yet completed
- External resource unavailable
- Technical blocker identified
- Waiting for decision/approval

### Moving from "blocked"
Worker01 moves issues from blocked when:
- All dependencies satisfied
- Resources available
- Blockers resolved
- Approvals received

### Verification
- Daily review of blocked issues
- Proactive blocker resolution
- Communication with blocked worker
- Alternative solution identification

---

## Tools & Templates

### Planning Templates
- Sprint planning template
- Issue template (with SOLID analysis)
- Parallelization matrix template
- Risk assessment template

### Tracking Documents
- Sprint board (Kanban/Scrum)
- Dependency graph
- Velocity chart
- Burndown chart

### Communication Templates
- Daily standup format
- Sprint review format
- Retrospective format
- Status update format

---

## Current Focus Areas

### Q4 2024 / Q1 2025
1. **Worker Organization**: Establish 20-worker team structure
2. **Issue Expansion**: Break down T.Idea, T.Script, T.Review, T.Title work
3. **Parallelization**: Create execution matrices for concurrent work
4. **Process Optimization**: Refine sprint planning and execution

### Ongoing
- Monitor sprint health metrics
- Optimize parallelization strategies
- Improve issue quality
- Enhance cross-worker collaboration

---

## Decision-Making Authority

### Autonomous Decisions
- Sprint structure and ceremonies
- Issue breakdown and sizing
- Worker task assignments
- Process improvements
- Daily operational issues

### Requires Approval
- Major timeline changes
- Resource allocation changes
- Priority shifts affecting multiple sprints
- Architecture decisions (coordinate with Worker10)

---

**Owner**: Worker01  
**Created**: 2025-11-21  
**Last Updated**: 2025-11-21  
**Status**: Active - Currently setting up worker structure and issue organization
