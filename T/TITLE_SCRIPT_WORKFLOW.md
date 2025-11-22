# Title and Script Creation Workflow

**Complete workflow from idea inception to text publishing**

## Overview

This document provides a clear, step-by-step workflow for creating titles and script text in the PrismQ Text Generation Pipeline (T module). The workflow starts with **Idea.Creation** (initial idea formation) and ends with **Publishing** (text publication).

## Complete Workflow Path

```
IdeaInspiration (External)
        ↓
    ┌───────────────────────────────────┐
    │   Idea Module (Composite State)   │
    │                                   │
    │   1. Creation                     │
    │      └─→ Idea formation           │
    │           ↓                       │
    │   2. Outline                      │
    │      └─→ Structure development    │
    │           ↓                       │
    │   3. Skeleton                     │
    │      └─→ Basic framework          │
    │           ↓                       │
    │   4. Title                        │
    │      └─→ Title finalization       │
    └───────────────────────────────────┘
        ↓
    ScriptDraft
        ↓
    ScriptReview
        ↓
    ScriptApproved
        ↓
    TextPublishing
        ↓
    PublishedText ✓
```

## Detailed Workflow Stages

### Stage 0: IdeaInspiration (Entry Point)
**External State** - Before entering the T module workflow

- Content idea collection from various sources
- Initial concept scoring and classification
- Platform and audience targeting

**Transitions to:** Idea.Creation

---

### Stage 1: Idea.Creation
**Location:** `T/Idea` (via Model)  
**Purpose:** Transform inspiration into concrete idea concept

**Activities:**
- Define the core concept and purpose
- Identify theme and emotional impact
- Specify target audience and demographics
- Clarify content goals and objectives
- Initialize the Idea data model

**Key Deliverables:**
- Idea concept statement
- Purpose definition
- Target audience profile
- Initial idea metadata

**Quality Gates:**
- Concept is clearly defined
- Purpose aligns with content strategy
- Target audience is identified

**Transitions to:** Idea.Outline

---

### Stage 2: Idea.Outline
**Location:** `T/Idea/Outline`  
**Purpose:** Develop structured content outline

**Activities:**
- Organize main topics and subtopics
- Define content hierarchy and flow
- Plan section structure
- Identify key message points
- Create narrative arc

**Key Deliverables:**
- Complete content outline
- Topic hierarchy
- Section breakdown
- Flow diagram

**Quality Gates:**
- All major topics covered
- Logical flow established
- Depth appropriate for target audience

**Transitions to:** Idea.Skeleton

---

### Stage 3: Idea.Skeleton
**Location:** `T/Idea` (conceptual sub-state)  
**Purpose:** Create basic structural framework

**Activities:**
- Define section templates
- Establish content patterns
- Set structural guidelines
- Create framework for script development

**Key Deliverables:**
- Structural framework
- Section templates
- Content patterns
- Development guidelines

**Quality Gates:**
- Framework supports outline structure
- Templates are reusable
- Structure is production-ready

**Transitions to:** Idea.Title

---

### Stage 4: Idea.Title
**Location:** `T/Title`  
**Purpose:** Create and optimize final title

**Activities:**
- Generate title options (Title/Draft)
- Test and optimize titles (Title/Optimization)
- Refine based on testing (Title/Refinement)
- Finalize SEO-optimized title

**Sub-workflow:**
```
Title.Draft → Title.Optimization → Title.Refinement → Finalized Title
```

**Key Deliverables:**
- Finalized title
- Title alternatives
- SEO metadata
- Click-through optimization data

**Quality Gates:**
- Title is compelling and clear
- SEO keywords integrated
- Length appropriate for target platforms
- A/B testing completed (if applicable)

**Transitions to:** ScriptDraft (exits Idea composite state)

---

### Stage 5: ScriptDraft
**Location:** `T/Script/Draft`  
**Purpose:** Write initial script from structured idea

**Activities:**
- Transform outline into full narrative
- Write in natural spoken form
- Include dialogue and narration
- Ensure conversational tone
- Structure for audio/video delivery

**Key Deliverables:**
- Complete script draft
- Narrative structure
- Dialogue text
- Stage directions (if applicable)

**Quality Gates:**
- All outline points covered
- Script flows naturally
- Length appropriate for format
- Tone matches target audience

**Transitions to:** ScriptReview

---

### Stage 6: ScriptReview
**Location:** `T/Review` (various review modules)  
**Purpose:** Review and enhance script quality

**Activities:**
- Grammar and spelling review (Review/Grammar)
- Readability optimization (Review/Readability)
- Tone and voice consistency (Review/Tone)
- Content accuracy validation (Review/Content)
- Style consistency check (Review/Consistency)
- Final editing pass (Review/Editing)

**Key Deliverables:**
- Reviewed script
- Correction notes
- Quality assessment
- Enhancement recommendations

**Quality Gates:**
- No grammar or spelling errors
- Readability score meets target
- Tone is consistent
- Content is accurate
- Style is cohesive

**Transitions to:** 
- ScriptApproved (if quality gates passed)
- ScriptDraft (if major revisions needed)
- Idea (if fundamental concept issues found)

---

### Stage 7: ScriptApproved
**Location:** `T/Script` (approved state)  
**Purpose:** Lock approved script for publishing

**Activities:**
- Final approval sign-off
- Version locking
- Metadata finalization
- Publishing preparation

**Key Deliverables:**
- Approved script (locked version)
- Final metadata
- Publishing checklist

**Quality Gates:**
- All stakeholders approved
- Version locked
- Ready for publishing pipeline

**Transitions to:** TextPublishing

---

### Stage 8: TextPublishing
**Location:** `T/Publishing`  
**Purpose:** Prepare and publish text content

**Activities:**
- SEO optimization (Publishing/SEO)
  - Keyword research (SEO/Keywords)
  - Tag optimization (SEO/Tags)
  - Category assignment (SEO/Categories)
- Final formatting (Publishing/Finalization)
- Platform-specific preparation
- Publication execution

**Key Deliverables:**
- SEO-optimized text
- Platform-specific formats
- Metadata packages
- Published URLs

**Quality Gates:**
- SEO metadata complete
- All platforms prepared
- Publishing checklist verified

**Transitions to:** PublishedText

---

### Stage 9: PublishedText (End State)
**Status:** ✓ Published  
**Purpose:** Live text content available to audience

**Outcomes:**
- Content is publicly available
- Analytics tracking active
- Ready for audio pipeline (if continuing)
- Workflow complete for text-only path

**Next Steps:**
- Monitor analytics
- Gather audience feedback
- Consider audio production (A pipeline)
- Archive if workflow complete

---

## Quick Reference Paths

### Text-Only Path (Complete)
```
Idea.Creation → Outline → Skeleton → Title → 
ScriptDraft → ScriptReview → ScriptApproved → 
TextPublishing → PublishedText ✓
```

### With Script Revisions
```
Idea.Creation → ... → Title → ScriptDraft → 
ScriptReview → ScriptDraft (revision) → 
ScriptReview → ScriptApproved → TextPublishing → PublishedText ✓
```

### With Idea Refinement
```
Idea.Creation → ... → ScriptDraft → 
ScriptReview → Idea (refinement) → 
Idea.Outline → ... → ScriptDraft → ... → PublishedText ✓
```

## State Characteristics

### Entry Points
- **Idea.Creation** - Primary entry into T module workflow
- **IdeaInspiration** - External inspiration collection (feeds into Creation)

### Composite States
- **Idea** - Contains sequential sub-states (Creation → Outline → Skeleton → Title)

### Review Gates
- **ScriptReview** - Major quality checkpoint with multiple review dimensions

### Terminal State (for Text Pipeline)
- **PublishedText** - End of text-only workflow

## Module Cross-References

### T/Idea Module
- **Creation**: Initial idea formation (uses Model structure)
- **Model**: Core data structure for ideas
- **Outline**: Content structure development
- **Review**: Idea validation and assessment

### T/Title Module
- **Draft**: Initial title creation
- **Optimization**: A/B testing and optimization
- **Refinement**: Final title polish

### T/Script Module
- **Draft**: Initial script writing
- **Writer**: AI-powered script optimization
- **Improvements**: Script enhancement
- **Optimization**: Final script optimization

### T/Review Module
- **Grammar**: Grammar and syntax review
- **Readability**: Reading level optimization
- **Tone**: Voice consistency
- **Content**: Accuracy validation
- **Consistency**: Style checking
- **Editing**: Final editing pass

### T/Publishing Module
- **SEO**: Search engine optimization
  - Keywords, Tags, Categories
- **Finalization**: Publication preparation

## Best Practices

### Starting the Workflow
1. Begin with clear idea formation in **Idea.Creation**
2. Take time to develop comprehensive outline
3. Create solid skeleton before finalizing title
4. Finalize title before moving to script

### During Script Development
1. Use outline as guide for script structure
2. Write for spoken delivery, not just reading
3. Review early and often
4. Don't skip quality gates

### Before Publishing
1. Complete all review dimensions
2. Verify SEO optimization
3. Check platform-specific requirements
4. Test formatting on target platforms

### Success Metrics
- **Time to Publish**: Track time from Creation to PublishedText
- **Revision Count**: Monitor how many review cycles needed
- **Quality Scores**: Track review dimension scores
- **SEO Performance**: Measure keyword rankings and traffic

## Integration with Other Pipelines

### Audio Pipeline (A)
- Uses **PublishedText** as source for voiceover
- Script serves as narration foundation
- Title becomes episode/track title

### Video Pipeline (V)
- Uses published audio from A pipeline
- Script informs visual scene planning
- Title becomes video title

### Client/TaskManager
- Tracks workflow progress
- Assigns tasks at each stage
- Monitors quality gates
- Reports metrics and bottlenecks

## Workflow Automation

### Automated Transitions
- Idea sub-states (Creation → Outline → Skeleton → Title)
- Publishing to PublishedText

### Manual Approvals Required
- ScriptReview → ScriptApproved
- ScriptApproved → TextPublishing

### AI-Assisted Stages
- Script/Writer (AI optimization)
- Review modules (AI-powered review)
- Publishing/SEO (keyword research)

## Related Documentation

- **[Main Workflow](../WORKFLOW.md)** - Complete PrismQ state machine
- **[T Module Overview](./README.md)** - Text pipeline documentation
- **[T/Idea README](./Idea/README.md)** - Idea module details
- **[T/Title README](./Title/README.md)** - Title creation details
- **[T/Script README](./Script/README.md)** - Script development details
- **[T/Publishing README](./Publishing/README.md)** - Publishing details

---

**Version:** 1.0  
**Last Updated:** 2025-11-20  
**Part of:** PrismQ.T Text Generation Pipeline
