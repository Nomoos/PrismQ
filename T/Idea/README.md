# T/Idea - Idea Development Module

**Namespace**: `PrismQ.T.Idea`

The Idea module represents a unit of creative content — the fundamental "thought object" that emerges from inspiration, analysis, and transformation. It is an abstract entity that captures the essence of a new idea: its purpose, theme, potential, and direction for further development.

## Purpose

Transform inspiration into structured content concepts with clear outlines, validated potential, and production-ready foundations. Ideas are not mere text or one-time concepts, but structured products that can be tracked, evaluated, modified, and integrated into larger workflows.

## Submodules

### [Fusion](./Fusion/)
**Combine multiple Ideas or IdeaInspiration sources**

Fuse multiple Ideas or IdeaInspiration instances into unified, cohesive Ideas using AI-powered combination logic with batch processing support.

- Batch processing of Ideas
- Multiple fusion strategies (best_elements, weighted_merge, theme_based, keyword_cluster)
- Signal aggregation (keywords, themes, platforms)
- Story synthesis and narrative merging
- Quality-based source selection

**Workflow Position**: `IdeaInspiration (multiple) → Fusion → New Idea(s)` or `Idea (multiple) → Fusion → New Idea(s)`

**[→ View Fusion Documentation](./Fusion/README.md)**

**[→ View Fusion Metadata](./Fusion/_meta/)**
- [Examples](./Fusion/_meta/examples/) - Usage examples
- [Tests](./Fusion/_meta/tests/) - Fusion tests

---

### [Creation](./Creation/)
**Generate multiple Ideas from simple inputs**

Create multiple rich, detailed Ideas from minimal input (title or description) using AI-powered generation with variable-length optimization.

- Create from title with variations
- Create from description with auto-title generation
- Variable-length content generation
- Batch idea generation
- Multi-format optimization

**Workflow Position**: `Title/Description → Creation → Multiple Ideas`

**[→ View Creation Documentation](./Creation/README.md)**

**[→ View Creation Metadata](./Creation/_meta/)**
- [Examples](./Creation/_meta/examples/) - Usage examples
- [Tests](./Creation/_meta/tests/) - Creation tests
### [Inspiration](./Inspiration/)
**Idea inspiration and collection**

Gather and evaluate content inspiration from multiple sources to identify high-potential concepts for idea development.

- Multi-source inspiration collection (24+ sources)
- Content classification (8 categories)
- Engagement potential scoring (0-100 scale)
- Analytics feedback integration

**[→ View Inspiration Documentation](./Inspiration/README.md)**

**[→ View Inspiration Metadata](./Inspiration/_meta/)**
- [Docs](./Inspiration/_meta/docs/) - Inspiration documentation
- [Examples](./Inspiration/_meta/examples/) - Inspiration examples
- [Tests](./Inspiration/_meta/tests/) - Inspiration tests

---

### [Model](./Model/)
**Core data model and structure**

Defines the Idea data structure, fields, validation, and database schema. Also serves as the Creation stage where inspiration transforms into a concrete idea concept.

- Data model definition
- Field specifications and validation
- Database integration
- AI generation support
- Multi-format content support
- **Summary generation** (new)
- **Czech translation** (new)
- Initial idea formation and concept development

**Workflow Position**: `Inspiration → Model (Creation) → Outline → Title`

**[→ View Model Documentation](./Model/README.md)**

**[→ View Model Metadata](./Model/_meta/)**
- [Docs](./Model/_meta/docs/) - Model documentation
- [Examples](./Model/_meta/examples/) - Usage examples
- [Tests](./Model/_meta/tests/) - Model tests

---

### [Outline](./Outline/)
**Content outline development**

Structured content outline creation and refinement.

- Topic organization
- Structure development
- Flow and hierarchy
- Section planning

**[→ View Outline Documentation](./Outline/README.md)**

**[→ View Outline Metadata](./Outline/_meta/)**
- [Docs](./Outline/_meta/docs/) - Outline documentation
- [Examples](./Outline/_meta/examples/) - Outline examples
- [Tests](./Outline/_meta/tests/) - Outline tests

---

## Related Modules

### Idea Review
For idea validation and review, see **[T/Review/Idea](../Review/Idea/)** - validates ideas for viability, potential, and alignment with content strategy.

---

## Module Metadata

### Documentation
Technical documentation and implementation guides.

**[→ View Idea/_meta/docs/](./_meta/docs/)**

### Examples
Usage examples and sample implementations.

**[→ View Idea/_meta/examples/](./_meta/examples/)**

### Tests
Test suites and test data.

**[→ View Idea/_meta/tests/](./_meta/tests/)**

---

## Key Features

### Structured Content Object
Ideas are structured entities with:
- **Purpose**: What the idea represents and what problem it solves
- **Theme**: Core topic and emotional quality
- **Target Audience**: Demographics, platforms, style, genre
- **Metadata**: Technical and strategic criteria for usability

### Potential Modeling
Ideas model their cross-platform potential:
- Platform suitability (short videos, podcasts, articles)
- Regional and demographic reach
- Measurable parameters for decision making
- Computational or expert-based scoring

### Iterative Development
Ideas support evolution over time:
- Version control
- Context refinement
- Feedback integration
- Life-cycle tracking from capture to production

### Multi-Format Support
Ideas serve as foundation for:
- Script generation
- Podcast production
- Video creation
- Marketing content
- Product proposals

## Workflow Integration
```
Creation Module → Multiple Idea variations
    ↓
Idea Module (Composite State)
    ├─ Model (data structure, summary, translation)
    ├─ Outline (organization)
    ├─ Skeleton (basic framework)
    ├─ Title (finalization)
    └─ Review (validation)
Inspiration (Source Collection & Scoring)
    ↓
Idea Module (Composite State)
    ├─ Model/Creation (idea formation) ← Starting sub-state
    └─ Outline (organization)
    ↓
[Exit Idea Module] → Review/Idea (validation) → Title → ScriptDraft
```
```
Inspiration (multiple sources)
    ↓
Fusion Module → Fused Idea(s)
    ↓
Idea Module (Composite State)
    ├─ Model (data structure, summary, translation)
    ├─ Outline (organization)
    ├─ Skeleton (basic framework)
    ├─ Title (finalization)
    └─ Review (validation)
Inspiration (Source Collection & Scoring)
    ↓
Idea Module (Composite State)
    ├─ Model/Creation (idea formation) ← Starting sub-state
    └─ Outline (organization)
    ↓
[Exit Idea Module] → Review/Idea (validation) → Title → ScriptDraft
```

**New Workflows:**
```
# Fusion Workflow
IdeaInspiration (multiple) → Fusion → New Idea(s)
Idea (multiple) → Fusion → New Idea(s)

# Creation Workflow
Title/Description → Creation → Multiple Ideas (with variations)

# Summary & Translation Workflow
Idea → Generate Summary → Translate to Czech
```

## Usage Examples

### Fusion Example

```python
from PrismQ.T.Idea.Fusion.src import IdeaFusion
from PrismQ.T.Idea.Model.src import Idea, ContentGenre

# Fuse multiple ideas
idea1 = Idea(title="AI Ethics", concept="Ethical AI development", 
             genre=ContentGenre.TECHNOLOGY)
idea2 = Idea(title="Machine Learning", concept="ML algorithms explained",
             genre=ContentGenre.EDUCATIONAL)

fusion = IdeaFusion()
fused_idea = fusion.fuse_ideas([idea1, idea2])
```

### Creation Example

```python
from PrismQ.T.Idea.From.User.src import IdeaCreator

# Create multiple ideas from title
creator = IdeaCreator()
ideas = creator.create_from_title(
    "The Future of AI",
    num_ideas=3,
    target_platforms=["youtube", "medium"],
    target_formats=["video", "text"]
)
```

### Summary & Translation Example

```python
from PrismQ.T.Idea.Model.src import Idea, ContentGenre

# Create idea
idea = Idea(
    title="Digital Privacy",
    concept="Protecting personal information",
    genre=ContentGenre.EDUCATIONAL
)

# Generate summary
summary = idea.generate_summary(max_length=500)
```

### Traditional Model Example
Inspiration → Model (Creation) → Outline → [Exit to Review/Idea for validation] → Title
```

**Note**: 
- Title is a separate module at `T/Title/`, not a sub-state of Idea
- Idea validation/review is handled by `T/Review/Idea/`, which is part of the review pipeline
- After completing Outline, the workflow exits the Idea module and proceeds to Review/Idea for validation

## Usage Example

```python
from PrismQ.T.Idea import Model, Outline
from PrismQ.T.Review.Idea import Review

# Create new idea
idea = Model.create(
    title="AI Content Generation Guide",
    purpose="Educate developers on AI tools",
    target_audience="Software engineers",
    platform="Blog, YouTube"
)

# Develop outline
outline = Outline.create_from_idea(idea)
outline.add_section("Introduction to AI Tools")
outline.add_section("Practical Implementation")

# Review and validate
review = Review.validate(idea)
if review.is_viable:
    idea.status = IdeaStatus.APPROVED
```

## Navigation

**[← Back to T](../README.md)** | **[→ Script Module](../Script/)** | **[→ T/_meta](./_meta/)**

---

*Part of the PrismQ.T Text Generation Pipeline*
