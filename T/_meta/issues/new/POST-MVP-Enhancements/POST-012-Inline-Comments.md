# POST-012: T.Review.Comments - Inline Comments & Annotations

**Type**: Post-MVP Enhancement  
**Worker**: Worker18 (Workflow Specialist)  
**Priority**: Medium  
**Effort**: 2 days  
**Module**: `PrismQ.T.Review.Comments`  
**Sprint**: Sprint 5 (Weeks 11-12)  
**Status**: 🎯 PLANNED

---

## Description

Add inline commenting system for precise feedback on specific text sections with threading and resolution tracking.

---

## Acceptance Criteria

- [ ] Comment on specific text ranges (line numbers, character positions)
- [ ] Support threaded discussions (reply to comments)
- [ ] Mark comments as resolved/unresolved
- [ ] Highlight commented sections in content view
- [ ] Export comments with content
- [ ] Comment history tracking
- [ ] Search comments by keyword/author
- [ ] Comment notifications

---

## Input/Output

**Input**:
- Content ID
- Comment position (start/end line or char offset)
- Comment text
- Parent comment ID (for threading)

**Output**:
- Annotated content with inline comments
- Comment thread structure
- Resolution status
- Comment statistics

---

## Dependencies

- **MVP-005**: T.Review.Script.ByTitleAndIdea
- **POST-011**: Multi-Reviewer Workflow (optional enhancement)

---

## Technical Notes

### Comment Data Model
```python
@dataclass
class InlineComment:
    comment_id: str
    content_id: str
    position: CommentPosition
    text: str
    author_id: str
    parent_comment_id: str = None  # For threading
    resolved: bool = False
    created_at: datetime
    resolved_at: datetime = None

@dataclass
class CommentPosition:
    start_line: int = None
    end_line: int = None
    start_char: int = None
    end_char: int = None
```

### Database Schema
```sql
CREATE TABLE inline_comments (
    id INTEGER PRIMARY KEY,
    comment_id TEXT UNIQUE,
    content_id TEXT,
    start_line INTEGER,
    end_line INTEGER,
    start_char INTEGER,
    end_char INTEGER,
    text TEXT,
    author_id TEXT,
    parent_comment_id TEXT,
    resolved BOOLEAN DEFAULT 0,
    created_at TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (parent_comment_id) REFERENCES inline_comments(comment_id)
);
```

### Files to Create
- `T/Review/Comments/comment_manager.py` (new)
- `T/Review/Comments/position_tracker.py` (new)
- `T/Review/Comments/thread_handler.py` (new)
- `T/Review/Comments/export_formatter.py` (new)

---

## Success Metrics

- Comment creation time: <500ms
- Thread depth support: Up to 5 levels
- Highlight rendering time: <1 second
- Export with comments: <3 seconds

---

**Created**: 2025-11-23  
**Owner**: Worker18 (Workflow Specialist)
