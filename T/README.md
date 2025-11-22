# T - Text Generation Pipeline

**Namespace**: `PrismQ.T`

The Text Generation Pipeline is the foundation of the PrismQ content workflow. It transforms initial ideas into high-quality, published text content optimized for blogs, articles, and social media platforms.

## 📋 Quick Start

**[→ Title & Script Creation Workflow](./TITLE_SCRIPT_WORKFLOW.md)** - Complete step-by-step guide from Idea.Creation to Publishing

## Purpose

This pipeline handles the complete text content lifecycle from inspiration through ideation, scripting, review, and publication. Published text from this pipeline serves as the **foundation** for subsequent audio and video production.

## Sequential Workflow Position

```
IdeaInspiration → Text Pipeline → PublishedText
    ↓                                  ↓
Analytics Feedback              Audio Pipeline (A)
```

## 📁 Modules

### [Idea](./Idea/README.md)
**Idea development and structuring**

Transform inspiration into structured content concepts with clear outlines and titles.

- **[Model](./Idea/Model/)** - Core data model and structure
- **[Outline](./Idea/Outline/)** - Content outline development
- **[Review](./Idea/Review/)** - Idea validation and review

**[→ Explore Idea Module](./Idea/README.md)**

---

### [Script](./Script/)
**Script drafting and refinement**

Develop and refine scripts through iterative drafting and optimization.

- **[Draft](./Script/Draft/)** - Initial script writing
- **[Improvements](./Script/Improvements/)** - Script enhancement
- **[Optimization](./Script/Optimization/)** - Script optimization

**Submodule Navigation:**
- [Draft README](./Script/Draft/README.md)
- [Improvements README](./Script/Improvements/README.md)
- [Optimization README](./Script/Optimization/README.md)

---

### [Title](./Title/)
**Title creation and optimization**

Create compelling, SEO-optimized titles through testing and refinement.

- **[Draft](./Title/Draft/)** - Initial title creation
- **[Optimization](./Title/Optimization/)** - Title A/B testing
- **[Refinement](./Title/Refinement/)** - Final title polish

**Submodule Navigation:**
- [Draft README](./Title/Draft/README.md)
- [Optimization README](./Title/Optimization/README.md)
- [Refinement README](./Title/Refinement/README.md)

---

### [Review](./Review/)
**Content review and editing**

Multi-dimensional content quality review and enhancement.

- **[Grammar](./Review/Grammar/)** - Grammar and syntax
- **[Readability](./Review/Readability/)** - Reading level optimization
- **[Tone](./Review/Tone/)** - Tone and voice consistency
- **[Content](./Review/Content/)** - Content accuracy and relevance
- **[Consistency](./Review/Consistency/)** - Style consistency
- **[Editing](./Review/Editing/)** - Final editing pass

**Submodule Navigation:**
- [Grammar README](./Review/Grammar/README.md)
- [Readability README](./Review/Readability/README.md)
- [Tone README](./Review/Tone/README.md)
- [Content README](./Review/Content/README.md)
- [Consistency README](./Review/Consistency/README.md)
- [Editing README](./Review/Editing/README.md)

---

### [Publishing](./Publishing/)
**Text content publication**

Prepare and publish text content with SEO optimization and platform-specific formatting.

- **[SEO](./Publishing/SEO/)** - Search engine optimization
  - [Keywords](./Publishing/SEO/Keywords/) - Keyword research and targeting
  - [Tags](./Publishing/SEO/Tags/) - Tag optimization
  - [Categories](./Publishing/SEO/Categories/) - Content categorization
- **[Finalization](./Publishing/Finalization/)** - Final publication preparation

**Submodule Navigation:**
- [SEO README](./Publishing/SEO/README.MD)
- [Finalization README](./Publishing/Finalization/README.md)

---

## 📖 Module Metadata

### Documentation
Technical documentation and implementation guides.

**[→ View T/_meta/docs/](./_meta/docs/)**

### Examples
Usage examples and sample implementations.

**[→ View T/_meta/examples/](./_meta/examples/)**

### Tests
Test suites and test data.

**[→ View T/_meta/tests/](./_meta/tests/)**

---

## Workflow Stages

```
IdeaInspiration
    ↓
Idea (Creation → Outline → Skeleton → Title)
    ↓
ScriptDraft
    ↓
ScriptReview (Review modules)
    ↓
ScriptApproved
    ↓
TextPublishing (Publishing modules)
    ↓
PublishedText → Audio Pipeline (A)
```

## Key Features

- **Idea Management**: Structured approach from inspiration to concept
- **Script Development**: Iterative drafting and improvement
- **Quality Review**: Multi-dimensional review process
- **SEO Optimization**: Keyword research, tags, and metadata
- **Fast Publication**: Hours to days from idea to published text
- **Foundation Format**: Serves as source for audio production

## Target Platforms

- **Blogs**: Medium, Substack, WordPress
- **Social Media**: LinkedIn, Twitter/X
- **Content Platforms**: Dev.to, Hashnode
- **Documentation**: GitHub Pages, GitBook

## Usage Examples

### Python Namespace
```python
from PrismQ.T.Idea import Outline, Model
from PrismQ.T.Script import Draft, Improvements
from PrismQ.T.Publishing import SEO, Finalization
```

### State Transitions
```python
content = Content(status=ContentStatus.IDEA_OUTLINE)
# Develop outline...
content.status = ContentStatus.SCRIPT_DRAFT
# Write script...
content.status = ContentStatus.SCRIPT_REVIEW
# Review and improve...
content.status = ContentStatus.TEXT_PUBLISHING
```

## Outputs

- **Published Text**: SEO-optimized text content
- **Metadata**: Keywords, tags, categories
- **Analytics**: Views, engagement, SEO performance
- **Source Material**: Foundation for Audio Pipeline (A)

## Related Pipelines

- **Next Stage**: `PrismQ.A` (Audio Generation) - Uses published text for voiceover
- **Final Stage**: `PrismQ.V` (Video Generation) - Uses text and audio for video
- **Client**: `PrismQ.Client` (Task Management) - Workflow coordination

---

## Navigation

**[← Back to Main](../README.md)** | **[Audio Pipeline →](../A/README.md)** | **[Video Pipeline →](../V/README.md)** | **[Workflow](../WORKFLOW.md)**

---

*Part of the PrismQ sequential progressive enrichment workflow: Text → Audio → Video*
