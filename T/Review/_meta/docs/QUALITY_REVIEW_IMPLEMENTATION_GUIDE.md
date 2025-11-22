# Quality Review Modules Implementation Guide

This document outlines the implementation pattern for quality review modules in the MVP iterative workflow (Stages 14-20).

## Overview

Quality review modules provide pass/fail validation gates in the content pipeline. Each module checks a specific quality dimension and can loop back to refinement if issues are found.

## Implemented Modules

### ✅ Grammar Review (Stage 14)
**Module**: `T.Review.Grammar`  
**Status**: Fully implemented with 12 passing tests  
**Pattern**: Established the reference implementation

## Modules to Implement

Following the Grammar Review pattern, these modules need implementation:

### 📋 Tone Review (Stage 15)
**Purpose**: Emotional and stylistic tone validation  
**Loop**: If FAILS → Return to Script Refinement (Stage 11)

**Key Components**:
- `ToneReview` data model
- `ToneIssue` for tracking tone mismatches
- `ToneCategory` enum (emotional_intensity, style_alignment, voice_consistency, audience_fit, mystery_balance, tonal_mismatches)
- `ToneSeverity` enum
- Pass/fail based on score threshold (default 80)
- Serialization support

**Testing**:
- Basic review creation
- Issue tracking and categorization
- Pass/fail determination
- Serialization round-trip

### 📋 Content Review (Stage 16)
**Purpose**: Narrative logic and story coherence validation  
**Loop**: If FAILS → Return to Script Refinement (Stage 11)

**Key Components**:
- `ContentReview` data model
- `ContentIssue` for tracking narrative problems
- `ContentIssueType` enum (logic_gaps, plot_contradictions, character_motivation, pacing, structural, scene_ordering)
- `ContentSeverity` enum
- Pass/fail based on score threshold (default 80)
- Serialization support

**Testing**:
- Narrative coherence validation
- Plot logic checking
- Character consistency
- Structural integrity

### 📋 Consistency Review (Stage 17)
**Purpose**: Internal continuity and logic validation  
**Loop**: If FAILS → Return to Script Refinement (Stage 11)

**Key Components**:
- `ConsistencyReview` data model
- `ConsistencyIssue` for tracking continuity errors
- `ConsistencyType` enum (character_names, timeline, locations, repeated_details, lore_facts, contradictions)
- `ConsistencySeverity` enum
- Pass/fail based on score threshold (default 85)
- Serialization support

**Testing**:
- Character name consistency
- Timeline validation
- Location continuity
- Detail matching

### 📋 Editing Review (Stage 18)
**Purpose**: Clarity, flow, and readability polish  
**Loop**: If FAILS → Return to Script Refinement (Stage 11)

**Key Components**:
- `EditingReview` data model
- `EditingSuggestion` for improvement recommendations
- `EditingCategory` enum (sentence_structure, paragraph_flow, clarity, redundancy, transitions, rewriting)
- `EditingPriority` enum
- Pass/fail based on score threshold (default 80)
- Serialization support

**Testing**:
- Sentence clarity validation
- Flow assessment
- Redundancy detection
- Transition quality

### 📋 Readability Review (Stages 19-20)
**Purpose**: Final voiceover suitability validation  
**Loops**: 
- Stage 19: Title Readability → Title Refinement if fails
- Stage 20: Script Readability → Script Refinement if fails

**Key Components**:
- `ReadabilityReview` data model (can handle both title and script)
- `ReadabilityIssue` for voiceover problems
- `ReadabilityAspect` enum (voiceover_flow, rhythm_pacing, hard_to_read, mouthfeel, dramatic_pauses, listening_clarity)
- `ReadabilitySeverity` enum
- Pass/fail based on score threshold (default 85)
- Content type field (title/script)
- Serialization support

**Testing**:
- Voiceover flow validation
- Speaking ease assessment
- Listening clarity
- Both title and script variants

## Implementation Pattern

### 1. Data Model Structure

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime

class [Type]Category/Type(Enum):
    """Categories/types for review."""
    CATEGORY_1 = "category_1"
    # ... more categories

class [Type]Severity(Enum):
    """Severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class [Type]Issue:
    """Individual issue/concern."""
    category: [Type]Category
    severity: [Type]Severity
    line_number: int  # or location reference
    text: str  # Problematic text
    suggestion: str  # Suggested fix
    explanation: str
    confidence: int = 85

@dataclass
class [Type]Review:
    """AI-powered review with pass/fail determination."""
    
    # Core fields
    script_id: str  # or title_id, content_id
    script_version: str = "v3"
    overall_score: int = 0
    pass_threshold: int = 85  # Adjust per module
    passes: bool = True
    
    # Issue tracking
    issues: List[[Type]Issue] = field(default_factory=list)
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    
    # Metadata
    reviewer_id: str = "AI-[Type]Reviewer-001"
    reviewed_at: Optional[str] = None
    confidence_score: int = 90
    
    # Feedback
    summary: str = ""
    primary_concerns: List[str] = field(default_factory=list)
    quick_fixes: List[str] = field(default_factory=list)
    notes: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize computed fields."""
        if self.reviewed_at is None:
            self.reviewed_at = datetime.now().isoformat()
        self.passes = self.overall_score >= self.pass_threshold
    
    def add_issue(self, issue: [Type]Issue) -> None:
        """Add issue and update counts."""
        self.issues.append(issue)
        # Update severity counts
        # Recalculate pass status
    
    def get_issues_by_severity(self, severity) -> List[[Type]Issue]:
        """Filter issues by severity."""
        pass
    
    def get_critical_issues(self) -> List[[Type]Issue]:
        """Get critical issues."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        pass
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Deserialize from dictionary."""
        pass
```

### 2. Module Structure

```
T/Review/[Module]/
├── __init__.py                     # Module exports
├── [module]_review.py              # Main implementation
├── requirements.txt                # Test dependencies (pytest)
├── pyproject.toml                  # Project configuration
├── README.md                       # Module documentation
└── _meta/
    ├── README.md                   # Testing instructions
    ├── tests/
    │   ├── __init__.py
    │   └── test_[module]_review.py # Comprehensive tests
    └── examples/
        └── example_usage.py        # Usage examples
```

### 3. Test Structure

```python
class TestBasic:
    """Basic functionality tests."""
    def test_create_review(self): pass
    def test_create_passing_review(self): pass
    def test_create_failing_review(self): pass

class TestIssues:
    """Issue tracking tests."""
    def test_create_issue(self): pass
    def test_add_issue(self): pass
    def test_critical_fails_review(self): pass

class TestMethods:
    """Method tests."""
    def test_get_by_severity(self): pass
    def test_get_by_type(self): pass
    def test_get_critical(self): pass
    def test_get_high_priority(self): pass

class TestSerialization:
    """Serialization tests."""
    def test_to_dict(self): pass
    def test_from_dict(self): pass
    def test_round_trip(self): pass
```

### 4. Workflow Integration

Each module must integrate into the workflow loop:

```python
# Stage [N]: [Type] Review
review = [Type]Review(
    script_id=script_id,
    script_version=version,
    overall_score=score
)

# Add issues found
for issue in detected_issues:
    review.add_issue(issue)

# Determine next stage
if review.passes:
    # Proceed to next review stage
    next_stage = Stage[N+1]
else:
    # Loop back to refinement
    return_to_refinement(review.get_high_priority_issues())
```

## Key Principles

1. **Pass/Fail Gates**: Every review must have clear pass/fail determination
2. **Issue Tracking**: All issues must be categorized, prioritized, and explained
3. **Feedback Loop**: Failed reviews provide actionable feedback for refinement
4. **Consistency**: All modules follow the same pattern and conventions
5. **Testing**: Comprehensive test coverage (10-15 tests minimum)
6. **Documentation**: Clear docstrings and usage examples
7. **Serialization**: Support for persistence and API integration

## Implementation Priority

1. **Tone Review** (Stage 15) - Critical for emotional consistency
2. **Content Review** (Stage 16) - Critical for narrative coherence
3. **Readability Review** (Stages 19-20) - Critical final validation
4. **Consistency Review** (Stage 17) - Important for continuity
5. **Editing Review** (Stage 18) - Important for polish

## Success Criteria

Each implemented module must:
- [ ] Follow the established pattern from Grammar Review
- [ ] Have comprehensive data model
- [ ] Include 10-15 passing tests minimum
- [ ] Support serialization (to_dict/from_dict)
- [ ] Have clear pass/fail determination
- [ ] Provide actionable feedback
- [ ] Include usage examples
- [ ] Be documented in T/Review/README.md

## Reference Implementation

See `T/Review/Grammar/` for the complete reference implementation that established this pattern.
