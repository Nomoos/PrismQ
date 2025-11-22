# Title and Script Creation Workflow

**Complete workflow from idea inception to text publishing**

## Overview

This document provides a clear, step-by-step workflow for creating titles and script text in the PrismQ Text Generation Pipeline (T module). The workflow starts with **Idea.Creation** (initial idea formation) and ends with **Publishing** (text publication).

## Complete Workflow Path

```
┌─────────────────────────────────────────────────────────────┐
│              Idea Generation (Two Sources)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Path 1: Automated from Inspiration                         │
│  Idea.Inspiration → Idea.Fusion → List of Candidate Ideas   │
│  (combines multiple inspirations)                           │
│                                                              │
│  Path 2: Manual Creation                                    │
│  Idea.Creation → List of Candidate Ideas                    │
│  (direct manual input)                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
        ↓
    AI Scoring & Selection
    (picks best idea from list)
        ↓
    ┌───────────────────────────────────┐
    │   Idea Processing Module          │
    │                                   │
    │   1. Model                        │
    │      └─→ Data structure & storage │
    │           ↓                       │
    │   2. Outline                      │
    │      └─→ Structure development    │
    │           ↓                       │
    │   3. Title                        │
    │      └─→ Title creation           │
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

### Stage 0A: Idea.Inspiration (Entry Point - Automated Path)
**Location:** `T/Idea/Inspiration`  
**Purpose:** Collect and manage content ideas from various sources

**Activities:**
- Content idea collection from external sources
- Initial concept scoring and classification
- Platform and audience targeting
- Source tracking and attribution

**Key Deliverables:**
- Raw inspiration data
- Source metadata
- Initial scoring metrics
- Platform tags

**Quality Gates:**
- Source is valid and reliable
- Concept has potential value
- Metadata is complete

**Transitions to:** Idea.Fusion

---

### Stage 0B: Idea.Fusion (Automated Path)
**Location:** `T/Idea/Fusion`  
**Purpose:** Combine multiple inspirations into candidate ideas

**Activities:**
- Analyze multiple Idea.Inspiration sources
- Identify common themes and patterns
- Merge complementary concepts
- Generate fusion variants
- Create list of candidate ideas

**Key Deliverables:**
- List of fused idea candidates
- Fusion rationale for each candidate
- Combined metadata
- Scoring for each candidate

**Quality Gates:**
- Fused ideas are coherent
- Multiple inspirations properly integrated
- Each candidate is viable

**Transitions to:** AI Scoring & Selection

---

### Stage 0C: Idea.Creation (Entry Point - Manual Path)
**Location:** `T/Idea/Creation`  
**Purpose:** Manually create idea concepts

**Activities:**
- Define the core concept and purpose
- Identify theme and emotional impact
- Specify target audience and demographics
- Clarify content goals and objectives
- Create list of candidate ideas

**Key Deliverables:**
- Manually created idea candidates
- Purpose definition
- Target audience profile
- Initial idea metadata

**Quality Gates:**
- Concept is clearly defined
- Purpose aligns with content strategy
- Target audience is identified

**Transitions to:** AI Scoring & Selection

---

### Stage 0D: AI Scoring & Selection
**Purpose:** Select the best idea from candidate list for processing

**Activities:**
- Score all candidate ideas using AI
- Evaluate viability, potential, and alignment
- Compare candidates against criteria
- Select top-ranked idea for processing
- Archive non-selected candidates

**Key Deliverables:**
- Selected idea for processing
- Scoring report for all candidates
- Selection rationale

**Quality Gates:**
- Scoring algorithm executed successfully
- Selection criteria met
- Selected idea has highest score

**Transitions to:** Idea.Model

---

### Stage 1: Idea.Model
**Location:** `T/Idea/Model`  
**Purpose:** Store and structure the selected idea

**Activities:**
- Initialize the Idea data model
- Store idea in database
- Structure metadata and attributes
- Link to source inspirations (if applicable)
- Prepare for outline development

**Key Deliverables:**
- Structured idea data model
- Database record
- Linked metadata
- Unique identifier

**Quality Gates:**
- Data model is complete
- All required fields populated
- Database integrity maintained

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

**Transitions to:** Title Creation (T/Title)

---

### Stage 3: Title Creation
**Location:** `T/Title/FromIdea`  
**Purpose:** Create initial title from idea (v1)

**Activities:**
- Generate title options from idea
- Consider SEO and engagement factors
- Create multiple title variants
- Store variants with idea reference

**Key Deliverables:**
- Title v1 variants (3-5 options)
- Associated metadata (length, keywords, style)
- Link to source idea

**Quality Gates:**
- Title is compelling and clear
- SEO keywords integrated
- Length appropriate for target platforms

**Transitions to:** Script Creation (T/Script)

---

### Stage 4: Script Creation
**Location:** `T/Script/FromIdeaAndTitle`  
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

### Stage 5: ScriptReview
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

### Stage 6: ScriptApproved
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

### Stage 7: TextPublishing
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

### Stage 8: PublishedText (End State)
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

### Automated Path (From Inspiration)
```
Idea.Inspiration → Idea.Fusion → [Candidate List] → 
AI Scoring → Idea.Model → Idea.Outline → 
Title.FromIdea → Script.FromIdeaAndTitle → 
ScriptReview → ScriptApproved → TextPublishing → PublishedText ✓
```

### Manual Path (Direct Creation)
```
Idea.Creation → [Candidate List] → AI Scoring → 
Idea.Model → Idea.Outline → Title.FromIdea → 
Script.FromIdeaAndTitle → ScriptReview → ScriptApproved → 
TextPublishing → PublishedText ✓
```

### With Script Revisions
```
... → Title.FromIdea → Script.FromIdeaAndTitle → 
ScriptReview → Script.FromOriginalScriptAndReviewAndTitle (v2) → 
ScriptReview → ScriptApproved → TextPublishing → PublishedText ✓
```

### With Title & Script Improvements
```
... → Title.FromIdea (v1) → Script.FromIdeaAndTitle (v1) → 
Reviews → Title.FromOriginalTitleAndReviewAndScript (v2) → 
Script.FromOriginalScriptAndReviewAndTitle (v2) → 
ScriptApproved → TextPublishing → PublishedText ✓
```

## State Characteristics

### Entry Points
- **Idea.Inspiration** - Automated entry via inspiration collection (feeds into Fusion)
- **Idea.Creation** - Manual entry via direct idea creation

### Fusion & Selection
- **Idea.Fusion** - Combines multiple inspirations into candidate list
- **AI Scoring** - Selects best idea from candidate list for processing

### Idea Processing States
- **Idea.Model** - Data structure and storage
- **Idea.Outline** - Content structure development

### Review Gates
- **ScriptReview** - Major quality checkpoint with multiple review dimensions

### Terminal State (for Text Pipeline)
- **PublishedText** - End of text-only workflow

## Module Cross-References

### T/Idea Module
- **Inspiration**: External idea collection from various sources
- **Fusion**: Combines multiple inspirations into candidate ideas
- **Creation**: Manual idea creation
- **Model**: Core data structure for selected ideas
- **Outline**: Content structure development

### T/Title Module
- **FromIdea**: Initial title creation from idea (v1)
- **FromOriginalTitleAndReviewAndScript**: Title improvements (v2+)

### T/Script Module
- **FromIdeaAndTitle**: Initial script creation from idea and title (v1)
- **FromOriginalScriptAndReviewAndTitle**: Script improvements (v2+)
- **Writer**: AI-powered script optimization support

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
1. **Automated Path**: Collect quality inspirations in **Idea.Inspiration**, let **Idea.Fusion** combine them
2. **Manual Path**: Create well-defined ideas in **Idea.Creation**
3. Trust **AI Scoring** to select the best candidate from the list
4. Develop comprehensive outline in **Idea.Outline**
5. Create initial title in **Title.FromIdea** before moving to script

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
- Idea.Inspiration → Idea.Fusion
- Idea.Fusion → AI Scoring & Selection
- AI Scoring → Idea.Model
- Idea.Model → Idea.Outline
- Publishing to PublishedText

### Manual Approvals Required
- ScriptReview → ScriptApproved
- ScriptApproved → TextPublishing

### AI-Assisted Stages
- Script/Writer (AI optimization)
- Review modules (AI-powered review)
- Publishing/SEO (keyword research)

## Related Documentation

- **[Main Workflow](../_meta/WORKFLOW.md)** - Complete PrismQ state machine
- **[T Module Overview](./README.md)** - Text pipeline documentation
- **[T/Idea README](./Idea/README.md)** - Idea module details
- **[T/Title README](./Title/README.md)** - Title creation details
- **[T/Script README](./Script/README.md)** - Script development details
- **[T/Publishing README](./Publishing/README.md)** - Publishing details

---

**Version:** 1.0  
**Last Updated:** 2025-11-20  
**Part of:** PrismQ.T Text Generation Pipeline
