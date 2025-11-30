# T/Title/From/Idea - Initial Title Draft from Idea

**Namespace**: `PrismQ.T.Title.From.Idea`

Generate initial title variants directly from the idea concept and create Story objects.

## Purpose

Create the first version (v0) of title options based solely on the original idea, before any script content exists. This module:
1. Creates 10 Story objects with FK reference to the source Idea
2. Generates the first Title (version 0) for each Story from the Idea content

## Workflow Position

**Stage 2** in MVP workflow: `PrismQ.T.Title.Draft (v0)`

```
PrismQ.T.Idea.Creation
    ↓
PrismQ.T.Title.From.Idea (v0) ← Creates Stories + Initial titles
    ↓
PrismQ.T.Script.Draft (v0)
```

## Input

- Idea object with:
  - Core concept
  - Target audience
  - Content theme
  - Key message

## Process

1. Analyze idea concept and theme
2. Create 10 Story objects, each referencing the source Idea (FK relationship)
3. Generate 10 title variants using diverse strategies
4. Create first Title (v0) for each Story using generated variants
5. Update each Story's state to TITLE_V0
6. Consider SEO and engagement factors
7. Return Stories with their Titles

## Output

- 10 Story objects with:
  - FK reference to source Idea (idea_id)
  - State: TITLE_V0
  - Timestamps (created_at, updated_at)

- 10 Title objects (one per Story):
  - FK reference to Story (story_id)
  - Version: 0 (initial version)
  - Text from generated title variant

- Title variants (10 options) with diverse styles:
  - **Direct**: Straightforward, clear title
  - **Question**: Poses a question to engage readers
  - **How-to**: Action-oriented, instructional
  - **Curiosity**: Intriguing, creates interest
  - **Authoritative**: Expert perspective, comprehensive
  - **Listicle**: Number-based, digestible format
  - **Problem-Solution**: Addresses challenges and solutions
  - **Comparison**: Contrasts different approaches
  - **Ultimate-Guide**: Comprehensive resource positioning
  - **Benefit**: Value proposition, reader-focused

- Associated metadata (length, keywords, style, score)

## Usage

### Basic Usage (In-Memory)

```python
from T.Title.From.Idea import create_stories_from_idea
from T.Idea.Model.src.idea import Idea, IdeaStatus

# Create an idea
idea = Idea(
    title="The Future of AI",
    concept="An exploration of AI trends and their impact",
    status=IdeaStatus.DRAFT
)

# Create stories with titles
result = create_stories_from_idea(idea)

print(f"Created {result.count} stories")
for story, title in result.get_story_title_pairs():
    print(f"Story #{story.id}: {title.text}")
```

### With Database Persistence

```python
import sqlite3
from T.Title.From.Idea import StoryTitleService
from T.Idea.Model.src.idea import Idea, IdeaStatus

# Set up database connection
conn = sqlite3.connect("prismq.db")
conn.row_factory = sqlite3.Row

# Create service and ensure tables exist
service = StoryTitleService(conn)
service.ensure_tables_exist()

# Create an idea
idea = Idea(
    title="Blockchain Technology",
    concept="Understanding decentralized systems",
    status=IdeaStatus.DRAFT
)

# Create stories with titles (persisted to database)
result = service.create_stories_with_titles(idea)

# Stories and Titles are now in the database
print(f"Created {result.count} stories with database persistence")
```

## Next Stage

After stories and titles are created, they are used in:
- **Stage 3**: Script.FromIdea (uses Title v0 and Idea as context)
- **Stage 4**: Review.Title.ByScript (reviews Title v0 against Script v0)

## Module Exports

- `TitleGenerator`: Generate title variants from an Idea
- `TitleVariant`: Data class for title variant
- `TitleConfig`: Configuration for title generation
- `generate_titles_from_idea`: Convenience function for title generation
- `StoryTitleService`: Service for creating Stories with Titles
- `StoryTitleResult`: Result container for created Stories and Titles
- `create_stories_from_idea`: Convenience function for Story+Title creation

## Module Metadata

**[→ View From/Idea/_meta/docs/](./_meta/docs/)**
**[→ View From/Idea/_meta/examples/](./_meta/examples/)**
**[→ View From/Idea/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Title](../../README.md)** | **[→ Title/_meta](../../_meta/)**
