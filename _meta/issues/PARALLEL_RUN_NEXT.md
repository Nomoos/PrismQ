# PARALLEL_RUN_NEXT - Implementation Commands

> **Current Focus**: CORE-001 and CORE-002 (Stages 2-3 of Core Pipeline)  
> **Issue Specs**: `_meta/issues/new/CORE-001-Title-From-Idea.md` | `_meta/issues/new/CORE-002-Script-FromIdeaAndTitle.md`

**Updated**: 2025-11-30 | **Sprint**: 4 - Core Pipeline

---

## 🎯 ACTIVE ISSUES

| Issue | Module | Stage | Effort | Status |
|-------|--------|-------|--------|--------|
| **CORE-001** | `T.Title.From.Idea` | Stage 2 | 2 days | 🆕 Ready |
| **CORE-002** | `T.Script.FromIdeaAndTitle` | Stage 3 | 3 days | 🔒 Blocked by CORE-001 |

---

## 🚀 CORE-001: T.Title.From.Idea

### Implementation Commands

```bash
# === Step 1: Create Branch ===
cd /home/runner/work/PrismQ/PrismQ
git checkout -b core-001-title-from-idea

# === Step 2: Navigate to Module ===
cd T/Title/From/Idea/

# === Step 3: Review Existing Implementation ===
cat src/title_generator.py
cat README.md

# === Step 4: Run Existing Tests ===
cd /home/runner/work/PrismQ/PrismQ
python -m pytest T/Title/From/Idea/_meta/tests/ -v

# === Step 5: Implement Enhancements ===
# File: T/Title/From/Idea/src/title_generator.py
# 
# Key Classes:
#   - TitleGenerator: Main generator class
#   - TitleVariant: Output dataclass (text, style, length, keywords, score)
#   - TitleConfig: Configuration (num_variants, min/max_length, focus)
#
# 10 Generation Strategies:
#   1. direct      - Straightforward title
#   2. question    - Engaging question
#   3. how-to      - Action-oriented
#   4. curiosity   - Creates intrigue
#   5. authoritative - Expert perspective
#   6. listicle    - Number-based
#   7. problem-solution - Addresses challenges
#   8. comparison  - Contrasts approaches
#   9. ultimate-guide - Comprehensive
#   10. benefit    - Value proposition

# === Step 6: Write/Update Tests ===
# File: T/Title/From/Idea/_meta/tests/test_title_generator.py
#
# Test Cases:
#   - test_generate_10_variants_from_valid_idea
#   - test_handle_minimal_idea_data
#   - test_length_constraints_20_to_100_chars
#   - test_all_10_strategies_unique_output
#   - test_keyword_extraction_accuracy
#   - test_edge_cases_empty_idea_invalid_num

# === Step 7: Run Tests ===
python -m pytest T/Title/From/Idea/_meta/tests/ -v --cov=T/Title/From/Idea/src

# === Step 8: Integration Test with Idea.Creation ===
python -m pytest tests/test_integration.py -k "title" -v

# === Step 9: Update Documentation ===
# Update: T/Title/From/Idea/README.md

# === Step 10: Commit and Push ===
git add .
git commit -m "CORE-001: Enhance T.Title.From.Idea module"
git push origin core-001-title-from-idea
```

### Acceptance Criteria Checklist

```markdown
- [ ] Title generation produces 3-10 high-quality variants per idea
- [ ] Each variant uses a distinct generation strategy
- [ ] Generated titles meet length constraints (20-100 chars)
- [ ] Titles include relevant keywords from source idea
- [ ] Quality scores accurately reflect title engagement potential
- [ ] Module integrates with Idea.Creation output format
- [ ] Unit tests achieve >80% coverage
- [ ] Integration with Stage 3 (Script.FromIdeaAndTitle) verified
```

---

## 🚀 CORE-002: T.Script.FromIdeaAndTitle

### Implementation Commands

```bash
# === Step 1: Create Branch (after CORE-001 complete) ===
cd /home/runner/work/PrismQ/PrismQ
git checkout -b core-002-script-from-idea-title

# === Step 2: Navigate to Module ===
cd T/Script/FromIdeaAndTitle/

# === Step 3: Review Existing Implementation ===
cat src/script_generator.py
cat README.md

# === Step 4: Run Existing Tests ===
cd /home/runner/work/PrismQ/PrismQ
python -m pytest T/Script/FromIdeaAndTitle/_meta/tests/ -v

# === Step 5: Implement Enhancements ===
# File: T/Script/FromIdeaAndTitle/src/script_generator.py
#
# Key Classes:
#   - ScriptGenerator: Main generator class
#   - ScriptV1: Output dataclass (script_id, idea_id, title, full_text, sections, duration)
#   - ScriptSection: Section breakdown (introduction, body, conclusion)
#   - ScriptGeneratorConfig: Configuration (platform_target, duration, structure, tone)
#
# 4 Structure Types:
#   1. HOOK_DELIVER_CTA: Hook (15%) → Deliver (70%) → CTA (15%)
#   2. THREE_ACT: Setup (25%) → Development (50%) → Resolution (25%)
#   3. PROBLEM_SOLUTION: Problem (30%) → Investigation (50%) → Solution (20%)
#   4. STORY: Beginning → Middle → End
#
# Platform Targets:
#   - YOUTUBE_SHORT: < 60 seconds
#   - YOUTUBE_MEDIUM: 60-180 seconds
#   - YOUTUBE_LONG: > 180 seconds
#   - TIKTOK: < 60 seconds
#   - INSTAGRAM_REEL: < 90 seconds

# === Step 6: Write/Update Tests ===
# File: T/Script/FromIdeaAndTitle/_meta/tests/test_script_generator.py
#
# Test Cases:
#   - test_generate_script_from_valid_idea_and_title
#   - test_section_structure_intro_body_conclusion
#   - test_all_4_structure_types
#   - test_duration_calculations_accurate
#   - test_platform_specific_constraints
#   - test_tone_detection
#   - test_edge_cases_minimal_idea_long_titles

# === Step 7: Run Tests ===
python -m pytest T/Script/FromIdeaAndTitle/_meta/tests/ -v --cov=T/Script/FromIdeaAndTitle/src

# === Step 8: Integration Test with Title.From.Idea ===
python -m pytest tests/test_integration.py -k "script" -v

# === Step 9: Update Documentation ===
# Update: T/Script/FromIdeaAndTitle/README.md

# === Step 10: Commit and Push ===
git add .
git commit -m "CORE-002: Enhance T.Script.FromIdeaAndTitle module"
git push origin core-002-script-from-idea-title
```

### Acceptance Criteria Checklist

```markdown
- [ ] Script generation produces structured v1 drafts
- [ ] Scripts respect platform duration constraints (YouTube short < 60s, medium < 180s)
- [ ] Scripts include intro, body, and conclusion sections
- [ ] Content delivers on title promises
- [ ] Duration estimates are accurate (±10%)
- [ ] Module integrates with Title.From.Idea output
- [ ] Unit tests achieve >80% coverage
- [ ] Integration with Stage 4-5 (Review stages) verified
```

---

## 📊 WORKFLOW POSITION

```
Stage 1: PrismQ.T.Idea.Creation ✅ COMPLETE
    ↓
    Idea Object (concept, themes, keywords, hook, premise, synopsis)
    ↓
Stage 2: T.Title.From.Idea ← CORE-001 (Current)
    ↓
    TitleVariant (text, style, keywords, score)
    ↓
Stage 3: T.Script.FromIdeaAndTitle ← CORE-002 (Next)
    ↓
    ScriptV1 (full_text, sections, duration, metadata)
    ↓
Stage 4-5: Review stages (Future)
```

---

## 📚 RELATED DOCUMENTATION

- **[CORE-001-Title-From-Idea.md](new/CORE-001-Title-From-Idea.md)** - Full issue specification
- **[CORE-002-Script-FromIdeaAndTitle.md](new/CORE-002-Script-FromIdeaAndTitle.md)** - Full issue specification
- **[T/WORKFLOW_DETAILED.md](../../T/WORKFLOW_DETAILED.md)** - Complete 18-stage workflow
- **[PARALLEL_RUN_NEXT_FULL.md](PARALLEL_RUN_NEXT_FULL.md)** - Complete POST-MVP roadmap
