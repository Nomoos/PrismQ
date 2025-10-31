# Issue 504: Extend Model with Classification and Scoring Tables

**Type**: Database Schema Enhancement
**Priority**: Medium
**Status**: New
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM

## Description

Extend the Model database schema to include dedicated tables for Classification and Scoring results, creating proper relationships with IdeaInspiration. This enables storing rich classification metadata and scoring breakdowns separately from the main IdeaInspiration table.

## Current State

The IdeaInspiration table currently stores:
- Basic classification: `category` (single field)
- Basic scoring: `score` (single integer)
- Some metadata: `subcategory_relevance`, `contextual_category_scores`

**Limitations:**
- ❌ No history of classification changes
- ❌ No confidence scores or classification metadata
- ❌ No detailed score breakdown
- ❌ No versioning or timestamps for scores
- ❌ Can't track which classifier or scorer was used
- ❌ Can't store multiple classifications

## Goals

1. **Rich Classification Storage**
   - Store classification confidence scores
   - Track which classifier produced the result
   - Support multiple classifications per idea
   - Store classification metadata and indicators
   - Version classification results

2. **Detailed Scoring Storage**
   - Break down composite scores into components
   - Track engagement vs. quality scores separately
   - Store scoring methodology and version
   - Enable score history and auditing

3. **Proper Relationships**
   - One-to-many: IdeaInspiration → Classifications
   - One-to-many: IdeaInspiration → Scores
   - Referential integrity with foreign keys

4. **Query Capabilities**
   - Find ideas by classification confidence
   - Compare scoring methods
   - Track classification/scoring history
   - Analytics on classifier/scorer performance

## Proposed Schema

### Classification Table

```sql
CREATE TABLE classifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_inspiration_id INTEGER NOT NULL,
    
    -- Classification results
    category TEXT NOT NULL,
    confidence REAL NOT NULL,  -- 0.0 to 1.0
    is_story BOOLEAN DEFAULT 0,
    story_confidence REAL,
    
    -- Classification metadata
    classifier_name TEXT NOT NULL,
    classifier_version TEXT,
    model_name TEXT,  -- e.g., 'bert-base', 'gpt-4'
    
    -- Detailed indicators (JSON)
    indicators TEXT,  -- Story indicators, category signals, etc.
    subcategory_scores TEXT,  -- Full category breakdown as JSON
    
    -- Timestamps
    classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key
    FOREIGN KEY (idea_inspiration_id) REFERENCES idea_inspiration(id) ON DELETE CASCADE
);

CREATE INDEX idx_classification_idea ON classifications(idea_inspiration_id);
CREATE INDEX idx_classification_category ON classifications(category);
CREATE INDEX idx_classification_confidence ON classifications(confidence);
```

### Scoring Table

```sql
CREATE TABLE scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_inspiration_id INTEGER NOT NULL,
    
    -- Composite score
    composite_score REAL NOT NULL,
    
    -- Score components
    engagement_score REAL,
    text_quality_score REAL,
    virality_score REAL,
    relevance_score REAL,
    
    -- Score breakdown (JSON)
    engagement_metrics TEXT,  -- Views, likes, comments breakdown
    quality_metrics TEXT,  -- Grammar, coherence, originality, etc.
    
    -- Scoring metadata
    scorer_name TEXT NOT NULL,
    scorer_version TEXT,
    scoring_method TEXT,  -- 'rule-based', 'ml-based', 'hybrid'
    
    -- Contextual scores
    contextual_scores TEXT,  -- Language, region, age, gender context
    
    -- Timestamps
    scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key
    FOREIGN KEY (idea_inspiration_id) REFERENCES idea_inspiration(id) ON DELETE CASCADE
);

CREATE INDEX idx_score_idea ON scores(idea_inspiration_id);
CREATE INDEX idx_score_composite ON scores(composite_score);
CREATE INDEX idx_score_engagement ON scores(engagement_score);
```

### Source Tracking Table

```sql
CREATE TABLE source_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idea_inspiration_id INTEGER NOT NULL,
    
    -- Source information
    source_type TEXT NOT NULL,  -- 'creative', 'signal', 'event', etc.
    platform TEXT NOT NULL,  -- 'youtube', 'genius', 'google_trends', etc.
    source_module TEXT,  -- Module that collected it
    
    -- Collection metadata
    collection_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    collection_method TEXT,  -- 'api', 'scrape', 'manual', etc.
    
    -- Processing status
    processing_status TEXT DEFAULT 'pending',  -- 'pending', 'processed', 'failed'
    last_processed_at TIMESTAMP,
    error_log TEXT,
    
    -- Retry tracking
    retry_count INTEGER DEFAULT 0,
    last_retry_at TIMESTAMP,
    
    -- Foreign key
    FOREIGN KEY (idea_inspiration_id) REFERENCES idea_inspiration(id) ON DELETE CASCADE
);

CREATE INDEX idx_tracking_idea ON source_tracking(idea_inspiration_id);
CREATE INDEX idx_tracking_status ON source_tracking(processing_status);
CREATE INDEX idx_tracking_platform ON source_tracking(platform);
```

## Domain Models

### Classification Model

```python
# Model/classification_result.py
from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime

@dataclass
class ClassificationResult:
    """Classification result for an IdeaInspiration."""
    
    idea_inspiration_id: int
    category: str
    confidence: float
    is_story: bool = False
    story_confidence: Optional[float] = None
    
    classifier_name: str = "default"
    classifier_version: Optional[str] = None
    model_name: Optional[str] = None
    
    indicators: Dict[str, any] = field(default_factory=dict)
    subcategory_scores: Dict[str, float] = field(default_factory=dict)
    
    classified_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for database storage."""
        return {
            'idea_inspiration_id': self.idea_inspiration_id,
            'category': self.category,
            'confidence': self.confidence,
            'is_story': self.is_story,
            'story_confidence': self.story_confidence,
            'classifier_name': self.classifier_name,
            'classifier_version': self.classifier_version,
            'model_name': self.model_name,
            'indicators': self.indicators,
            'subcategory_scores': self.subcategory_scores,
            'classified_at': self.classified_at
        }
```

### Score Model

```python
# Model/score_result.py
from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime

@dataclass
class ScoreResult:
    """Scoring result for an IdeaInspiration."""
    
    idea_inspiration_id: int
    composite_score: float
    
    engagement_score: Optional[float] = None
    text_quality_score: Optional[float] = None
    virality_score: Optional[float] = None
    relevance_score: Optional[float] = None
    
    scorer_name: str = "default"
    scorer_version: Optional[str] = None
    scoring_method: str = "rule-based"
    
    engagement_metrics: Dict[str, any] = field(default_factory=dict)
    quality_metrics: Dict[str, any] = field(default_factory=dict)
    contextual_scores: Dict[str, int] = field(default_factory=dict)
    
    scored_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for database storage."""
        return {
            'idea_inspiration_id': self.idea_inspiration_id,
            'composite_score': self.composite_score,
            'engagement_score': self.engagement_score,
            'text_quality_score': self.text_quality_score,
            'virality_score': self.virality_score,
            'relevance_score': self.relevance_score,
            'scorer_name': self.scorer_name,
            'scorer_version': self.scorer_version,
            'scoring_method': self.scoring_method,
            'engagement_metrics': self.engagement_metrics,
            'quality_metrics': self.quality_metrics,
            'contextual_scores': self.contextual_scores,
            'scored_at': self.scored_at
        }
```

## Repository Extensions

```python
class ClassificationRepository:
    """Repository for ClassificationResult persistence."""
    
    def add(self, classification: ClassificationResult) -> int:
        """Save classification result."""
        pass
    
    def get_by_idea(self, idea_id: int) -> List[ClassificationResult]:
        """Get all classifications for an idea."""
        pass
    
    def get_latest_by_idea(self, idea_id: int) -> Optional[ClassificationResult]:
        """Get most recent classification for an idea."""
        pass

class ScoreRepository:
    """Repository for ScoreResult persistence."""
    
    def add(self, score: ScoreResult) -> int:
        """Save score result."""
        pass
    
    def get_by_idea(self, idea_id: int) -> List[ScoreResult]:
        """Get all scores for an idea."""
        pass
    
    def get_latest_by_idea(self, idea_id: int) -> Optional[ScoreResult]:
        """Get most recent score for an idea."""
        pass
```

## Integration with Classification Module

```python
# In Classification module
from Model.classification_result import ClassificationResult
from Model.infrastructure.repositories.classification_repository import ClassificationRepository

def classify_and_save(idea: IdeaInspiration, repo: ClassificationRepository):
    """Classify idea and save results."""
    # Classify
    category, confidence = classifier.classify(idea)
    is_story, story_conf = story_detector.detect(idea)
    
    # Create result
    result = ClassificationResult(
        idea_inspiration_id=idea.id,
        category=category,
        confidence=confidence,
        is_story=is_story,
        story_confidence=story_conf,
        classifier_name="TextClassifier",
        classifier_version="1.0.0"
    )
    
    # Save
    repo.add(result)
```

## Implementation Steps

1. **Phase 1: Schema Design** (Week 1)
   - Finalize table schemas
   - Create migration scripts
   - Update setup_db scripts

2. **Phase 2: Domain Models** (Week 1)
   - Implement ClassificationResult
   - Implement ScoreResult
   - Implement SourceTracking

3. **Phase 3: Repositories** (Week 2)
   - Implement ClassificationRepository
   - Implement ScoreRepository
   - Implement SourceTrackingRepository

4. **Phase 4: Migration** (Week 2-3)
   - Migrate existing category data to classifications table
   - Migrate existing score data to scores table
   - Data validation

5. **Phase 5: Integration** (Week 3)
   - Update Classification module
   - Update Scoring module
   - Update Source modules

6. **Phase 6: Testing** (Week 3-4)
   - Unit tests for new models
   - Integration tests
   - Migration tests

7. **Phase 7: Documentation** (Week 4)
   - Update schema documentation
   - Add usage examples
   - Migration guide

## Benefits

1. **Rich Metadata**
   - Store full classification/scoring details
   - Track confidence and methods
   - Enable auditing and analysis

2. **History Tracking**
   - See how classifications change over time
   - Compare different classifiers/scorers
   - A/B testing of models

3. **Better Queries**
   - Find high-confidence classifications
   - Compare scoring methods
   - Analytics on classifier performance

4. **Proper Architecture**
   - Normalized database design
   - Clear relationships
   - Referential integrity

## Related Issues

- Issue #500: Repository Pattern
- Issue #502: SQLAlchemy ORM Layer
- Classification module: Uses these tables
- Scoring module: Uses these tables

## Success Criteria

- [ ] Database schema extended with new tables
- [ ] Migration scripts working
- [ ] Domain models implemented
- [ ] Repositories implemented
- [ ] Classification module integrated
- [ ] Scoring module integrated
- [ ] All tests passing
- [ ] Documentation complete

## Estimated Effort

4 weeks (1 developer)

## Migration Strategy

1. **Backward Compatible**: Keep existing fields in IdeaInspiration
2. **Gradual Migration**: Populate new tables alongside old fields
3. **Dual-Write**: Write to both old and new locations temporarily
4. **Validation**: Verify data consistency
5. **Cutover**: Eventually deprecate old fields

## Notes

This schema extension aligns with Issue #002 (Database Integration) and provides the foundation for advanced analytics and machine learning features.
