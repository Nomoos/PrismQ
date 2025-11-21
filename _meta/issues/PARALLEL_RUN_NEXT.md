# PARALLEL_RUN_NEXT - MVP Sprint Execution

**Sprint**: Sprint 1-2 (4 weeks) - MVP Core Workflow  
**Date**: 2025-11-21  
**Status**: Planning  
**Goal**: Build MVP end-to-end workflow following: **Idea.Create → T.Title.Draft → T.Script.Draft → T.Review.Initial → T.Script.Improvements → T.Title.Improvements → T.Review.Final → T.Publish**

---

## MVP Approach

### Why MVP First?
- **Fast validation**: 4 weeks to working product (vs 7 weeks for full features)
- **Reduced risk**: 8 issues vs 120 issues
- **Resource efficiency**: 3-4 workers vs 10-12 workers
- **Early feedback**: Learn from real usage before building advanced features

### MVP Workflow with Real Folder Names

```
PrismQ.T.Idea.Creation          → Basic idea capture
    ↓
PrismQ.T.Title.Draft            → Generate 3-5 title variants
    ↓
PrismQ.T.Script.Draft           → Generate basic script
    ↓
PrismQ.T.Rewiew.Script          → Manual review, approve/changes requested
    ↓
PrismQ.T.Script.Improvements    → Edit based on feedback
    ↓
PrismQ.T.Title.Refinement       → Update title if needed
    ↓
PrismQ.T.Rewiew.Content         → Final approval gate
    ↓
PrismQ.T.Publishing.Finalization → Mark as published
```

**Folder Paths:**
- `T/Idea/Creation/` - Idea creation
- `T/Title/Draft/` - Title drafting
- `T/Script/Draft/` - Script drafting
- `T/Rewiew/Script/` - Script review
- `T/Script/Improvements/` - Script improvements
- `T/Title/Refinement/` - Title refinement
- `T/Rewiew/Content/` - Content review
- `T/Publishing/Finalization/` - Publishing

---

## Sprint 1: Core Creation (Weeks 1-2)

### Week 1: Foundation

**Goal**: Idea → Title generation working  
**Active Workers**: 4

| Worker | Issue | Effort | Description |
|--------|-------|--------|-------------|
| **Worker02** | #MVP-001 | 2d | Basic Idea Creation |
| **Worker13** | #MVP-002 | 2d | Basic Title Generator |
| **Worker15** | Documentation | 2d | MVP workflow docs |
| **Worker04** | Test Setup | 2d | Test framework |

**Commands**:
```
Worker02: Implement #MVP-001 in T/Idea/Creation/
- Module: PrismQ.T.Idea.Creation
- Dependencies: None
- Priority: Critical
- Effort: 2 days
- Deliverable: Basic idea capture and storage working

Worker13: Implement #MVP-002 in T/Title/Draft/
- Module: PrismQ.T.Title.Draft
- Dependencies: #MVP-001 (can start in parallel)
- Priority: Critical
- Effort: 2 days
- Deliverable: Generate 3-5 title variants from idea
```

**Week 1 Deliverable**: ✅ Create idea → generate titles

---

### Week 2: Script & Review

**Goal**: Script generation and review system working  
**Active Workers**: 4

| Worker | Issue | Effort | Description |
|--------|-------|--------|-------------|
| **Worker02** | #MVP-003 | 3d | Basic Script Generator |
| **Worker10** | #MVP-004 | 2d | Simple Review System |
| **Worker15** | API Docs | 2d | Document MVP APIs |
| **Worker04** | Integration Tests | 2d | Test end-to-end flow |

**Commands**:
```
Worker02: Implement #MVP-003 in T/Script/Draft/
- Module: PrismQ.T.Script.Draft
- Dependencies: #MVP-001, #MVP-002
- Priority: Critical
- Effort: 3 days
- Deliverable: Generate basic script from idea + selected title

Worker10: Implement #MVP-004 in T/Rewiew/Script/
- Module: PrismQ.T.Rewiew.Script
- Dependencies: #MVP-003 (can start design in parallel)
- Priority: Critical
- Effort: 2 days
- Deliverable: Review workflow with approve/request changes states
```

**Week 2 Deliverable**: ✅ Generate script → perform review

---

## Sprint 2: Iteration & Publishing (Weeks 3-4)

### Week 3: Improvements

**Goal**: Improvement cycle working  
**Active Workers**: 4

| Worker | Issue | Effort | Description |
|--------|-------|--------|-------------|
| **Worker02** | #MVP-005 | 2d | Manual Script Editing |
| **Worker13** | #MVP-006 | 1d | Title Update |
| **Worker10** | #MVP-007 | 1d | Final Review Approval |
| **Worker04** | E2E Tests | 2d | Complete workflow tests |

**Commands**:
```
Worker02: Implement #MVP-005 in T/Script/Improvements/
- Module: PrismQ.T.Script.Improvements
- Dependencies: #MVP-004
- Priority: Critical
- Effort: 2 days
- Deliverable: Edit script based on review feedback

Worker13: Implement #MVP-006 in T/Title/Refinement/
- Module: PrismQ.T.Title.Refinement
- Dependencies: #MVP-005
- Priority: High
- Effort: 1 day
- Deliverable: Update title after script changes

Worker10: Implement #MVP-007 in T/Rewiew/Content/
- Module: PrismQ.T.Rewiew.Content
- Dependencies: #MVP-005, #MVP-006
- Priority: Critical
- Effort: 1 day
- Deliverable: Final approval gate before publishing
```

**Week 3 Deliverable**: ✅ Improvement cycle complete

---

### Week 4: Publishing

**Goal**: End-to-end flow complete  
**Active Workers**: 3

| Worker | Issue | Effort | Description |
|--------|-------|--------|-------------|
| **Worker02** | #MVP-008 | 2d | Basic Publishing |
| **Worker15** | User Guide | 2d | Complete documentation |
| **Worker04** | Final Testing | 2d | Validate all scenarios |

**Commands**:
```
Worker02: Implement #MVP-008 in T/Publishing/Finalization/
- Module: PrismQ.T.Publishing.Finalization
- Dependencies: #MVP-007
- Priority: Critical
- Effort: 2 days
- Deliverable: Publish approved content (mark as published, export)

Worker15: Complete user guide
- Dependencies: All MVP features
- Priority: High
- Effort: 2 days
- Deliverable: End-to-end user documentation

Worker04: Final MVP testing
- Dependencies: All MVP features
- Priority: High
- Effort: 2 days
- Deliverable: Full E2E test suite passing
```

**Week 4 Deliverable**: ✅ MVP complete and ready for use

---

## MVP Issues Summary

| Issue | Module | Stage | Worker | Effort | Description |
|-------|--------|-------|--------|--------|-------------|
| #MVP-001 | PrismQ.T.Idea.Creation | Idea.Create | Worker02 | 2d | Basic idea capture |
| #MVP-002 | PrismQ.T.Title.Draft | Title.Draft | Worker13 | 2d | Title generation |
| #MVP-003 | PrismQ.T.Script.Draft | Script.Draft | Worker02 | 3d | Script generation |
| #MVP-004 | PrismQ.T.Rewiew.Script | Review.Initial | Worker10 | 2d | Script review |
| #MVP-005 | PrismQ.T.Script.Improvements | Script.Improvements | Worker02 | 2d | Script editing |
| #MVP-006 | PrismQ.T.Title.Refinement | Title.Refinement | Worker13 | 1d | Title update |
| #MVP-007 | PrismQ.T.Rewiew.Content | Review.Final | Worker10 | 1d | Final approval |
| #MVP-008 | PrismQ.T.Publishing.Finalization | Publish | Worker02 | 2d | Publishing |

**Total**: 8 issues, 15 days of work, 4 weeks calendar time with 3-4 workers

**Folder Paths:**
- `T/Idea/Creation/`
- `T/Title/Draft/`
- `T/Script/Draft/`
- `T/Rewiew/Script/`
- `T/Script/Improvements/`
- `T/Title/Refinement/`
- `T/Rewiew/Content/`
- `T/Publishing/Finalization/`

---

## Workflow State Machine

```mermaid
stateDiagram-v2
    [*] --> IdeaCreation: PrismQ.T.Idea.Creation
    IdeaCreation --> TitleDraft: PrismQ.T.Title.Draft
    TitleDraft --> ScriptDraft: PrismQ.T.Script.Draft
    ScriptDraft --> ScriptReview: PrismQ.T.Rewiew.Script
    ScriptReview --> ScriptImprovements: changes_requested
    ScriptReview --> ContentReview: approved
    ScriptImprovements --> TitleRefinement: PrismQ.T.Script.Improvements
    TitleRefinement --> ContentReview: PrismQ.T.Title.Refinement
    ContentReview --> Publishing: approved (PrismQ.T.Rewiew.Content)
    ContentReview --> ScriptImprovements: changes_requested
    Publishing --> [*]: PrismQ.T.Publishing.Finalization
```

---

## Success Metrics

### MVP Completion Criteria
- ✅ All 8 MVP issues implemented
- ✅ End-to-end workflow tested
- ✅ Documentation complete
- ✅ At least one content piece published through full workflow

### Quality Standards
- Test coverage: >80% for MVP features
- All happy path E2E tests passing
- API documentation complete
- User guide available

---

## Post-MVP Roadmap

See `ISSUE_PLAN_T_*.md` files for full feature plans (120 issues total) to be added after MVP validates the workflow.

### Phase 2 (After MVP)
- AI-powered improvements
- SEO optimization
- Automated quality checks
- Multi-platform publishing

### Phase 3 (Future)
- A/B testing
- Analytics integration
- Collaboration features
- Batch processing

---

## Related Documents

- **MVP_WORKFLOW.md**: Detailed MVP planning and issue specifications
- **PARALLEL_RUN_NEXT_FULL.md**: Full 120-issue plan for post-MVP
- **ISSUE_PLAN_T_*.md**: Comprehensive feature plans for each module
- **Worker*/README.md**: Worker role definitions

---

**Status**: Ready for MVP Sprint 1  
**Next Action**: Worker01 to create 8 MVP issues in GitHub  
**Timeline**: 4 weeks to working MVP  
**Approach**: MVP-first, iterative development

---

**Owner**: Worker01  
**Created**: 2025-11-21  
**Last Updated**: 2025-11-21  
**Focus**: MVP workflow following Idea → Title → Script → Review → Improvements → Publish
