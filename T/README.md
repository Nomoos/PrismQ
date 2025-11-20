# T - Text Generation Pipeline

**Namespace**: `PrismQ.T`

This module handles the complete text generation workflow from initial idea inspiration through to published text content, using a granular quality-focused state machine.

## Purpose

The Text Generation pipeline transforms creative inspiration into polished, published text content optimized for various platforms. This is the **first stage** of the sequential progressive enrichment workflow, where published text serves as the source material for subsequent audio and video production.

## State Machine Workflow

The text generation pipeline uses a **17-state quality-focused workflow** with dedicated quality review gates:

```
Idea → IdeaReview → Outline → TitleDraft →
ScriptDraft → ContentReview → Editing →
GrammarReview → ConsistencyCheck → ToneCheck → ReadabilityReview →
Finalization → TitleOptimization → Publishing → Archived
```

**Central Revision Hub**: `ScriptImprovements` enables loops back to `Editing` or `TitleRefinement` when quality issues are found.

## State-Based Folder Structure

Each state in the workflow has its own folder with tools, operations, and documentation:

### Concept Phase (4 states)
- **[Idea](./Idea/)** - Initial concept (includes existing Idea model)
- **[IdeaReview](./IdeaReview/)** - Review and validate concept
- **[Outline](./Outline/)** - Create structured outline
- **[TitleDraft](./TitleDraft/)** - Draft initial title

### Script Creation (2 states)
- **[ScriptDraft](./ScriptDraft/)** - Write initial script
- **[ContentReview](./ContentReview/)** - Review content structure and flow

### Editing (1 state)
- **[Editing](./Editing/)** - Edit for clarity and coherence

### Quality Review Pipeline (4 states)
- **[GrammarReview](./GrammarReview/)** - Check grammar, spelling, punctuation
- **[ConsistencyCheck](./ConsistencyCheck/)** - Verify consistency (names, facts, timeline)
- **[ToneCheck](./ToneCheck/)** - Validate tone and style match
- **[ReadabilityReview](./ReadabilityReview/)** - Ensure suitable for voiceover

### Improvement Hub (1 state)
- **[ScriptImprovements](./ScriptImprovements/)** - Central hub for revisions

### Title Refinement (2 states)
- **[TitleRefinement](./TitleRefinement/)** - Align title with final script
- **[TitleOptimization](./TitleOptimization/)** - Optimize for engagement/SEO

### Final Phase (2 states)
- **[Finalization](./Finalization/)** - Final preparation
- **[Publishing](./Publishing/)** - Publish to platform

### Terminal (1 state)
- **[Archived](./Archived/)** - Completed or terminated

## State Machine Model

The state machine is implemented in **[Story](./Story/)** module:

```python
from PrismQ.T.Story.Model.src.story import Story, StoryState

# Create story from idea
story = Story.from_idea(idea, created_by="writer_1")

# Progress through quality gates
story.transition_to(StoryState.IDEA_REVIEW)
story.transition_to(StoryState.OUTLINE)
story.transition_to(StoryState.TITLE_DRAFT)
story.transition_to(StoryState.SCRIPT_DRAFT)
story.transition_to(StoryState.CONTENT_REVIEW)
story.transition_to(StoryState.EDITING)

# Quality review pipeline
story.transition_to(StoryState.GRAMMAR_REVIEW)
story.transition_to(StoryState.CONSISTENCY_CHECK)
story.transition_to(StoryState.TONE_CHECK)
story.transition_to(StoryState.READABILITY_REVIEW)

# Finalization and publishing
story.transition_to(StoryState.FINALIZATION)
story.transition_to(StoryState.TITLE_OPTIMIZATION)
story.transition_to(StoryState.PUBLISHING)
story.transition_to(StoryState.ARCHIVED)
```

## Quality Gates

Each review state has specific responsibilities:

- **GrammarReview**: Grammar, spelling, punctuation correctness
- **ConsistencyCheck**: Names, facts, timeline consistency
- **ToneCheck**: Tone and style alignment with genre
- **ReadabilityReview**: Voiceover suitability and pacing

Failed quality gates route to **ScriptImprovements** for revision loops.

## Data Flow

Published text from this pipeline serves as the **source material** for the Audio Generation pipeline:

```
PrismQ.T.Publishing → PrismQ.T.Archived
                 ↓
         Published Content
                 ↓
    PrismQ.A.Voiceover (next stage)
```

## Key Features

- **17 Quality-Focused States**: Granular control over production workflow
- **Quality Review Pipeline**: 4 dedicated review gates (Grammar, Consistency, Tone, Readability)
- **Revision Loops**: Central ScriptImprovements hub for quality iterations
- **State Machine Enforcement**: Only valid transitions allowed
- **Complete Audit Trail**: State history tracks all transitions
- **Platform Optimization**: SEO, formatting, readability for text platforms
- **Fast Publication**: Hours to days from idea to published text

## Modules

### [IdeaInspiration](./IdeaInspiration/)
Initial creative spark - capturing ideas, topics, and inspiration for content.

### [Idea](./Idea/)
Structured idea development with the Idea model supporting the initial concept phase.

### [Story](./Story/)
State machine coordinator managing the complete production workflow from Idea to Publishing.

## Usage Examples

### State Machine Operations
```python
from PrismQ.T.Story.Model.src.story import Story, StoryState
from PrismQ.T.Story.Model.src.story_db import StoryDatabase

# Create and progress story
story = Story.from_idea(idea)
story.transition_to(StoryState.IDEA_REVIEW)

# Check valid transitions
valid_states = story.get_valid_transitions()

# Quality gate with revision loop
story.transition_to(StoryState.GRAMMAR_REVIEW)
if grammar_issues_found:
    story.transition_to(StoryState.SCRIPT_IMPROVEMENTS, notes="Grammar issues")
    story.transition_to(StoryState.EDITING)  # Loop back

# Database operations
db = StoryDatabase("stories.db")
db.connect()
stories = db.get_stories_by_state(StoryState.EDITING)
```

## Target Platforms

- **Long-form**: Medium, Substack, Blog posts
- **Professional**: LinkedIn articles
- **Social**: Twitter/X threads, Reddit posts (especially AITA, NoSleep)
- **SEO**: Search-optimized web content

## Outputs

- **Published Text**: Polished content ready for voiceover recording
- **Analytics**: Page views, time on page, scroll depth, search rankings
- **Source Material**: Stable text for Audio Generation pipeline
- **Quality Reports**: Grammar, consistency, tone, readability assessments

## Related Pipelines

- **Next Stage**: `PrismQ.A` (Audio Generation) - Uses published text for voiceover
- **Final Stage**: `PrismQ.V` (Video Generation) - Uses published audio for video scenes

---

*Part of the PrismQ sequential progressive enrichment workflow: Text → Audio → Video*
