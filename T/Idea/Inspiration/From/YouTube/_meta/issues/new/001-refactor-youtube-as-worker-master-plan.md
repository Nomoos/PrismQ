# Issue #001: Refactor YouTube Shorts Source as Worker - Master Plan

**Type**: Architecture Refactor  
**Worker**: Worker 01 - Project Manager/Scrum Master  
**Status**: Planning  
**Priority**: High  
**Created**: 2025-11-11  
**Duration**: 4-6 weeks (parallelized)

---

## Executive Summary

Refactor the YouTube Shorts Source module (PrismQ.T.Idea.Inspiration.Froms.Content.Shorts.YouTube) to implement worker-based architecture following PrismQ.Client patterns. This will enable:

- **Persistent task execution** via SQLite queue
- **State management** via TaskManager API
- **Parameter variant registration** for different scraping modes
- **LIFO task claiming** by default
- **Better scalability** and **observability**

---

## Current State

### Module Location
`Sources/Content/Shorts/YouTube/`

### Current Architecture
- **3 Scraping Plugins**: 
  - `youtube_plugin.py` - YouTube API search (legacy)
  - `youtube_channel_plugin.py` - Channel-based scraping via yt-dlp
  - `youtube_trending_plugin.py` - Trending page scraping via yt-dlp

- **CLI Interface**: `src/cli.py` with multiple commands
  - `scrape` - Legacy YouTube API
  - `scrape-channel` - Channel scraping
  - `scrape-trending` - Trending scraping
  - `scrape-keyword` - Keyword search
  - `list`, `stats`, `process`, `clear` - Data management

- **Core Components**:
  - `config.py` - Configuration management
  - `database.py` - SQLite operations
  - `metrics.py` - Universal metrics
  - `idea_processor.py` - IdeaInspiration transformation

- **Data Storage**:
  - Local SQLite database per module
  - Central IdeaInspiration database integration

### Current Design Principles
✅ Already follows SOLID principles:
- Single Responsibility Principle (SRP)
- Open/Closed Principle (OCP)
- Liskov Substitution Principle (LSP)
- Interface Segregation Principle (ISP)
- Dependency Inversion Principle (DIP)

---

## Target Architecture

### Worker-Based Implementation

Following the Worker Implementation Template from PrismQ.Client:

```
Worker Process
├── Task Poller       # Poll SQLite queue for tasks
├── Task Processor    # Execute YouTube scraping logic
├── Error Handler     # Manage failures and retries
├── Result Reporter   # Save results to SQLite
└── Health Monitor    # Report worker health
```

### Integration Points

1. **SQLite Queue** (from Issue #320-340)
   - Task persistence
   - LIFO claiming strategy (default)
   - Priority management
   - Retry logic with exponential backoff

2. **TaskManager API**
   - State updates (QUEUED → RUNNING → COMPLETED/FAILED)
   - Progress reporting
   - Health monitoring
   - Metrics collection

3. **Parameter Variants**
   - Register all scraping modes as task types
   - Mode-specific configurations
   - Validation rules per mode

4. **Results Storage**
   - SQLite database for scraped data
   - Central IdeaInspiration database
   - Deduplication logic
   - Metrics tracking

---

## Refactor Strategy

### Principle: **SOLID Compliance**

All refactoring must:
- ✅ Keep single responsibilities
- ✅ Maintain open/closed principle
- ✅ Ensure substitutability
- ✅ Use minimal interfaces
- ✅ Depend on abstractions

### Approach: **Incremental Migration**

1. **Phase 1**: Worker Infrastructure (Week 1-2)
   - Create worker base classes
   - Implement task polling
   - Set up SQLite integration
   - Parameter registration system

2. **Phase 2**: Plugin Migration (Week 2-3)
   - Migrate channel plugin to worker
   - Migrate trending plugin to worker
   - Migrate API plugin to worker (optional)
   - Keyword search implementation

3. **Phase 3**: Integration & Testing (Week 3-4)
   - TaskManager API integration
   - Comprehensive testing
   - Documentation updates
   - Performance validation

4. **Phase 4**: Deployment & Monitoring (Week 5-6)
   - Production deployment
   - Monitoring setup
   - Performance tuning
   - Final documentation

---

## Worker Specializations

### Worker01 - Project Manager/Scrum Master
**Responsibilities**:
- ✅ Create this master plan
- Create specialized worker issues
- Review all issues for SOLID compliance
- Ensure small, focused issues
- Assign appropriate workers
- Track overall progress
- Coordinate integration

**Skills**: Architecture, planning, SOLID principles, project management

---

### Worker02 - Python Specialist
**Responsibilities**:
- Implement worker base classes
- Refactor plugin architecture
- Ensure Python best practices
- Code optimization
- Type hints and documentation

**Skills**: Python 3.10+, async programming, SOLID principles, yt-dlp, SQLite

---

### Worker03 - Full Stack Developer
**Responsibilities**:
- API endpoint development
- Frontend integration
- Parameter validation
- Mode switching logic

**Skills**: Python, FastAPI/Flask, Vue.js, REST API design

---

### Worker04 - QA/Testing Specialist
**Responsibilities**:
- Test strategy development
- Unit test implementation
- Integration tests
- Windows-specific testing
- CI/CD integration

**Skills**: pytest, integration testing, Windows testing, GitHub Actions

---

### Worker05 - DevOps/Infrastructure
**Responsibilities**:
- SQLite queue setup
- Worker deployment
- Monitoring setup
- Performance optimization

**Skills**: SQLite, monitoring tools, system administration

---

### Worker06 - Database Specialist
**Responsibilities**:
- Schema design
- Migration utilities
- Database optimization
- Data integrity

**Skills**: SQLite, SQL optimization, data modeling

---

### Worker10 - Review Specialist
**Responsibilities**:
- Code review
- Architecture review
- SOLID compliance verification
- Integration validation
- Documentation review

**Skills**: Senior engineering, architecture, code review, SOLID principles

---

## Issue Breakdown Plan

Worker01 will create the following issues in worker-specific folders:

### Core Infrastructure Issues

**Worker02 Issues** (Python Specialist):
- [ ] #002 - Create Worker Base Class and Interface
- [ ] #003 - Implement Task Polling Mechanism
- [ ] #005 - Refactor Plugin Architecture for Worker Pattern
- [ ] #006 - Implement Error Handling and Retry Logic

**Worker06 Issues** (Database Specialist):
- [ ] #004 - Design Worker Task Schema in SQLite
- [ ] #007 - Implement Result Storage Layer
- [ ] #008 - Create Migration Utilities for Data Transfer

### Plugin Migration Issues

**Worker02 Issues** (Python Specialist):
- [ ] #009 - Migrate YouTubeChannelPlugin to Worker
- [ ] #010 - Migrate YouTubeTrendingPlugin to Worker
- [ ] #011 - Implement YouTube Keyword Search Worker
- [ ] #012 - Migrate YouTubePlugin to Worker (Optional/Legacy)

### Integration Issues

**Worker03 Issues** (Full Stack):
- [ ] #013 - Implement Parameter Variant Registration
- [ ] #014 - Create Worker Management API Endpoints
- [ ] #015 - Update CLI for Worker-Based Execution

**Worker05 Issues** (DevOps):
- [ ] #016 - Integrate with TaskManager API
- [ ] #017 - Setup Worker Health Monitoring
- [ ] #018 - Implement Metrics Collection

### Testing Issues

**Worker04 Issues** (QA/Testing):
- [ ] #019 - Create Worker Unit Tests
- [ ] #020 - Implement Integration Tests
- [ ] #021 - Windows-Specific Subprocess Testing
- [ ] #022 - Performance and Load Testing

### Review Issues

**Worker10 Issues** (Review Specialist):
- [ ] #023 - Review Worker Architecture for SOLID Compliance
- [ ] #024 - Integration Testing and Validation
- [ ] #025 - Documentation Review and Completion

---

## SOLID Principles Checklist

Each issue must be reviewed against SOLID principles:

### Single Responsibility Principle (SRP)
- [ ] Each class has one reason to change
- [ ] Worker focuses on task execution only
- [ ] Separate concerns: polling, execution, storage, reporting

### Open/Closed Principle (OCP)
- [ ] Worker is open for extension (new scraping modes)
- [ ] Worker is closed for modification (base implementation stable)
- [ ] Plugin system allows new scrapers without changing core

### Liskov Substitution Principle (LSP)
- [ ] All worker implementations can substitute base worker
- [ ] All plugins can substitute base plugin interface
- [ ] No breaking changes to abstractions

### Interface Segregation Principle (ISP)
- [ ] Worker interface has minimal required methods
- [ ] No forcing implementations to depend on unused methods
- [ ] Focused, specific interfaces

### Dependency Inversion Principle (DIP)
- [ ] High-level modules depend on abstractions
- [ ] Dependencies injected (Config, Database, Queue)
- [ ] No direct dependencies on concrete implementations

---

## Issue Size Guidelines

Each issue should be:
- ✅ **Small**: 1-3 days maximum
- ✅ **Focused**: Single responsibility
- ✅ **Testable**: Clear acceptance criteria
- ✅ **Independent**: Minimal dependencies
- ✅ **Reviewable**: Easy to code review

If an issue seems too large:
- Break it down further
- Create sub-issues
- Identify core vs. optional features

---

## Parallelization Strategy

### Phase 1 - Infrastructure (Week 1-2)
```
Worker02: #002, #003, #005 ████████ (Core infrastructure)
Worker06: #004, #007      ████████ (Database layer)
Worker05: #016            ████     (TaskManager integration planning)
```
**Can work in parallel**: Yes (different code areas)

### Phase 2 - Plugin Migration (Week 2-3)
```
Worker02: #009 ████████ (Channel plugin)
Worker02: #010 ████████ (Trending plugin)
Worker02: #011 ████████ (Keyword search)
Worker03: #013 ████████ (Parameter registration)
```
**Can work in parallel**: Mostly (some sequencing needed)

### Phase 3 - Integration & Testing (Week 3-4)
```
Worker03: #014, #015 ████████ (API & CLI)
Worker04: #019, #020 ████████ (Testing)
Worker05: #017, #018 ████████ (Monitoring)
Worker10: #023       ████     (Review)
```
**Can work in parallel**: Yes (different concerns)

### Phase 4 - Validation (Week 5-6)
```
Worker04: #021, #022 ████████ (Performance testing)
Worker10: #024, #025 ████████ (Final validation)
```
**Can work in parallel**: Partially (some sequencing)

---

## Success Criteria

### Functional Requirements
- [ ] All scraping modes work as workers
- [ ] Tasks persist across restarts
- [ ] State updates to TaskManager API
- [ ] Results saved to SQLite
- [ ] LIFO claiming works correctly
- [ ] Parameter variants registered
- [ ] Retry logic handles failures
- [ ] Health monitoring operational

### Non-Functional Requirements
- [ ] SOLID principles maintained
- [ ] Test coverage > 80%
- [ ] Performance equivalent or better
- [ ] Windows compatibility verified
- [ ] Documentation complete
- [ ] Code review approved

### Integration Requirements
- [ ] SQLite queue integration
- [ ] TaskManager API integration
- [ ] Backward compatibility (CLI)
- [ ] Central database integration
- [ ] Monitoring integration

---

## Dependencies

### External Dependencies
- SQLite Queue System (Issues #320-340)
- TaskManager API (from PrismQ.Client)
- IdeaInspiration Model (central database)

### Internal Dependencies
- yt-dlp library
- YouTube Data API (optional)
- Config management
- Logging infrastructure

---

## Risk Assessment

### Technical Risks

**Risk**: Breaking existing functionality
- **Mitigation**: Comprehensive testing, gradual migration
- **Severity**: High
- **Probability**: Medium

**Risk**: Performance degradation
- **Mitigation**: Load testing, optimization
- **Severity**: Medium
- **Probability**: Low

**Risk**: SQLite queue bottleneck
- **Mitigation**: Benchmarking, optimization from #337
- **Severity**: Medium
- **Probability**: Low

### Process Risks

**Risk**: Issue scope creep
- **Mitigation**: Strict issue size limits, Worker01 review
- **Severity**: Medium
- **Probability**: Medium

**Risk**: Worker coordination overhead
- **Mitigation**: Clear interfaces, minimal dependencies
- **Severity**: Low
- **Probability**: Low

**Risk**: SOLID violations
- **Mitigation**: Worker10 reviews, code review process
- **Severity**: High
- **Probability**: Low

---

## Timeline

### Optimistic (4 weeks)
```
Week 1: Infrastructure complete
Week 2: Plugins migrated
Week 3: Integration complete
Week 4: Testing and review done
```

### Realistic (5 weeks)
```
Week 1-2: Infrastructure (with buffer)
Week 3: Plugin migration
Week 4: Integration and testing
Week 5: Review and fixes
```

### Pessimistic (6 weeks)
```
Week 1-2: Infrastructure (with issues)
Week 3-4: Plugin migration (with refactoring)
Week 5: Integration (with debugging)
Week 6: Testing, review, fixes
```

**Target**: 5 weeks (realistic with some buffer)

---

## Next Steps (Worker01 Actions)

### Immediate (This Week)
1. [ ] Create Worker01 folder: `_meta/issues/new/Worker01/`
2. [ ] Create issue #002-404 (Worker02 infrastructure issues)
3. [ ] Create issue #004-407 (Worker06 database issues)
4. [ ] Review all issues for SOLID compliance
5. [ ] Ensure issues are small and focused

### Week 1
6. [ ] Create issue #009-411 (Worker02 plugin issues)
7. [ ] Create issue #013-414 (Worker03 integration issues)
8. [ ] Create issue #016-417 (Worker05 monitoring issues)
9. [ ] Assign workers based on availability

### Week 2
10. [ ] Create issue #019-421 (Worker04 testing issues)
11. [ ] Create issue #023-424 (Worker10 review issues)
12. [ ] Track progress and adjust assignments
13. [ ] Coordinate integration planning

### Week 3-5
14. [ ] Monitor progress across all workers
15. [ ] Address blockers and dependencies
16. [ ] Facilitate integration meetings
17. [ ] Review pull requests
18. [ ] Update this master plan with actual progress

---

## Communication Plan

### Daily Standups
Each worker answers:
1. What did I complete yesterday?
2. What am I working on today?
3. Am I blocked?

### Weekly Reviews
- Progress across all workers
- Issue completion rate
- Risk assessment
- Timeline adjustments

### Code Reviews
- Worker02 code reviewed by Worker10
- All PRs require approval
- SOLID compliance check
- Test coverage verification

---

## Documentation Requirements

### Each Issue Must Include
- [ ] Clear problem statement
- [ ] SOLID principle analysis
- [ ] Implementation approach
- [ ] Acceptance criteria
- [ ] Test strategy
- [ ] Files to modify
- [ ] Dependencies

### Master Documentation Updates
- [ ] Architecture diagram (before/after)
- [ ] Worker implementation guide
- [ ] Migration guide
- [ ] API documentation
- [ ] Deployment guide

---

## References

### Templates & Guides
- [Worker Implementation Template](https://github.com/Nomoos/PrismQ.Client/blob/3d8301aa5641d772fa39d84f9c0a54c18ee7c1d2/_meta/templates/WORKER_IMPLEMENTATION_TEMPLATE.md)
- [Integration Guide](https://github.com/Nomoos/PrismQ.Client/blob/3d8301aa5641d772fa39d84f9c0a54c18ee7c1d2/_meta/examples/workers/INTEGRATION_GUIDE.md)

### Related Issues
- #320-340: SQLite Queue System
- #300-303: Previous Worker Organization
- Current YouTube module issues

### Documentation
- `Sources/Content/Shorts/YouTube/README.md` - Current architecture
- `_meta/docs/SOLID_PRINCIPLES.md` - SOLID principles guide
- `_meta/issues/new/README-WORKER-ORGANIZATION.md` - Worker organization

---

## Success Metrics

### Code Quality
- Test coverage: >80%
- Code review approval: 100%
- SOLID compliance: 100%
- Documentation: Complete

### Timeline
- Actual vs. planned: ±20%
- Issue completion rate: >90%
- Rework rate: <10%

### Functionality
- All modes working: 100%
- Performance maintained: 100%
- Zero breaking changes: 100%

---

## Approval & Sign-off

### Planning Phase
- [ ] Worker01 (this plan created)
- [ ] Team review
- [ ] Architecture approval
- [ ] Resource allocation

### Implementation Phase
- [ ] Issues created and assigned
- [ ] Workers confirmed availability
- [ ] Dependencies identified
- [ ] Timeline agreed

### Completion Phase
- [ ] All acceptance criteria met
- [ ] Documentation complete
- [ ] Code review passed
- [ ] Testing complete
- [ ] Deployment successful

---

**Status**: ✅ Master Plan Created - Awaiting Team Review  
**Next Action**: Worker01 to create specialized worker issues  
**Created**: 2025-11-11  
**Last Updated**: 2025-11-11  
**Owner**: Worker01 - Project Manager/Scrum Master
