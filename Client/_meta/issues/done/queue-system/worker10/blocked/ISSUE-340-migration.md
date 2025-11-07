# ISSUE-340: Migration - Utilities and Procedures

## Status
⏳ **PLANNED** - Depends on #339

## Worker Assignment
**Worker 10**: Senior Engineer (Integration, Architecture)

## Phase
Phase 3 (Week 4) - Integration & Testing

## Component
Backend/src/queue/migration/

## Type
Feature - Migration Tools

## Priority
High - Required for production migration

## Description
Create migration utilities and procedures for transitioning from old BackgroundTaskManager to new queue system, including data migration, testing, and rollback procedures.

## Problem Statement
Need to migrate production systems:
- Migrate in-flight tasks safely
- No data loss during migration
- Zero-downtime deployment
- Rollback capability
- Validation and testing

## Solution
Migration toolkit with:
1. Data migration scripts
2. Task state transfer
3. Validation utilities
4. Rollback procedures
5. Migration runbooks

## Migration Scope

### Data Migration
- [ ] Export tasks from old system
- [ ] Import tasks to new queue
- [ ] Preserve task state and metadata
- [ ] Validate data integrity
- [ ] Handle edge cases

### Zero-Downtime Migration
- [ ] Dual-write mode (both systems)
- [ ] Gradual cutover
- [ ] Read from new, fallback to old
- [ ] Validation during migration
- [ ] Final cutover

### Rollback Procedures
- [ ] Revert configuration
- [ ] Restore old task manager
- [ ] Data consistency check
- [ ] Testing rollback path

## Implementation Details

### Migration Utilities
```python
class QueueMigration:
    def __init__(self, old_manager, new_queue):
        self.old_manager = old_manager
        self.new_queue = new_queue
    
    async def export_tasks(self):
        """Export tasks from old system"""
        tasks = await self.old_manager.get_all_tasks()
        return [self.convert_task(t) for t in tasks]
    
    async def import_tasks(self, tasks):
        """Import tasks to new queue"""
        for task in tasks:
            await self.new_queue.enqueue(
                type=task["type"],
                payload=task["payload"],
                status=task["status"],
                created_at=task["created_at"]
            )
    
    async def migrate_inflight_tasks(self):
        """Migrate tasks that are currently running"""
        inflight = await self.old_manager.get_running_tasks()
        
        for task in inflight:
            # Wait for completion or timeout
            await self.wait_or_timeout(task)
            
            # Transfer to new queue
            if not task.completed:
                await self.transfer_task(task)
    
    async def validate_migration(self):
        """Validate migration completed successfully"""
        old_count = await self.old_manager.count_tasks()
        new_count = await self.new_queue.count_tasks()
        
        return {
            "old_count": old_count,
            "new_count": new_count,
            "match": old_count == new_count,
            "missing": old_count - new_count
        }
```

### Zero-Downtime Strategy
```python
class DualWriteManager:
    """Write to both systems during migration"""
    
    def __init__(self, old_manager, new_queue):
        self.old_manager = old_manager
        self.new_queue = new_queue
        self.mode = "dual-write"  # dual-write, new-only
    
    async def schedule_task(self, task_type, payload, **kwargs):
        """Write to both systems"""
        if self.mode == "dual-write":
            # Write to both
            old_id = await self.old_manager.schedule_task(
                task_type, payload, **kwargs
            )
            new_id = await self.new_queue.enqueue(
                type=task_type,
                payload=payload,
                **kwargs
            )
            return {"old": old_id, "new": new_id}
        else:
            # New system only
            return await self.new_queue.enqueue(
                type=task_type,
                payload=payload,
                **kwargs
            )
```

### Rollback Procedure
```python
async def rollback_migration():
    """Rollback to old system"""
    # Step 1: Switch configuration
    config.USE_QUEUE_SYSTEM = False
    
    # Step 2: Stop new workers
    await stop_queue_workers()
    
    # Step 3: Start old task manager
    await start_old_task_manager()
    
    # Step 4: Validate
    status = await validate_system_health()
    
    return status
```

## Migration Phases

### Phase 1: Preparation (Pre-Migration)
1. Backup current task data
2. Deploy new queue system (inactive)
3. Test migration scripts in staging
4. Prepare rollback procedures
5. Document migration steps

### Phase 2: Dual-Write (Migration Start)
1. Enable dual-write mode
2. New tasks go to both systems
3. Workers consume from old system
4. Validate data consistency
5. Monitor for issues

### Phase 3: Read Migration (Cutover)
1. Stop accepting tasks in old system
2. Wait for old tasks to complete
3. Migrate any remaining tasks
4. Start queue workers
5. Begin reading from new queue

### Phase 4: Cleanup (Post-Migration)
1. Disable dual-write mode
2. Archive old task data
3. Remove old task manager code
4. Update documentation
5. Monitor new system

## Acceptance Criteria
- [ ] Migration utilities created
- [ ] Data export/import working
- [ ] Zero-downtime strategy implemented
- [ ] Rollback procedures tested
- [ ] Validation utilities complete
- [ ] Migration runbook written
- [ ] Tested in staging environment
- [ ] Production migration successful

## Dependencies
**Requires**: 
- #339: Integration ⏳ PLANNED (must complete first)
- #321-#332: All Phase 2 features ✅ COMPLETE
- #333: Testing ⏳ PENDING (for validation)

**Blocked By**: 
- **#339: Integration** (cannot start until adapter ready)
- Partial: #333 testing (for validation)

## Blocks
- Production deployment
- System migration completion

## Related Issues
- #339: Integration (Worker 10) - Must complete first
- #336: Operations Guide (Worker 08) - Needs migration docs
- All Phase 2 issues - Migrating to their features

## Parallel Work
**Cannot run in parallel with**:
- #339: Integration (depends on it)

**Can run in parallel with**:
- #333-#334: Testing (different focus)
- #335-#336: Documentation (partial)

## Files to Create
```
Backend/src/queue/migration/
├── migrator.py (migration utilities)
├── validator.py (validation tools)
├── dual_write.py (dual-write manager)
└── rollback.py (rollback utilities)

_meta/docs/queue/operations/
├── MIGRATION.md (migration runbook)
├── ROLLBACK.md (rollback procedures)
└── VALIDATION.md (validation guide)

tests/migration/
├── test_migration.py
├── test_dual_write.py
├── test_rollback.py
└── test_validation.py
```

## Migration Runbook Structure

### Pre-Migration Checklist
```markdown
- [ ] Backup all task data
- [ ] Deploy new queue system (inactive)
- [ ] Test migration scripts in staging
- [ ] Prepare rollback procedures
- [ ] Notify stakeholders
- [ ] Schedule maintenance window (if needed)
```

### Migration Steps
```markdown
1. Enable dual-write mode
2. Monitor for 24 hours
3. Validate data consistency
4. Migrate in-flight tasks
5. Cut over to new queue
6. Monitor for 24 hours
7. Disable dual-write
8. Archive old data
```

### Rollback Steps
```markdown
1. Switch USE_QUEUE_SYSTEM=false
2. Stop queue workers
3. Start old task manager
4. Validate system health
5. Monitor for issues
6. Document reasons for rollback
```

## Testing Strategy

### Staging Tests
- [ ] End-to-end migration
- [ ] Rollback procedure
- [ ] Data validation
- [ ] Performance testing
- [ ] Load testing

### Production Validation
- [ ] Monitor error rates
- [ ] Check task completion rates
- [ ] Validate data consistency
- [ ] Performance metrics
- [ ] User experience

## Risk Mitigation

### Risks
1. **Data loss**: Backup before migration, dual-write mode
2. **Downtime**: Zero-downtime strategy, rollback ready
3. **Performance**: Load test before migration
4. **Bugs**: Extensive testing in staging

### Mitigation
- Comprehensive testing
- Gradual rollout
- Monitoring at every step
- Quick rollback capability
- Backup procedures

## Timeline
- **Week 4, Day 3**: Design migration strategy (after #339)
- **Week 4, Day 4**: Implement utilities
- **Week 4, Day 5**: Testing and validation
- **Week 4, Day 6**: Documentation
- **Week 4, Day 7**: Staging migration test
- **Post Week 4**: Production migration

## Success Metrics

### Migration Success
- Zero data loss
- Zero unplanned downtime
- <1% error rate during migration
- All tasks migrated successfully
- Rollback procedures validated

### Post-Migration
- Task completion rate: >99%
- Queue performance: meets targets
- No increase in error rates
- Monitoring and alerting working

## Notes
- Critical dependency on #339
- High-priority work for Week 4
- Enables production use
- Comprehensive testing required
- Coordinate with Worker 08 for docs
- Must validate in staging first

---

**Created**: Week 4 (Planned)  
**Status**: ⏳ Depends on #339  
**Blockers**: #339 Integration (high priority)  
**Priority**: High
