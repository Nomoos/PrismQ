# MVP-006: Title Improvements v2

**Module**: PrismQ.T.Title.FromOriginalTitleAndReviewAndScript  
**Worker**: Worker13  
**Priority**: Critical  
**Effort**: 2 days  
**Status**: READY TO START

---

## Overview

Implement title v2 generation module that creates improved title versions using feedback from both cross-reviews (MVP-004: Title reviewed by Script, MVP-005: Script reviewed by Title). This is Stage 6 in the 26-stage iterative workflow.

---

## Dependencies

**Requires**:
- ✅ MVP-001: T.Idea.Creation (Complete)
- ✅ MVP-002: T.Title.FromIdea (Complete) - Provides title v1
- ✅ MVP-003: T.Script.FromIdeaAndTitle (Complete) - Provides script v1
- ✅ MVP-004: T.Review.Title.ByScript (Complete) - Provides title review feedback
- ✅ MVP-005: T.Review.Script.ByTitle (Complete) - Provides script review feedback

**Required By**:
- MVP-007: T.Script.FromOriginalScriptAndReviewAndTitle (needs title v2)
- MVP-008: T.Review.Title.ByScript (v2) (reviews title v2)

**Status**: ✅ ALL DEPENDENCIES MET - READY TO START

---

## Implementation Location

- **Path**: `T/Title/FromOriginalTitleAndReviewAndScript/`
- **Module Structure**:
  ```
  T/Title/FromOriginalTitleAndReviewAndScript/
  ├── src/
  │   ├── __init__.py
  │   └── title_improver.py (main implementation)
  ├── _meta/
  │   ├── tests/
  │   │   ├── test_title_improver.py (unit tests)
  │   │   └── test_acceptance_criteria.py (acceptance tests)
  │   └── examples/
  │       └── improvement_example.py (usage examples)
  └── README.md (module documentation)
  ```

---

## Input Specifications

### Title v1
- Original title from MVP-002
- 3-5 variants with rationale
- Engagement scores
- SEO metrics

### Script v1
- Complete narrative script from MVP-003
- Structured content
- Key themes and keywords

### Title Review Feedback (from MVP-004)
- Alignment scores (script 30% + idea 25%)
- Engagement assessment (25%)
- SEO optimization (20%)
- Keyword mismatches (title keywords not in script)
- Prioritized improvements with impact scores (0-100)

### Script Review Feedback (from MVP-005)
- Title alignment score (25%)
- Idea alignment score (30%)
- Content quality scores (45%):
  - Engagement
  - Pacing
  - Clarity
  - Structure
  - Impact
- Gap analysis (title promises vs script delivery)
- Prioritized improvement recommendations

### Original Idea
- Source idea for consistency checking
- Core concept and intent

---

## Output Specifications

### Title v2 Object

```python
{
    "version": 2,
    "title": "Improved Title Text",
    "previous_version": 1,
    "improvements_applied": [
        {
            "category": "alignment",  # or "engagement", "seo", "clarity"
            "issue": "Description of issue from reviews",
            "fix": "How it was addressed",
            "impact_score": 85
        }
    ],
    "v1_reference": "title_v1_id",
    "review_references": {
        "title_review": "review_id_from_mvp004",
        "script_review": "review_id_from_mvp005"
    },
    "engagement_score": 8.5,  # out of 10
    "alignment_score": 9.0,   # out of 10
    "seo_score": 8.0,         # out of 10
    "rationale": "Explanation of how v2 addresses v1 issues",
    "metadata": {
        "created_at": "2025-11-22T...",
        "generated_by": "PrismQ.T.Title.FromOriginalTitleAndReviewAndScript",
        "feedback_sources": ["MVP-004", "MVP-005"]
    }
}
```

---

## Acceptance Criteria

### Functional Requirements
- ✅ Generate title v2 using feedback from BOTH reviews (MVP-004 and MVP-005)
- ✅ Use title v1, script v1, and both review feedbacks as inputs
- ✅ Maintain or improve engagement while improving alignment
- ✅ Address high-impact feedback items first (sorted by impact score)
- ✅ Store v2 with reference to v1 and review sources
- ✅ Preserve engagement while fixing alignment issues

### Quality Requirements
- ✅ v2 shows measurable improvement over v1 in alignment scores
- ✅ v2 maintains or improves engagement metrics
- ✅ v2 addresses at least top 3 high-impact issues from reviews
- ✅ Rationale clearly explains how feedback was incorporated
- ✅ All keyword mismatches from MVP-004 addressed

### Technical Requirements
- ✅ JSON output format compatible with workflow
- ✅ Version tracking (v1 → v2 relationship)
- ✅ Metadata includes all review references
- ✅ Module supports v2 → v3 → v4+ progression (extensible)

### Testing Requirements
- ✅ Unit tests: Title improvement logic
- ✅ Integration tests: Using real review feedback
- ✅ Acceptance tests: Verify v2 addresses v1 issues
- ✅ Edge cases: Missing feedback, conflicting feedback
- ✅ Test coverage: >90% of improvement logic

---

## Algorithm Approach

### Step 1: Analyze Feedback
1. Parse feedback from MVP-004 (title review)
2. Parse feedback from MVP-005 (script review)
3. Identify alignment issues
4. Prioritize by impact score (0-100)

### Step 2: Identify Improvements
1. Extract keyword mismatches (from MVP-004)
2. Identify gaps in title promise vs script delivery (from MVP-005)
3. Assess engagement issues
4. Evaluate SEO opportunities

### Step 3: Generate Title v2
1. Start with title v1 as base
2. Apply high-impact improvements first (score >70)
3. Ensure new keywords from script are included
4. Maintain or improve engagement level
5. Validate against idea for consistency

### Step 4: Validate v2
1. Check alignment with script v1
2. Verify engagement level maintained
3. Ensure SEO score improved
4. Confirm all high-priority issues addressed

---

## Success Metrics

### Alignment Improvement
- **Target**: v2 alignment score ≥ v1 + 15%
- **Measurement**: Compare alignment scores from reviews

### Engagement Preservation
- **Target**: v2 engagement score ≥ v1 - 5%
- **Measurement**: Engagement metrics from scoring

### Issue Resolution
- **Target**: Address 100% of high-impact issues (score >70)
- **Measurement**: Count of resolved vs total issues

### SEO Enhancement
- **Target**: v2 SEO score ≥ v1 + 10%
- **Measurement**: SEO metrics from analysis

---

## Integration Points

### Inputs From
- MVP-002: Title v1 variants
- MVP-003: Script v1 content
- MVP-004: Title review feedback
- MVP-005: Script review feedback

### Outputs To
- MVP-007: Script v2 generation (uses title v2)
- MVP-008: Title v2 review (reviews this output)
- Workflow system: Version tracking

---

## Testing Strategy

### Unit Tests (15-20 tests)
- Test improvement logic with sample feedback
- Test prioritization by impact score
- Test keyword integration
- Test engagement preservation
- Test version reference creation
- Test JSON serialization

### Integration Tests (8-10 tests)
- Test with real MVP-004 feedback
- Test with real MVP-005 feedback
- Test with both feedbacks combined
- Test edge cases (minimal feedback)
- Test conflicting feedback resolution

### Acceptance Tests (5-8 tests)
- Verify v2 > v1 in alignment
- Verify engagement maintained
- Verify high-impact issues resolved
- Verify version progression works
- Verify rationale completeness

---

## Example Usage

```python
from T.Title.FromOriginalTitleAndReviewAndScript import TitleImprover

# Initialize improver
improver = TitleImprover()

# Generate title v2
title_v2 = improver.improve_title(
    title_v1=title_v1_object,
    script_v1=script_v1_object,
    title_review=mvp004_review_object,
    script_review=mvp005_review_object,
    original_idea=idea_object
)

# Access improvements
print(f"Title v2: {title_v2.title}")
print(f"Improvements: {len(title_v2.improvements_applied)}")
print(f"Alignment score: {title_v2.alignment_score}")
print(f"Rationale: {title_v2.rationale}")
```

---

## Documentation Requirements

### README.md
- Module overview and purpose
- Input/output specifications
- Usage examples
- API reference
- Integration guide

### Code Comments
- Complex improvement logic explained
- Prioritization algorithm documented
- Edge cases noted

---

## SOLID Principles

### Single Responsibility
- Focus: Generate improved title v2 from reviews
- Does NOT: Generate reviews, validate scripts, create ideas

### Open/Closed
- Extensible: Can support v3, v4, v5+ versions
- Closed: Core improvement algorithm stable

### Liskov Substitution
- TitleImprover can be used wherever title generation is needed
- Output compatible with downstream modules

### Interface Segregation
- Clean API: improve_title() method
- No unnecessary dependencies

### Dependency Inversion
- Depends on abstractions (review format, title format)
- Not dependent on specific review implementations

---

## Risk Assessment

### Technical Risks
- **Risk**: Conflicting feedback from two reviews
- **Mitigation**: Prioritize by impact score, use script alignment as tiebreaker

- **Risk**: Over-optimization losing engagement
- **Mitigation**: Set minimum engagement threshold, test preservation

### Schedule Risks
- **Risk**: Complex feedback integration takes >2 days
- **Mitigation**: Start with high-impact items, iterate

---

## Definition of Done

- ✅ Code implementation complete
- ✅ All unit tests passing (15-20 tests)
- ✅ All integration tests passing (8-10 tests)
- ✅ All acceptance tests passing (5-8 tests)
- ✅ README.md documentation complete
- ✅ Code review passed
- ✅ Integration with MVP-007 verified
- ✅ Improvement metrics validated (alignment +15%, engagement -5%)

---

**Issue Created**: 2025-11-22  
**Owner**: Worker13  
**Reviewer**: Worker10  
**Status**: READY TO START ✅
