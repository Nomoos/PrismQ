# Issue #012: Migrate YouTubePlugin to Worker (Optional/Legacy)

**Parent Issue**: #001 (YouTube Worker Refactor Master Plan)  
**Worker**: Worker 02 - Python Specialist  
**Language**: Python 3.10+  
**Status**: New  
**Priority**: Low (Optional)  
**Duration**: 1-2 days  
**Dependencies**: #002 (Worker Base Class), #005 (Plugin Architecture Refactor)

---

## Worker Details: Worker02 - Python Specialist

**Role**: Legacy Plugin Migration (Optional)  
**Expertise Required**:
- Python 3.10+
- YouTube API integration
- Worker pattern implementation

**Collaboration**:
- **Worker01** (PM): Confirm if this plugin is still needed
- **Worker02** (self): Build on existing patterns

**See**: `_meta/issues/new/Worker02/README.md` for complete role description

---

## Objective

**OPTIONAL**: Migrate the existing `youtube_plugin.py` (YouTube API-based plugin) to the worker pattern, if it's still in use. This plugin may be legacy/deprecated in favor of yt-dlp-based plugins.

---

## Problem Statement

There may be an existing `youtube_plugin.py` that uses the YouTube Data API v3 instead of yt-dlp. This plugin:
- May be deprecated/legacy
- May still be in use for API-based scraping
- Needs evaluation before migration

**Decision Required**: 
1. Is this plugin still actively used?
2. Should it be migrated or deprecated?
3. If migrated, follow the same pattern as #009, #010, #011

---

## SOLID Principles Analysis

(Same as other plugins - SRP, OCP, LSP, ISP, DIP all apply)

---

## Proposed Solution

### Option 1: Deprecate (Recommended if yt-dlp covers all use cases)

**Action**:
- Add deprecation warning
- Document migration path to yt-dlp plugins
- No worker migration needed

**File**: `Sources/Content/Shorts/YouTube/src/plugins/youtube_plugin.py`

```python
import warnings

class YouTubePlugin:
    """DEPRECATED: Use YouTubeChannelPlugin, YouTubeTrendingPlugin, 
    or YouTubeKeywordPlugin instead.
    
    This plugin used YouTube Data API v3 which has strict quota limits.
    The yt-dlp-based plugins are recommended for all use cases.
    """
    
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "YouTubePlugin is deprecated. Use yt-dlp-based plugins instead.",
            DeprecationWarning,
            stacklevel=2
        )
```

### Option 2: Migrate (If still needed)

Follow the same pattern as #009:
1. Extend `PluginBase`
2. Implement required methods
3. Keep YouTube API logic
4. Add worker integration
5. Test thoroughly

---

## Implementation Plan

### Step 1: Evaluate (Day 1, 2 hours)
- Check if plugin is used in production
- Review dependencies on YouTube API
- Consult with Worker01 (PM)
- Decision: Deprecate or Migrate

### Step 2: If Deprecate (Day 1, 2 hours)
- Add deprecation warnings
- Document migration path
- Update tests to skip deprecated plugin
- Update documentation

### Step 3: If Migrate (Day 1-2)
- Follow pattern from #009
- Implement `PluginBase` interface
- Test with YouTube API
- Ensure quota handling
- Document API key requirements

---

## Acceptance Criteria

### If Deprecated
- [ ] Deprecation warning added
- [ ] Migration guide documented
- [ ] Tests updated
- [ ] No breaking changes

### If Migrated
- [ ] Extends `PluginBase`
- [ ] All methods implemented
- [ ] YouTube API integration working
- [ ] Quota handling implemented
- [ ] Test coverage >80%

---

## Decision Matrix

| Factor | Deprecate | Migrate |
|--------|-----------|---------|
| Plugin used? | No | Yes |
| API quota available? | N/A | Yes |
| yt-dlp covers use case? | Yes | No |
| Maintenance effort | Low | High |
| **Recommendation** | ✅ Yes | If needed |

---

## Files to Modify/Create

**If Deprecated**:
1. `Sources/Content/Shorts/YouTube/src/plugins/youtube_plugin.py` - Add deprecation

**If Migrated**:
1. `Sources/Content/Shorts/YouTube/src/plugins/youtube_plugin.py` - Refactor
2. `Sources/Content/Shorts/YouTube/_meta/tests/test_youtube_plugin.py` - Tests

---

## Dependencies

### Internal
- #002 (BaseWorker) - If migrating
- #005 (PluginBase) - If migrating

### External
- YouTube Data API v3 key - If migrating

---

## Estimated Effort

**1-2 days** (if migrating):
- Day 1: Evaluation and decision
- Day 2: Implementation (if needed)

**OR**

**2-4 hours** (if deprecating):
- Evaluation and deprecation

---

## Notes

### Recommendation

**Deprecate unless**:
1. There's a specific use case only YouTube API can handle
2. Quota is not an issue
3. There's active usage in production

**Reasons to deprecate**:
- yt-dlp is more flexible and has no quota limits
- Reduces maintenance burden
- One less dependency (no API key needed)
- #009, #010, #011 cover all major use cases

### If Deprecating

Provide migration guide:
```
# Old: YouTube API plugin
task = {
    'type': 'youtube_search',
    'parameters': {'query': 'python tutorial'}
}

# New: Keyword search plugin
task = {
    'type': 'keyword_search',
    'parameters': {'query': 'python tutorial', 'top_n': 50}
}
```

---

**Status**: 🤔 Requires Decision  
**Assignee**: Worker02 - Python Specialist  
**Estimated Start**: Week 3, Day 3 (after #011, if needed)  
**Estimated Completion**: Week 3, Day 4 (or mark as deprecated/skipped)
