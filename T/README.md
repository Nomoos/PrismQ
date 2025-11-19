# T - Text Generation Pipeline

**Namespace**: `PrismQ.T`

This module handles the complete text generation workflow from initial idea inspiration through to published text content.

## Purpose

The Text Generation pipeline transforms creative inspiration into polished, published text content optimized for various platforms. This is the **first stage** of the sequential progressive enrichment workflow, where published text serves as the source material for subsequent audio and video production.

## Workflow Stages

```
IdeaInspiration → Idea (Outline → Skeleton → Title) → Script (Draft → Review → Approved) → TextPublishing → PublishedText
```

## Modules

### IdeaInspiration
Initial creative spark - capturing ideas, topics, and inspiration for content.

### Idea
Structured idea development with progressive refinement:
- **Outline**: Detailed story/content map with key points and structure
- **Skeleton**: Brief 3-6 point framework holding the narrative
- **Title**: Short, punchy title that attracts attention and suggests genre/mood

### Script
Text development and quality assurance:
- **Draft**: Initial script writing with storytelling elements
- **Review**: Editorial review and feedback
- **Approved**: Final approved script ready for publication

### Text (Publishing)
Text publication and distribution:
- **TextPublishing**: Formatting and platform-specific optimization
- **PublishedText**: Live published content on platforms (Medium, Substack, Blog, LinkedIn, Twitter/X)

## Data Flow

Published text from this pipeline serves as the **source material** for the Audio Generation pipeline:

```
PrismQ.T.PublishedText → PrismQ.A.Voiceover
```

## Key Features

- **19 Storytelling Fields**: Comprehensive narrative structure support (premise, logline, hook, beat sheet, etc.)
- **Platform Optimization**: SEO, formatting, readability for text platforms
- **Quality Gates**: Review and approval stages ensure polished output
- **Fast Publication**: Hours to days from idea to published text
- **Analytics Integration**: Early metrics inform audio/video production

## Usage Examples

### Python Namespace
```python
from PrismQ.T.IdeaInspiration import capture_idea
from PrismQ.T.Idea import Outline, Skeleton, Title
from PrismQ.T.Script import Draft, Review, Approved
from PrismQ.T import TextPublishing
```

### State Transitions
```python
idea = Idea(status=IdeaStatus.OUTLINE)
# Work on outline...
idea.status = IdeaStatus.SKELETON
# Refine to skeleton...
idea.status = IdeaStatus.TITLE
# Add title...
idea.status = IdeaStatus.SCRIPT_DRAFT
```

## Target Platforms

- **Long-form**: Medium, Substack, Blog posts
- **Professional**: LinkedIn articles
- **Social**: Twitter/X threads, Reddit posts
- **SEO**: Search-optimized web content

## Outputs

- **Published Text**: Polished content ready for voiceover recording
- **Analytics**: Page views, time on page, scroll depth, search rankings
- **Source Material**: Stable text for Audio Generation pipeline

## Related Pipelines

- **Next Stage**: `PrismQ.A` (Audio Generation) - Uses published text for voiceover
- **Final Stage**: `PrismQ.V` (Video Generation) - Uses published audio for video scenes

---

*Part of the PrismQ sequential progressive enrichment workflow: Text → Audio → Video*
