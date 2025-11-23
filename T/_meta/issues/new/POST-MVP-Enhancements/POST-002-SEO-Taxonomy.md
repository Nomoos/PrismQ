# POST-002: T.Publishing.SEO - Tags & Categories

**Type**: Post-MVP Enhancement  
**Worker**: Worker17 (Analytics)  
**Priority**: High  
**Effort**: 1.5 days  
**Module**: `PrismQ.T.Publishing.SEO.Taxonomy`  
**Sprint**: Sprint 4 (Weeks 9-10)  
**Status**: 🎯 PLANNED

---

## Description

Automatic tag generation and category assignment for content classification.

This system will analyze content and automatically assign relevant tags and categories, improving content organization, discoverability, and enabling better filtering and recommendation systems.

---

## Acceptance Criteria

- [ ] Auto-generate relevant tags from content analysis
- [ ] Assign content to appropriate predefined categories
- [ ] Support custom taxonomy definitions (extensible)
- [ ] Validate tag relevance scores (>0.7 threshold)
- [ ] Integration with content export functionality
- [ ] Generate hierarchical category structure
- [ ] Support multi-category assignment (1-3 categories per content)
- [ ] Deduplicate similar tags automatically

---

## Input/Output

**Input**:
- Published content (title + script)
- SEO keywords from POST-001
- Optional: Existing taxonomy configuration

**Output**:
- Tag list with relevance scores
- Category assignments with confidence scores
- Taxonomy hierarchy visualization
- Tag/category statistics

---

## Dependencies

- **POST-001**: SEO keyword extraction (provides base keywords for tag generation)
- **MVP-024**: Publishing.Finalization module

---

## Technical Notes

### Tag Generation Strategy
1. Extract tags from SEO keywords
2. Use semantic analysis for tag expansion
3. Apply relevance filtering (score >0.7)
4. Deduplicate using similarity matching

### Category Assignment Strategy
1. Define predefined category taxonomy (e.g., Tech, Lifestyle, Education, Business)
2. Use classification algorithm (scikit-learn or GPT-based)
3. Support hierarchical categories (Parent > Child)
4. Multi-label classification for cross-category content

### Files to Create/Modify
- `T/Publishing/SEO/Taxonomy/tag_generator.py` (new)
- `T/Publishing/SEO/Taxonomy/category_classifier.py` (new)
- `T/Publishing/SEO/Taxonomy/taxonomy_config.py` (new)
- `T/Publishing/ContentExport/content_export.py` (modify - add taxonomy data)

### Database Schema
```sql
-- Tags table
CREATE TABLE content_tags (
    id INTEGER PRIMARY KEY,
    content_id INTEGER,
    tag TEXT,
    relevance_score REAL,
    created_at TIMESTAMP
);

-- Categories table  
CREATE TABLE content_categories (
    id INTEGER PRIMARY KEY,
    content_id INTEGER,
    category_path TEXT,  -- e.g., "Tech/AI/ML"
    confidence_score REAL,
    created_at TIMESTAMP
);
```

### Testing Requirements
- [ ] Unit tests for tag generation
- [ ] Unit tests for category classification
- [ ] Integration test with ContentExport
- [ ] Test with edge cases (short content, technical content, multi-topic)
- [ ] Validate taxonomy hierarchy

---

## Custom Taxonomy Configuration

Support JSON-based taxonomy definition:
```json
{
  "categories": {
    "Tech": ["AI", "Web", "Mobile", "Cloud"],
    "Lifestyle": ["Health", "Fitness", "Travel"],
    "Business": ["Marketing", "Finance", "Entrepreneurship"]
  },
  "tag_rules": {
    "min_relevance": 0.7,
    "max_tags": 10
  }
}
```

---

## Success Metrics

- Tag relevance accuracy >80%
- Category classification accuracy >85%
- Tag generation time <1 second
- Support for 20+ predefined categories
- Zero duplicated tags

---

**Created**: 2025-11-23  
**Owner**: Worker17 (Analytics Specialist)
