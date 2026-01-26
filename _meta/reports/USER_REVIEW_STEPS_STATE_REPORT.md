# User Review Steps/Scripts - Current State Report

**Generated:** 2026-01-26  
**Purpose:** Document the current state of user review steps, scripts, and processes in PrismQ

---

## Executive Summary

PrismQ has a comprehensive review infrastructure spanning:
- **Code Review**: PR checklist with 8 verification categories
- **Content Review**: 13+ review modules for quality assurance
- **User Scripts**: 59 batch scripts for running workflows
- **Interactive Workflows**: Python-based continuous processing

**Overall Status:** ✅ Well-structured with documented issues to address

---

## 1. Code Review Process (Pull Requests)

### Location
`_meta/docs/guidelines/PR_CODE_REVIEW_CHECKLIST.md`

### Structure
Comprehensive 8-category checklist for PR review:

1. **Merge & Stability** - Build, run, and test verification
2. **Module Responsibility & Layering** - Correct abstraction levels
3. **Namespace & Structure Consistency** - Hierarchy alignment
4. **Module Layout** - src/ and _meta/ convention
5. **Design & Maintainability** - Clear responsibilities, extensibility
6. **Configuration & Side Effects** - No import-time side effects
7. **Testability** - Isolated testing, explicit dependencies
8. **Final Gate** - Architecture cleanliness verification

### Status
✅ **Fully documented and referenced in GitHub Copilot instructions**

### Example Verification Pattern
```
- Database config: Lazy loading, no side effects at import ✓
- AI config: Lazy loading (requests imported only when needed) ✓
- Composition root pattern: create_database_config, create_ai_config ✓
```

---

## 2. User-Facing Scripts

### Location
`_meta/scripts/` (31 directories, 59 scripts total)

### Script Types

#### Run.bat (Production Mode)
- Saves content to database
- Continuous mode (1ms delay between runs)
- Automatic Ollama startup
- Virtual environment setup
- Example: `03_PrismQ.T.Title.From.Idea/Run.bat`

#### Preview.bat (Testing Mode)
- Does NOT save to database
- Used for testing and validation
- Same environment setup as Run.bat
- Includes debug mode
- Example: `07_PrismQ.T.Review.Title.From.Content/Preview.bat`

### Script Organization (by workflow stage)

| Stage | Module | Purpose | Status |
|-------|--------|---------|--------|
| 01 | PrismQ.T.Idea.From.User | Capture user ideas | ✅ Active |
| 02 | PrismQ.T.Story.From.Idea | Generate story structure | ✅ Active |
| 03 | PrismQ.T.Title.From.Idea | Create titles | ✅ Active |
| 04 | PrismQ.T.Content.From.Idea.Title | Generate content | ✅ Active |
| 05-10 | PrismQ.T.Review.* | Title & content review loops | ✅ Active |
| 11-17 | PrismQ.T.Review.* | Quality review dimensions | ✅ Active |
| 18-19 | PrismQ.T.Story.* | Story review & polish | ✅ Active |
| 20 | PrismQ.T.Publishing | Publishing preparation | ✅ Active |
| 21-24 | PrismQ.A.* | Audio generation | ✅ Active |
| 26-28 | PrismQ.V.* | Video generation | ✅ Active |
| 30 | PrismQ.M.Analytics | Analytics tracking | ✅ Active |

### Common Utilities

#### start_ollama.bat
**Location:** `_meta/scripts/common/start_ollama.bat`

**Purpose:**
- Check if Ollama service is running
- Start Ollama if not running
- Verify model availability (qwen2.5:14b-instruct)
- Used by all AI-powered scripts

**Status:** ✅ Active and functional

### Script Structure Pattern

All scripts follow a consistent pattern:

```batch
@echo off
REM Header with module name and purpose

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Start required services (e.g., Ollama)
call ..\common\start_ollama.bat

REM Setup Python virtual environment
call :setup_env

REM Run the Python module
python ..\..\..\<module_path>\src\<script>.py [options]

:setup_env
REM Create venv if needed
REM Install requirements
REM Activate environment
```

---

## 3. Content Review Modules

### Location
`T/Review/` with comprehensive submodule structure

### Review Module Hierarchy

#### Implemented Modules ✅

**Title Review (T/Review/Title/)**
- `ByScriptAndIdea/` - Stage 4 (MVP-004)
- Full implementation with 21 passing tests
- Dual alignment scoring (script + idea)
- 8 review categories
- Prioritized improvement recommendations
- Version tracking (v1, v2, v3+)

**Script Review (T/Review/Script/)**
- Stage 5, 10, 13 review loops
- Overall and category-specific scoring (0-100%)
- YouTube short optimization
- Prioritized improvement points

#### Planned Modules 📋

| Module | Stage | Purpose | Status |
|--------|-------|---------|--------|
| Grammar | 14 | Grammar & syntax corrections | Placeholder only |
| Tone | 15 | Emotional tone & voice consistency | Placeholder only |
| Content | 16 | Narrative coherence & accuracy | Placeholder only |
| Consistency | 17 | Internal continuity & logic | Placeholder only |
| Editing | 18 | Clarity, flow, readability | Placeholder only |
| Readability | 19-20 | Voiceover suitability | Placeholder only |

### Review Loop Pattern

```
Content v1 → Review → Feedback
    ↓
Content v2 → Review → Validation
    ↓
Acceptance Gate → Next Stage
```

Each review stage can loop back to refinement if quality gates not met.

---

## 4. Interactive Review Workflows

### Python Workflow Runners

**Location:** `*/src/*_interactive.py` or `*/src/*_workflow.py`

**Examples:**
- `T/Review/Title/From/Content/src/review_title_from_script_workflow.py`
- `T/Review/Script/From/Title/src/review_script_from_title_interactive.py`
- `T/Review/Title/From/Idea/Content/src/review_title_by_idea_content_interactive.py`

### Features

**Continuous Processing:**
- Monitors database for content needing review
- Dynamic wait intervals (30s when idle, shorter when busy)
- Processes items automatically

**Mode Support:**
- Production mode: Saves to database
- Preview mode: Testing only (--preview flag)
- Debug mode: Detailed logging (--debug flag)

**Example Usage:**
```bash
# Production mode (continuous, saves to DB)
python review_title_from_script_workflow.py

# Preview mode (no DB save)
python review_title_from_script_workflow.py --preview

# With debug logging
python review_title_from_script_workflow.py --preview --debug
```

### Workflow Integration

**Stage 4 Example (Title Review):**
1. User runs `05_PrismQ.T.Review.Title.From.Content.Idea/Run.bat`
2. Script starts Ollama
3. Python workflow runner processes Story objects needing title review
4. Reviews saved to database
5. Continues monitoring for new stories

---

## 5. Workflow Documentation

### Core Documentation

**Main Index:** `_meta/WORKFLOW.md`

**Detailed Documentation:**
- `_meta/docs/workflow/state-machine.md` - Complete state diagram
- `_meta/docs/workflow/phases.md` - 9 production phases
- `_meta/docs/workflow/mvp-stages.md` - All 26 MVP stages
- `_meta/docs/workflow/transitions.md` - State transition rules
- `_meta/docs/STATE_TRANSITIONS_REPORT.md` - Comprehensive transitions report

### MVP Workflow (26 Stages)

**Phase 1: Idea & Story (Stages 1-2)**
- Stage 1: Capture user ideas
- Stage 2: Generate story structure

**Phase 2: Initial Title & Script (Stages 3-4)**
- Stage 3: Create title v1
- Stage 4: Generate script v1

**Phase 3: Review & Iteration (Stages 5-13)**
- Stages 5, 7, 10: Title review loops
- Stages 6, 8, 11: Script review loops
- Stages 12-13: Acceptance gates

**Phase 4: Quality Reviews (Stages 14-20)**
- Grammar, Tone, Content, Consistency, Editing, Readability

**Phase 5: Publishing (Stage 23)**
- Content finalization and publishing

**Phase 6-8: Audio & Video (Stages 21-28)**
- Audio generation and processing
- Video scene and keyframe creation

**Phase 9: Distribution & Analytics (Stages 29-30)**
- Multi-platform publishing
- Performance tracking

---

## 6. Known Issues & Compliance

### Script Compliance Audit

**Report:** `_meta/docs/guidelines/SCRIPT_COMPLIANCE_AUDIT.md`

**Date:** 2025-12-23

### Identified Issues

#### ISSUE-001: Incorrect Script Directory Naming
**Severity:** Medium  
**Problem:** Directory `04_PrismQ.T.Content.From.Title.Idea` uses deprecated namespace  
**Correct:** Should be `04_PrismQ.T.Content.From.Idea.Title`  
**Impact:** Naming doesn't align with documented architecture

#### ISSUE-002: Deprecated Module Path References
**Severity:** Medium  
**Problem:** Some scripts reference old paths (`T\Script\` instead of `T\Content\`)  
**Files:** Various Run.bat files  
**Impact:** May cause path resolution issues

#### ISSUE-003-004: Incorrect Header Comments
**Severity:** Low  
**Problem:** Header comments don't match corrected namespace  
**Impact:** Documentation inconsistency

#### ISSUE-005-015: Review Module Script Naming
**Severity:** Low  
**Problem:** Mixed conventions in review scripts (05-17)  
**Analysis:** Need to verify if Review operations are domain operations or content pipelines

#### ISSUE-016: Story Module Script Verification
**Severity:** Low  
**Problem:** Uncertain if Story scripts belong to domain or content namespace  
**Directories:** 02, 18, 19

### Compliance Status

**Total Scripts Audited:** 63 .bat files  
**Violations Found:** 4 categories  
**Severity:** Medium - Naming inconsistencies  
**Priority:** Medium - Should be addressed for consistency

---

## 7. Review Data Models

### Title Review Data Model

**Location:** `T/Review/Title/ByScriptAndIdea/`

**Core Classes:**
```python
TitleReview
├── title_id: str
├── title_text: str
├── title_version: str
├── overall_score: int (0-100)
├── script_alignment_score: int
├── idea_alignment_score: int
├── engagement_score: int
├── categories: List[TitleReviewCategory]
├── improvement_points: List[TitleImprovementPoint]
└── seo_recommendations: List[str]

TitleReviewCategory
├── category: str
├── score: int (0-100)
├── strengths: List[str]
└── weaknesses: List[str]

TitleImprovementPoint
├── title: str
├── description: str
├── priority: str (high/medium/low)
└── impact_score: int (0-100)
```

**Features:**
- Serialization support (to_dict/from_dict)
- High-priority improvement filtering
- Ready-for-improvement validation
- Version tracking support

### Testing

**Status:** ✅ All 21 tests passing

**Test Coverage:**
- Data model creation and validation
- Serialization/deserialization
- Score calculations
- Priority filtering
- Workflow integration

---

## 8. Environment Setup

### Prerequisites

**Required:**
- Python 3.8+
- Ollama with qwen2.5:14b-instruct model
- SQLite database (db.s3db)

**Automatic Setup (via scripts):**
- Virtual environment creation
- Dependency installation
- Service startup (Ollama)

### Database Configuration

**Location:** Single shared database

**Path:**
- Default: `C:/PrismQ/db.s3db`
- Configurable via command-line arguments
- Used by ALL modules (Text, Audio, Video)

**Schema:**
- Idea, Story, Title, Content tables
- Publishing, Analytics tables
- All in ONE database (critical design decision)

---

## 9. Usage Examples

### Running a Review Script

```bash
# Navigate to script directory
cd _meta/scripts/07_PrismQ.T.Review.Title.From.Content

# Test mode (no database save)
Preview.bat

# Production mode (saves to database)
Run.bat

# With custom database path
Run.bat "D:\custom\path\db.s3db"
```

### Using Review API in Code

```python
from T.Review.Title.ByScriptAndIdea import (
    TitleReview,
    TitleReviewCategory,
    TitleImprovementPoint
)

# Create a review
review = TitleReview(
    title_id="title-001",
    title_text="The Echo - A Haunting Discovery",
    title_version="v1",
    overall_score=78,
    script_id="script-001",
    script_alignment_score=85,
    idea_id="idea-001",
    idea_alignment_score=82
)

# Check readiness for improvement
if review.is_ready_for_improvement():
    print("Ready for Stage 6: Title Improvements v2")
    
# Get high-priority improvements
improvements = review.get_high_priority_improvements()
for imp in improvements:
    print(f"{imp.title}: {imp.description}")
```

---

## 10. Recommendations

### Immediate Actions (Priority: High)

1. **Address ISSUE-001**
   - Rename `04_PrismQ.T.Content.From.Title.Idea` → `04_PrismQ.T.Content.From.Idea.Title`
   - Update all path references
   - Update header comments

2. **Verify Review Module Classification (ISSUE-005-015)**
   - Determine if Review operations are domain or content
   - Standardize naming accordingly
   - Update documentation

### Medium Priority

3. **Complete Planned Review Modules**
   - Implement Grammar (Stage 14)
   - Implement Tone (Stage 15)
   - Implement Content (Stage 16)
   - Implement Consistency (Stage 17)
   - Implement Editing (Stage 18)
   - Implement Readability (Stages 19-20)

4. **Create Script Templates**
   - Standardized Run.bat template
   - Standardized Preview.bat template
   - Automated compliance checking

### Long-term Improvements

5. **Automated Compliance Checking**
   - Script to validate naming conventions
   - Pre-commit hooks for compliance
   - CI/CD integration

6. **Enhanced Documentation**
   - User guide for running scripts
   - Troubleshooting guide
   - Video tutorials

7. **Web UI Integration**
   - Review dashboard in Client module
   - Visual workflow tracking
   - Manual review interface

---

## 11. Related Documentation

### Essential Reading

- **[PR Review Checklist](_meta/docs/guidelines/PR_CODE_REVIEW_CHECKLIST.md)** - PR verification standards
- **[Coding Guidelines](_meta/docs/guidelines/CODING_GUIDELINES.md)** - Module hierarchy and placement
- **[Module Hierarchy](_meta/docs/guidelines/MODULE_HIERARCHY_UPDATED.md)** - Detailed hierarchy rules
- **[Script Compliance Audit](_meta/docs/guidelines/SCRIPT_COMPLIANCE_AUDIT.md)** - Known script issues
- **[Workflow Documentation](_meta/WORKFLOW.md)** - Complete workflow guide
- **[T/Review README](T/Review/README.md)** - Review module documentation

### Module-Specific

- **[T/Review/Title/ByScriptAndIdea/README.md](T/Review/Title/ByScriptAndIdea/README.md)** - Title review implementation
- **[T/Review/Script/README.md](T/Review/Script/README.md)** - Script review implementation

---

## 12. Conclusion

### Summary

PrismQ has a **well-structured and comprehensive review infrastructure** with:
- Clear code review guidelines for PRs
- Extensive user-facing scripts for workflow execution
- Comprehensive content review modules
- Interactive Python workflows for continuous processing
- Detailed documentation and testing

### Current State: ✅ Functional with Room for Improvement

**Strengths:**
- Comprehensive PR review checklist
- 59 user-facing scripts covering entire workflow
- Well-documented review modules
- Consistent script structure and patterns
- Automated environment setup

**Areas for Improvement:**
- Naming inconsistencies to address (4-5 issues)
- Several review modules still in placeholder status
- Need for automated compliance checking
- Potential for web UI integration

### Next Steps

If action is required based on this investigation:
1. Address naming inconsistencies per audit report
2. Prioritize implementation of planned review modules
3. Create automated compliance checking
4. Consider web UI for manual review processes

---

**Report Status:** ✅ Complete  
**Last Updated:** 2026-01-26  
**Next Review:** After addressing compliance issues
