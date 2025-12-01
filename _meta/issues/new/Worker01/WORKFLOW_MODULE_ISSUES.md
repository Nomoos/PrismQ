# Worker01 Suggested Issues for Workflow Implementation

**Role**: Scrum Master, Planner & Project Manager  
**Task**: Suggest issues for implementing workflow modules  
**Date**: 2025-12-01

---

## Module Implementation Issues

Below are the suggested issues for each workflow module. Each module has been implemented with:
- Interactive Python CLI with --preview and --debug modes
- Batch files for Windows (.bat) execution
- Shell scripts for Linux/macOS
- Own virtual environment setup

---

### ISSUE-001: PrismQ.T.Idea.Creation
**Status**: ✅ Implemented  
**Location**: `T/Idea/Creation/`  
**Scripts**: `_meta/scripts/01_Idea/`

**Description**:
Interactive idea creation module that processes user input (text, JSON, story snippets) and generates idea variants using template-based generation.

**Features Implemented**:
- Interactive CLI with multiline input support
- Preview mode for testing without database save
- Debug logging to file
- 10 variant generation with weighted random template selection
- JSON output option
- Colorized terminal output

**Acceptance Criteria**:
- [x] Interactive mode accepts text input
- [x] Preview mode available (--preview flag)
- [x] Debug mode available (--debug flag)
- [x] Own virtual environment created
- [x] Batch file for execution

---

### ISSUE-002: PrismQ.T.Title.From.Idea
**Status**: ✅ Implemented  
**Location**: `T/Title/From/Idea/`  
**Scripts**: `_meta/scripts/02_Title/`

**Description**:
Generate title variants from ideas. Takes Idea objects and generates 10 compelling title variants using different strategies (direct, question, how-to, curiosity, etc.).

**Features Implemented**:
- Interactive CLI accepting JSON or plain text ideas
- 10 title variant generation
- Score and keyword tracking per variant
- Preview mode for testing
- JSON output option

**Acceptance Criteria**:
- [x] Generate 10 title variants from idea
- [x] Each variant has style, score, keywords
- [x] Preview mode available
- [x] Own virtual environment
- [x] Batch files for run and preview

---

### ISSUE-003: PrismQ.T.Script.From.Idea.Title
**Status**: ✅ Implemented  
**Location**: `T/Script/From/Idea/Title/`  
**Scripts**: `_meta/scripts/03_Script/`

**Description**:
Generate scripts from idea and title combination. Creates structured scripts with intro, body, conclusion sections.

**Features Implemented**:
- Interactive CLI for script generation
- Multiple structure types (hook_deliver_cta, three_act, etc.)
- Duration estimation
- Section breakdown with purpose and notes
- JSON output option

**Acceptance Criteria**:
- [x] Generate script from idea+title
- [x] Support multiple structure types
- [x] Preview mode available
- [x] Own virtual environment
- [x] Batch files for run and preview

---

### ISSUE-004: PrismQ.T.Review.Title.From.Script
**Status**: ✅ Implemented  
**Location**: `T/Review/Title/From/Script/`  
**Scripts**: `_meta/scripts/04_Review_Title/`

**Description**:
Review title against script for alignment, engagement, and SEO. Provides actionable improvement recommendations.

**Features Implemented**:
- Title-script alignment analysis
- Engagement score calculation
- SEO optimization analysis
- Improvement recommendations with priorities
- Overall assessment

**Acceptance Criteria**:
- [x] Analyze title-script alignment
- [x] Generate improvement recommendations
- [x] Preview mode available
- [x] Own virtual environment
- [x] Batch files for run and preview

---

### ISSUE-005: PrismQ.T.Review.Script.From.Title
**Status**: ✅ Implemented  
**Location**: `T/Review/Script/From/Title/`  
**Scripts**: `_meta/scripts/05_Review_Script/`

**Description**:
Review script against title for alignment and quality. Tracks improvements across versions.

**Features Implemented**:
- Script-title alignment analysis
- Category score breakdown
- Improvement recommendations
- Version comparison support
- Next steps generation

**Acceptance Criteria**:
- [x] Analyze script-title alignment
- [x] Generate improvement recommendations
- [x] Preview mode available
- [x] Own virtual environment
- [x] Batch files for run and preview

---

### ISSUE-006: PrismQ.T.Title.From.Script.Review.Title
**Status**: ✅ Implemented  
**Location**: `T/Title/From/Title/Review/Script/`  
**Scripts**: `_meta/scripts/06_Title_From_Review/`

**Description**:
Generate improved title versions based on review feedback. Takes original title, script, and reviews to generate improved v2/v3/etc.

**Features Implemented**:
- Title improvement from review feedback
- Version tracking (v1→v2→v3)
- Rationale generation
- Script alignment notes
- Engagement notes

**Acceptance Criteria**:
- [x] Generate improved title from reviews
- [x] Track version history
- [x] Preview mode available
- [x] Own virtual environment
- [x] Batch files for run and preview

---

### ISSUE-007: PrismQ.T.Script.From.Title.Review.Script
**Status**: ✅ Implemented  
**Location**: `T/Script/From/Title/Review/Script/`  
**Scripts**: `_meta/scripts/07_Script_From_Review/`

**Description**:
Generate improved script versions based on review feedback. Takes original script, title, and reviews to generate improved v2/v3/etc.

**Features Implemented**:
- Script improvement from review feedback
- Opening and conclusion enhancement
- Title alignment improvement
- Version tracking
- Structure notes

**Acceptance Criteria**:
- [x] Generate improved script from reviews
- [x] Track version history
- [x] Preview mode available
- [x] Own virtual environment
- [x] Batch files for run and preview

---

## Summary

All 7 workflow modules have been implemented with:
- ✅ Interactive Python CLI
- ✅ Preview mode (no database save)
- ✅ Debug logging support
- ✅ Own virtual environment
- ✅ Windows batch files (run + preview)
- ✅ Shell script environment setup

**Worker01 recommendation**: All modules are ready for Worker10 review and validation.

---

*Generated by Worker01 - Scrum Master, Planner & Project Manager*
