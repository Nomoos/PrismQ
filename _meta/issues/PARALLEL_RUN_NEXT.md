# PARALLEL_RUN_NEXT - Implementation Commands

> **Current Focus**: REVIEW-001 through REVIEW-007 (Stages 10-16 - Local AI Quality Reviews)  
> **Issue Specs**: See `T/WORKFLOW_DETAILED.md` for stage specifications

**Updated**: 2025-12-01 | **Sprint**: 5 - Local AI Quality Reviews

---

## 🎯 ACTIVE ISSUES

| Issue | Module | Stage | Effort | Status |
|-------|--------|-------|--------|--------|
| **REVIEW-001** | `T.Review.Script.Grammar` | Stage 10 | 2 days | 🔄 In Progress |
| **REVIEW-002** | `T.Review.Script.Tone` | Stage 11 | 2 days | 🔄 In Progress |
| **REVIEW-003** | `T.Review.Script.Content` | Stage 12 | 2 days | 🔄 In Progress |
| **REVIEW-004** | `T.Review.Script.Consistency` | Stage 13 | 2 days | 🔄 In Progress |
| **REVIEW-005** | `T.Review.Script.Editing` | Stage 14 | 2 days | 🔄 In Progress |
| **REVIEW-006** | `T.Review.Title.Readability` | Stage 15 | 2 days | 🔄 In Progress |
| **REVIEW-007** | `T.Review.Script.Readability` | Stage 16 | 2 days | 🔄 In Progress |

### Completed Issues

| Issue | Module | Stage | Status |
|-------|--------|-------|--------|
| **CORE-001** | `T.Title.From.Idea` | Stage 2 | ✅ Complete |
| **CORE-002** | `T.Script.FromIdeaAndTitle` | Stage 3 | ✅ Complete |

---

## 🚀 REVIEW-001: T.Review.Script.Grammar

### Implementation Commands

```bash
# === Step 1: Create Branch ===
cd /home/runner/work/PrismQ/PrismQ
git checkout -b review-001-script-grammar

# === Step 2: Navigate to Module ===
cd T/Review/Script/Grammar/

# === Step 3: Review Existing Implementation ===
cat src/script_grammar_service.py
cat README.md

# === Step 4: Run Existing Tests ===
cd /home/runner/work/PrismQ/PrismQ
python -m pytest T/Review/Script/Grammar/_meta/tests/ -v

# === Step 5: Implement Enhancements ===
# File: T/Review/Script/Grammar/script_grammar_service.py
# 
# Key Classes:
#   - ScriptGrammarReviewService: Main reviewer class
#   - Review: Output dataclass (id, text, score, created_at)
#   - StoryReview: Linking table for Story-Review relationship
#
# Review Criteria:
#   - Grammar correctness
#   - Spelling accuracy
#   - Punctuation usage
#   - Tense consistency

# === Step 6: Write/Update Tests ===
# File: T/Review/Script/Grammar/_meta/tests/test_script_grammar_service.py
#
# Test Cases:
#   - test_select_oldest_story_by_state
#   - test_create_review_with_score
#   - test_state_transition_on_pass
#   - test_state_transition_on_fail
#   - test_link_review_to_story

# === Step 7: Run Tests ===
python -m pytest T/Review/Script/Grammar/_meta/tests/ -v --cov=T/Review/Script/Grammar/src

# === Step 8: Update Documentation ===
# Update: T/Review/Script/Grammar/README.md

# === Step 9: Commit and Push ===
git add .
git commit -m "REVIEW-001: Implement T.Review.Script.Grammar module"
git push origin review-001-script-grammar
```

### Acceptance Criteria Checklist

```markdown
- [ ] Selects oldest Story where state is PrismQ.T.Review.Script.Grammar
- [ ] Creates Review with text and score (0-100)
- [ ] Links Review to Story via StoryReview table
- [ ] State transition: Pass (score >= 85) → PrismQ.T.Review.Script.Consistency
- [ ] State transition: Fail (score < 85) → PrismQ.T.Script.From.Title.Review.Script
- [ ] Unit tests achieve >80% coverage
```

---

## 🚀 REVIEW-002: T.Review.Script.Tone

### Implementation Commands

```bash
# === Step 1: Create Branch ===
cd /home/runner/work/PrismQ/PrismQ
git checkout -b review-002-script-tone

# === Step 2: Navigate to Module ===
cd T/Review/Script/Tone/

# === Step 3: Implement Module ===
# File: T/Review/Script/Tone/src/review_script_tone.py
#
# Key Functions:
#   - get_oldest_story_for_review(): Select oldest Story with correct state
#   - evaluate_script_tone(): Perform tone review
#   - create_review(): Create Review record
#   - determine_next_state(): State transition logic

# === Step 4: Run Tests ===
python -m pytest T/Review/Script/Tone/_meta/tests/ -v

# === Step 5: Commit and Push ===
git add .
git commit -m "REVIEW-002: Implement T.Review.Script.Tone module"
git push origin review-002-script-tone
```

### Acceptance Criteria Checklist

```markdown
- [ ] Selects oldest Story where state is PrismQ.T.Review.Script.Tone
- [ ] Creates Review with text and score (0-100)
- [ ] State transition: Pass → PrismQ.T.Review.Script.Content
- [ ] State transition: Fail → PrismQ.T.Script.From.Title.Review.Script
- [ ] Unit tests achieve >80% coverage
```

---

## 🚀 REVIEW-003 through REVIEW-007

Similar implementation pattern for remaining review stages:

| Issue | State Input | Pass State | Fail State |
|-------|-------------|------------|------------|
| **REVIEW-003** | Review.Script.Content | Review.Script.Consistency | Script.From.Title.Review.Script |
| **REVIEW-004** | Review.Script.Consistency | Review.Script.Editing | Script.From.Title.Review.Script |
| **REVIEW-005** | Review.Script.Editing | Review.Title.Readability | Script.From.Title.Review.Script |
| **REVIEW-006** | Review.Title.Readability | Review.Script.Readability | Title.From.Script.Review.Title |
| **REVIEW-007** | Review.Script.Readability | Story.Review | Script.From.Title.Review.Script |

---

## 📊 WORKFLOW POSITION

```
Stage 1: PrismQ.T.Idea.Creation ✅ COMPLETE
    ↓
Stage 1.5: PrismQ.T.Story.From.Idea ✅ COMPLETE
    ↓
Stage 2: T.Title.From.Idea ✅ COMPLETE (CORE-001)
    ↓
Stage 3: T.Script.FromIdeaAndTitle ✅ COMPLETE (CORE-002)
    ↓
Stages 4-9: Initial Review Cycles ✅ COMPLETE
    ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Local AI Quality Reviews ← CURRENT FOCUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ↓
Stage 10: T.Review.Script.Grammar ← REVIEW-001 (In Progress)
    ↓
Stage 11: T.Review.Script.Tone ← REVIEW-002 (In Progress)
    ↓
Stage 12: T.Review.Script.Content ← REVIEW-003 (In Progress)
    ↓
Stage 13: T.Review.Script.Consistency ← REVIEW-004 (In Progress)
    ↓
Stage 14: T.Review.Script.Editing ← REVIEW-005 (In Progress)
    ↓
Stage 15: T.Review.Title.Readability ← REVIEW-006 (In Progress)
    ↓
Stage 16: T.Review.Script.Readability ← REVIEW-007 (In Progress)
    ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stage 17-18: Story Review & Polish (Next Sprint)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📚 RELATED DOCUMENTATION

- **[T/WORKFLOW_DETAILED.md](../../T/WORKFLOW_DETAILED.md)** - Complete 18-stage workflow with all stages described
- **[T/WORKFLOW_STATE_MACHINE.md](../../T/WORKFLOW_STATE_MACHINE.md)** - Visual state machine diagram
- **[PARALLEL_RUN_NEXT_FULL.md](PARALLEL_RUN_NEXT_FULL.md)** - Complete POST-MVP roadmap
- **[new/CORE-001-Title-From-Idea.md](new/CORE-001-Title-From-Idea.md)** - CORE-001 specification (Complete)
- **[new/CORE-002-Script-FromIdeaAndTitle.md](new/CORE-002-Script-FromIdeaAndTitle.md)** - CORE-002 specification (Complete)

---

## 🔧 REVIEW OUTPUT MODEL

All review stages output the same Review model:

```sql
Review (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)
```

- **Title/Script** reference Review directly via FK
- **Story** references Review via **StoryReview** linking table
- Score >= 85 typically indicates acceptance (pass)
- Score < 85 indicates rejection (fail) and triggers refinement loop
