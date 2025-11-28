# POST-010: T.Script.Versioning - Version History & Rollback

**Type**: Post-MVP Enhancement  
**Worker**: Worker06 (Database Specialist)  
**Priority**: High  
**Effort**: 2 days  
**Module**: `PrismQ.T.Script.Versioning`  
**Sprint**: Sprint 5 (Weeks 11-12)  
**Status**: 🎯 PLANNED

---

## Description

Complete version history tracking with ability to view and rollback to previous script versions.

---

## Acceptance Criteria

- [ ] Store all script versions (v1, v2, v3, v4+) with full content
- [ ] Track version metadata (timestamp, author, change description)
- [ ] Implement version diff/comparison (side-by-side, unified)
- [ ] Enable rollback to any previous version
- [ ] Version branching support (create alternate versions)
- [ ] Efficient storage using delta compression
- [ ] Search version history
- [ ] Export version history report

---

## Input/Output

**Input**:
- Script ID
- Version number (optional, defaults to latest)

**Output**:
- Version history list
- Full script content for selected version
- Diff between versions
- Version metadata

---

## Dependencies

- **MVP-003**: T.Script.FromIdeaAndTitle
- **MVP-006**: T.Title.From.Title.Review.Script
- **MVP-007**: T.Script.FromOriginalScriptAndReviewAndTitle

---

## Technical Notes

### Database Schema
```sql
CREATE TABLE script_versions (
    id INTEGER PRIMARY KEY,
    script_id TEXT,
    version_number INTEGER,
    content TEXT,
    content_hash TEXT,
    delta_from_previous TEXT,  -- For compression
    author TEXT,
    change_description TEXT,
    created_at TIMESTAMP,
    UNIQUE(script_id, version_number)
);

CREATE INDEX idx_script_versions_lookup 
ON script_versions(script_id, version_number DESC);
```

### Delta Compression
```python
import difflib

def store_delta(previous_content: str, new_content: str) -> str:
    """Store only the differences to save space."""
    differ = difflib.Differ()
    delta = list(differ.compare(
        previous_content.splitlines(),
        new_content.splitlines()
    ))
    return '\n'.join(delta)
```

### Files to Create
- `T/Script/Versioning/version_manager.py` (new)
- `T/Script/Versioning/diff_generator.py` (new)
- `T/Script/Versioning/rollback_handler.py` (new)

---

## Success Metrics

- Storage efficiency: >60% space saved with delta compression
- Diff generation time: <1 second
- Rollback time: <2 seconds
- Version retrieval accuracy: 100%

---

**Created**: 2025-11-23  
**Owner**: Worker06 (Database Specialist)
