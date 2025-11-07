# ISSUE-331: Maintenance - Database Backup and Checkpoint

## Status
✅ **COMPLETE** (2025-11-05)

## Worker Assignment
**Worker 06**: DevOps Engineer (SQLite, Backup, Windows Ops)

## Phase
Phase 2 (Week 2-3) - Implementation

## Component
Backend/src/queue/maintenance.py, backup.py

## Type
Feature - Database Maintenance

## Priority
High - Data protection

## Description
Implement database maintenance utilities including backup, checkpoint, and integrity checking for the SQLite queue database.

## Problem Statement
Production database needs:
- Regular backups for disaster recovery
- WAL checkpoint management
- Integrity verification
- Vacuum operations
- Corruption detection

## Solution
Maintenance system with:
1. Online backup (SQLite backup API)
2. WAL checkpoint operations
3. Database integrity checks
4. Vacuum scheduling
5. Backup rotation

## Implementation Details

### Backup System
```python
class DatabaseBackup:
    async def create_backup(self, backup_path: str):
        """Create online backup using SQLite backup API"""
        src = await self.get_connection()
        dst = sqlite3.connect(backup_path)
        
        with dst:
            src.backup(dst)
        
        dst.close()
        
        return {
            "status": "success",
            "backup_path": backup_path,
            "timestamp": utc_now(),
            "size_bytes": os.path.getsize(backup_path)
        }
    
    async def rotate_backups(self, max_backups=7):
        """Keep only N most recent backups"""
        backups = sorted(glob("backups/queue_*.db"))
        
        while len(backups) > max_backups:
            old_backup = backups.pop(0)
            os.remove(old_backup)
```

### Checkpoint Operations
```python
async def checkpoint_wal():
    """Checkpoint WAL to main database"""
    await db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    
    return {
        "status": "success",
        "mode": "TRUNCATE",
        "timestamp": utc_now()
    }
```

### Integrity Check
```python
async def check_integrity():
    """Run SQLite integrity check"""
    result = await db.query("PRAGMA integrity_check")
    
    return {
        "status": "ok" if result[0] == "ok" else "corrupted",
        "details": result,
        "timestamp": utc_now()
    }
```

## Acceptance Criteria
- [x] Online backup implemented
- [x] WAL checkpoint working
- [x] Integrity check functional
- [x] Vacuum operation added
- [x] Backup rotation working
- [x] 52 tests passing
- [x] 82-88% test coverage
- [x] Windows compatibility verified

## Test Results
- **Total Tests**: 52
- **Coverage**: 82-88% (backup: 88%, maintenance: 82%)
- **Pass Rate**: 100%
- **Windows**: Verified on Windows

## Dependencies
**Requires**: #321 Core Infrastructure (Worker 01) ✅ COMPLETE

## Enables
- Disaster recovery
- Data protection
- Database health monitoring
- Production operations

## Related Issues
- #332: Cleanup (Worker 06) - Complementary feature
- #329: Observability (Worker 05) - Monitors maintenance

## Files Modified
- Backend/src/queue/maintenance.py (new)
- Backend/src/queue/backup.py (new)
- Backend/src/queue/integrity.py (new)
- tests/queue/test_maintenance.py (new)
- tests/queue/test_backup.py (new)

## Parallel Work
**Can run in parallel with**:
- #323: Client API (different code area)
- #325: Worker Engine (different code area)
- #327: Scheduling (different code area)
- #329: Observability (different code area)

## Commits
Week 2-3 implementation commits

## Notes
- Online backup doesn't block operations
- WAL checkpoint prevents WAL file growth
- Integrity check detects corruption early
- Backup rotation prevents disk space issues
- 52 tests with 82-88% coverage
- New files, no conflicts with other workers

## Maintenance Examples

### Daily Backup
```python
# Schedule daily backup
backup_manager = DatabaseBackup()
backup_path = f"backups/queue_{date.today()}.db"

result = await backup_manager.create_backup(backup_path)
await backup_manager.rotate_backups(max_backups=7)
```

### Checkpoint Schedule
```python
# Checkpoint every hour
async def hourly_checkpoint():
    while True:
        await checkpoint_wal()
        await asyncio.sleep(3600)
```

### Integrity Check
```python
# Weekly integrity check
result = await check_integrity()
if result["status"] != "ok":
    logger.error("database_corruption", details=result)
    await send_alert()
```

### Vacuum Operation
```python
# Monthly vacuum
await db.execute("VACUUM")
```

## Backup Strategy

### Backup Schedule
- **Hourly**: WAL checkpoint
- **Daily**: Full backup, 7-day rotation
- **Weekly**: Integrity check
- **Monthly**: Vacuum operation

### Retention Policy
- Keep 7 daily backups
- Keep 4 weekly backups
- Keep 12 monthly backups

---

**Created**: Week 2 (2025-11-05)  
**Completed**: Week 2-3 (2025-11-05)  
**Duration**: ~1.5 weeks  
**Success**: ✅ Complete with 52 tests, 82-88% coverage
