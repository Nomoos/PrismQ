---
name: Feature Request
about: Full Integration with Recursive Support (Option 3)
title: '[FEATURE] Full Integration with Backup, Rollback, and Recursive Support'
labels: enhancement
assignees: ''
---

## Feature Description
Implement a complete, production-ready submodule management solution with backup/rollback capabilities, full recursive support, dependency resolution, and interactive confirmation mode.

## Problem It Solves
While Options 1 and 2 provide good functionality, complex scenarios require:
- **Safety**: Backup before operations in case something goes wrong
- **Recovery**: Rollback capability if operations fail
- **Dependencies**: Ensure parent repos exist before adding child submodules
- **Confirmation**: Interactive mode to confirm actions before execution
- **Robustness**: Handle any edge cases and complex nested structures

This feature provides enterprise-grade reliability for mission-critical module management.

## Proposed Solution
Implement Option 3: Full Integration with Recursive Support

### Core Features
1. **All Option 2 Features**
   - Smart submodule management
   - Auto-initialization
   - Branch tracking and update strategy configuration
   - Pre-operation validation
   - Nested submodule handling

2. **Backup System**
   - Backup .gitmodules and git index before operations
   - Backup parent repository state
   - Store backups with timestamps
   - Automatic backup cleanup

3. **Rollback Capability**
   - Detect operation failures
   - Automatic rollback to pre-operation state
   - Restore .gitmodules and git index
   - Clear error messages about what was rolled back

4. **Recursive Chain Handling**
   - Add all repositories in chain as submodules in correct order
   - Handle arbitrary depth nesting
   - Proper parent-child relationship management
   - Depth-first processing

5. **Dependency Resolution**
   - Ensure parent repository exists before adding child
   - Create missing parent repositories automatically
   - Validate entire chain before starting operations
   - Handle circular dependency detection

6. **Interactive Confirmation Mode**
   - Display planned operations before execution
   - Ask for user confirmation
   - Dry-run mode to see what would happen
   - Verbose logging option

7. **Advanced Error Handling**
   - Comprehensive error messages
   - Recovery suggestions
   - Partial operation support
   - Graceful degradation

### Implementation Architecture

```
add-repo-with-submodule/
├── __init__.py
├── __main__.py
├── add_repo_submodule.py
├── submodule_operations.py
├── validation.py
├── configuration.py
├── backup_manager.py            # NEW: Backup and restore
├── rollback_handler.py          # NEW: Rollback operations
├── dependency_resolver.py       # NEW: Dependency resolution
├── interactive_mode.py          # NEW: Interactive confirmations
├── exceptions.py                # NEW: Custom exceptions
├── cli.py
├── test_add_repo_submodule.py
├── test_validation.py
├── test_backup_manager.py       # NEW: Backup tests
├── test_rollback_handler.py     # NEW: Rollback tests
├── test_dependency_resolver.py  # NEW: Dependency tests
└── README.md
```

### Key Functions to Add

```python
# backup_manager.py
class BackupManager:
    """Manage backups and restores."""
    
    def create_backup(self, repo_path: Path) -> str:
        """Create backup of repository state."""
    
    def restore_backup(self, backup_id: str) -> bool:
        """Restore from backup."""
    
    def cleanup_old_backups(self, days: int = 7) -> None:
        """Remove old backups."""

# rollback_handler.py
class RollbackHandler:
    """Handle operation rollbacks."""
    
    def register_operation(self, operation: str, data: dict) -> None:
        """Register an operation for potential rollback."""
    
    def rollback(self) -> bool:
        """Rollback all registered operations."""

# dependency_resolver.py
class DependencyResolver:
    """Resolve repository dependencies."""
    
    def resolve_chain(self, chain: List[str]) -> List[Tuple[str, str]]:
        """Resolve parent-child relationships."""
    
    def validate_dependencies(self, chain: List[str]) -> bool:
        """Validate all dependencies can be satisfied."""

# interactive_mode.py
def confirm_operations(operations: List[dict]) -> bool:
    """Display operations and get user confirmation."""

def dry_run_mode(operations: List[dict]) -> None:
    """Show what would happen without executing."""
```

## Alternatives Considered
- **Option 1 Only**: Too basic for complex scenarios
  - Rejected: Insufficient for production use
- **Option 2 Only**: Good but lacks safety features
  - Rejected: No backup/rollback for critical operations
- **Manual Backup**: Require users to backup manually
  - Rejected: Error-prone, users forget

## Target Platform Considerations
How this feature works with:
- **OS**: Windows - Full git command compatibility, Windows path handling
- **GPU**: NVIDIA RTX 5090 - Not applicable
- **CPU**: AMD Ryzen - Not applicable
- **RAM**: 64GB - Not applicable

## Use Case

### Scenario 1: Safe Operation with Backup
```bash
python -m add_repo_with_submodule PrismQ.Critical.Production.Module

# Output:
# 📦 Creating backup of PrismQ...
# ✅ Backup created: backup_20251017_084530
# 🔍 Validating dependencies...
# ✅ All dependencies satisfied
# ✅ Repository created
# ✅ Added as submodule
# ✅ Initialized and configured
# ✅ Committed changes
# 💾 Backup can be restored with: --restore backup_20251017_084530
```

### Scenario 2: Automatic Rollback on Failure
```bash
python -m add_repo_with_submodule PrismQ.A.B.C

# Output:
# 📦 Creating backup...
# ✅ PrismQ.A added successfully
# ✅ PrismQ.A.B added successfully
# ❌ Failed to add PrismQ.A.B.C: Network error
# ⏪ Rolling back operations...
# ✅ Removed PrismQ.A.B
# ✅ Removed PrismQ.A
# ✅ Restored to backup_20251017_084530
# ❌ Operation cancelled, no changes made
```

### Scenario 3: Interactive Confirmation Mode
```bash
python -m add_repo_with_submodule --interactive PrismQ.A.B.C

# Output:
# Planned operations:
# 1. Create PrismQ.A at Nomoos/PrismQ.A
# 2. Clone to: /workspace/mod/A
# 3. Add as submodule in PrismQ
# 4. Create PrismQ.A.B at Nomoos/PrismQ.A.B
# 5. Clone to: /workspace/mod/A/mod/B
# 6. Add as submodule in PrismQ.A
# 7. Create PrismQ.A.B.C at Nomoos/PrismQ.A.B.C
# 8. Clone to: /workspace/mod/A/mod/B/mod/C
# 9. Add as submodule in PrismQ.A.B
# 
# Proceed with these operations? [y/N]: y
# ✅ Operations completed successfully
```

### Scenario 4: Dry Run Mode
```bash
python -m add_repo_with_submodule --dry-run PrismQ.Complex.Chain

# Output:
# [DRY RUN] Would create PrismQ.Complex
# [DRY RUN] Would add as submodule in PrismQ
# [DRY RUN] Would create PrismQ.Complex.Chain
# [DRY RUN] Would add as submodule in PrismQ.Complex
# [DRY RUN] No changes made (dry run mode)
```

## Additional Context

### Benefits Over Options 1 and 2
- **Safety**: Backup before every operation
- **Recovery**: Automatic rollback on failure
- **Confidence**: Dry-run and interactive modes
- **Reliability**: Production-ready error handling
- **Complexity**: Handles any nested scenario

### Inspired By
- `submodule-converter` architecture (already in PrismQ)
- SOLID principles with proper separation of concerns
- Git's own operation model (backup, rollback)

### Testing Requirements
- Unit tests for all new modules
- Integration tests for complete workflows
- Failure scenario tests (rollback validation)
- Performance tests for deep nesting
- Edge case tests (circular deps, conflicts)

### Performance Considerations
- Backup creation overhead (~1-2 seconds)
- Rollback time depends on operation count
- Dependency resolution is O(n²) worst case
- Can handle chains of 10+ levels efficiently

## Dependencies
- Requires Options 1 and 2 to be implemented first
- Uses existing repo-builder and submodule-converter patterns
- No new external dependencies
- Leverages existing backup_manager patterns from submodule-converter

## Priority
- [ ] High - Critical for functionality
- [ ] Medium - Important but not critical
- [x] Low - Nice to have (can use Options 1 and 2 for most scenarios)

## Estimated Complexity
- **Complexity**: High
- **Timeline**: 4-6 hours implementation
- **Risk**: Higher (many moving parts, complex interactions)

## Implementation Checklist
- [ ] Create backup_manager.py module (can reuse patterns from submodule-converter)
- [ ] Create rollback_handler.py module
- [ ] Create dependency_resolver.py module
- [ ] Create interactive_mode.py module
- [ ] Create exceptions.py with custom exception hierarchy
- [ ] Implement backup/restore functionality
- [ ] Implement automatic rollback on failure
- [ ] Implement dependency resolution
- [ ] Add interactive confirmation mode
- [ ] Add dry-run mode
- [ ] Add verbose logging option
- [ ] Write comprehensive tests for all scenarios
- [ ] Update documentation
- [ ] Manual testing with complex nested structures
- [ ] Performance testing

## Related Issues
- Depends on: Option 1 implementation
- Depends on: Option 2 implementation
- Can leverage: submodule-converter backup patterns

## Notes
This is an advanced feature that may not be needed immediately. Options 1 and 2 cover most use cases. Implement this only if:
- Complex nested structures become common
- Safety/rollback becomes critical requirement
- Interactive mode is requested by users
- Production deployment needs highest reliability
