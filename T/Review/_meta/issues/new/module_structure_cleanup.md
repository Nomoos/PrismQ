# Module Structure Cleanup Plan

## Issue: T/Review Namespace Structure Analysis

The `T/Review` namespace needs clarification. After deep analysis, we found the structure is **intentionally layered**:
- **Parent-level modules** (e.g., `T/Review/Grammar/`) = **Data Models** (shared classes)
- **Script/Title submodules** (e.g., `T/Review/Script/Grammar/`) = **Services** (workflow processors)

## Analysis Summary

### Official Workflow States (from `T/State/constants/state_names.py`)

| State Name | Service Module Path |
|------------|---------------------|
| `PrismQ.T.Review.Script.Grammar` | `T/Review/Script/Grammar/` |
| `PrismQ.T.Review.Script.Tone` | `T/Review/Script/Tone/` |
| `PrismQ.T.Review.Script.Content` | `T/Review/Script/Content/` |
| `PrismQ.T.Review.Script.Consistency` | `T/Review/Script/Consistency/` |
| `PrismQ.T.Review.Script.Editing` | `T/Review/Script/Editing/` |
| `PrismQ.T.Review.Script.Readability` | `T/Review/Script/Readability/` |
| `PrismQ.T.Review.Title.Readability` | `T/Review/Title/Readability/` |
| `PrismQ.T.Review.Title.From.Script` | `T/Review/Title/From/Script/` |
| `PrismQ.T.Review.Title.From.Script.Idea` | `T/Review/Title/From/Script/Idea/` |
| `PrismQ.T.Review.Script.From.Title` | `T/Review/Script/From/Title/` |
| `PrismQ.T.Review.Script.From.Title.Idea` | `T/Review/Script/From/Title/Idea/` |

### Module Categories

#### 📦 Data Model Modules (Shared Libraries)
These modules contain **dataclasses** and **enums** that are imported by service modules:

| Module Path | Contains | Used By |
|-------------|----------|---------|
| `T/Review/Grammar/` | `GrammarReview`, `GrammarIssue`, `GrammarSeverity` | `T/Review/Script/Grammar/` |
| `T/Review/Tone/` | `ToneReview`, `ToneIssue`, `ToneSeverity` | `T/Review/Script/Tone/` |
| `T/Review/Content/` | `ContentReview`, `ContentIssue`, `ContentSeverity` | `T/Review/Script/Content/` |
| `T/Review/Consistency/` | `ConsistencyReview`, `ConsistencyIssue`, `ConsistencySeverity` | `T/Review/Script/Consistency/` |
| `T/Review/Editing/` | `EditingReview`, `EditingIssue`, `EditingSeverity` | `T/Review/Script/Editing/` |
| `T/Review/Readability/` | `TitleReadabilityReview`, `ReadabilityIssue`, `ReadabilitySeverity` | `T/Review/Title/Readability/` |
| `T/Review/Model/` | `Review`, `StoryReview`, `ReviewType` | Various services |

**Status**: ✅ KEEP - These are intentional shared libraries

#### ⚙️ Service Modules (Workflow Processors)
These modules contain **services** that process Stories through workflow states:

| Module Path | State | Status |
|-------------|-------|--------|
| `T/Review/Script/Grammar/` | `PrismQ.T.Review.Script.Grammar` | ✅ OK |
| `T/Review/Script/Tone/` | `PrismQ.T.Review.Script.Tone` | ✅ OK |
| `T/Review/Script/Content/` | `PrismQ.T.Review.Script.Content` | ✅ OK |
| `T/Review/Script/Consistency/` | `PrismQ.T.Review.Script.Consistency` | ✅ OK |
| `T/Review/Script/Editing/` | `PrismQ.T.Review.Script.Editing` | ✅ OK |
| `T/Review/Script/Readability/` | `PrismQ.T.Review.Script.Readability` | ✅ OK |
| `T/Review/Title/Readability/` | `PrismQ.T.Review.Title.Readability` | ✅ OK |
| `T/Review/Title/From/Script/` | `PrismQ.T.Review.Title.From.Script` | ✅ OK |
| `T/Review/Title/From/Script/Idea/` | `PrismQ.T.Review.Title.From.Script.Idea` | ✅ OK |
| `T/Review/Script/From/Title/` | `PrismQ.T.Review.Script.From.Title` | ✅ OK |
| `T/Review/Script/From/Title/Idea/` | `PrismQ.T.Review.Script.From.Title.Idea` | ✅ OK |

**Status**: ✅ KEEP - These match workflow states

#### ⚠️ Utility Modules (Non-State)
These don't correspond to workflow states but provide utility:

| Module Path | Purpose | Status |
|-------------|---------|--------|
| `T/Review/Script/Acceptance/` | Acceptance checking utility | ⚠️ Consider integrating into services |
| `T/Review/Title/Acceptance/` | Acceptance checking utility | ⚠️ Consider integrating into services |

#### ⚠️ Files in Non-Standard Locations

| File | Current Location | Issue |
|------|-----------------|-------|
| `T/Review/Script/script_review.py` | Parent of submodules | Should be in a submodule |
| `T/Review/Script/by_title_and_idea.py` | Parent of submodules | Should be in submodule |

---

## Current Architecture (CORRECT)

```
T/Review/
├── __init__.py                    # Unified: ReviewSeverity, pick_story_by_module
│
├── Grammar/                       # DATA MODEL (shared library)
│   └── grammar_review.py          # GrammarReview, GrammarIssue, GrammarSeverity
├── Tone/                          # DATA MODEL (shared library)
│   └── tone_review.py             # ToneReview, ToneIssue, ToneSeverity
├── Content/                       # DATA MODEL (shared library)
│   └── content_review.py          # ContentReview, ContentIssue, ContentSeverity
├── Consistency/                   # DATA MODEL (shared library)
│   └── consistency_review.py      # ConsistencyReview, ConsistencyIssue
├── Editing/                       # DATA MODEL (shared library)
│   └── editing_review.py          # EditingReview, EditingIssue
├── Readability/                   # DATA MODEL (shared library)
│   └── title_readability_review.py# TitleReadabilityReview, ReadabilityIssue
├── Model/                         # DATA MODEL (core review)
│   └── src/review.py              # Review, StoryReview
│
├── Script/                        # SERVICES for Script Reviews
│   ├── Grammar/                   # PrismQ.T.Review.Script.Grammar
│   ├── Tone/                      # PrismQ.T.Review.Script.Tone
│   ├── Content/                   # PrismQ.T.Review.Script.Content
│   ├── Consistency/               # PrismQ.T.Review.Script.Consistency
│   ├── Editing/                   # PrismQ.T.Review.Script.Editing
│   ├── Readability/               # PrismQ.T.Review.Script.Readability
│   └── From/Title/                # PrismQ.T.Review.Script.From.Title
│       └── Idea/                  # PrismQ.T.Review.Script.From.Title.Idea
│
├── Title/                         # SERVICES for Title Reviews
│   ├── Readability/               # PrismQ.T.Review.Title.Readability
│   └── From/Script/               # PrismQ.T.Review.Title.From.Script
│       └── Idea/                  # PrismQ.T.Review.Title.From.Script.Idea
│
└── _meta/                         # Metadata, tests, docs
```

---

## Summary of Completed Unification

### ✅ Done
1. **Unified `ReviewSeverity` enum** - Added to `T/Review/__init__.py`
2. **Unified `pick_story_by_module()` function** - Pick stories by module/state name
3. **Unified `count_stories_by_module()` function** - Count stories by module/state name
4. **All child modules export `ReviewSeverity`** - Backward compatible

### ⚠️ Minor Issues (Low Priority)
1. `T/Review/Script/script_review.py` - Loose file in parent
2. `T/Review/Script/by_title_and_idea.py` - Loose file in parent
3. Acceptance modules could be integrated into services

## Conclusion

The T/Review structure is **intentionally layered** with:
- **Data Models** at parent level for reuse across multiple services
- **Services** at Script/Title submodule level matching workflow states
- **Unified components** (ReviewSeverity, pick_story_by_module) in `T/Review/__init__.py`

**No modules need to be deleted.** The structure is correct.
