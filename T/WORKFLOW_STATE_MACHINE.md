# PrismQ.T Workflow State Machine

**Visual State Diagram for Detailed Text Generation Workflow**

## State Machine Diagram

```mermaid
stateDiagram-v2
    [*] --> IdeaCreation
    
    IdeaCreation --> TitleFromIdea
    TitleFromIdea --> ScriptFromTitleIdea
    ScriptFromTitleIdea --> ReviewTitleByScriptIdea
    
    ReviewTitleByScriptIdea --> ReviewScriptByTitleIdea
    
    ReviewScriptByTitleIdea --> ReviewTitleByScript
    
    ReviewTitleByScript --> TitleFromScriptReviewTitle
    ReviewTitleByScript --> ReviewScriptByTitle
    
    TitleFromScriptReviewTitle --> ScriptFromTitleReviewScript
    
    ScriptFromTitleReviewScript --> ReviewTitleByScript
    
    ReviewScriptByTitle --> ScriptFromTitleReviewScript
    ReviewScriptByTitle --> ReviewScriptGrammar
    
    ReviewScriptGrammar --> ReviewScriptTone
    ReviewScriptGrammar --> ScriptFromTitleReviewScript
    
    ReviewScriptTone --> ReviewScriptContent
    ReviewScriptTone --> ScriptFromTitleReviewScript
    
    ReviewScriptContent --> ReviewScriptConsistency
    ReviewScriptContent --> ScriptFromTitleReviewScript
    
    ReviewScriptConsistency --> ReviewScriptEditing
    ReviewScriptConsistency --> ScriptFromTitleReviewScript
    
    ReviewScriptEditing --> ReviewTitleReadability
    ReviewScriptEditing --> ScriptFromTitleReviewScript
    
    ReviewTitleReadability --> ReviewScriptReadability
    ReviewTitleReadability --> TitleFromScriptReviewTitle
    
    ReviewScriptReadability --> StoryReview
    ReviewScriptReadability --> ScriptFromTitleReviewScript
    
    StoryReview --> StoryPolish
    StoryReview --> Publishing
    
    StoryPolish --> StoryReview
    
    Publishing --> [*]

    note right of IdeaCreation
        Stage 1: Initial idea capture
        Location: T/Idea/Creation/
    end note
    
    note right of TitleFromIdea
        Stage 2: Generate title v1
        Location: T/Title/FromIdea/
    end note
    
    note right of ScriptFromTitleIdea
        Stage 3: Generate script v1
        Location: T/Script/FromIdeaAndTitle/
    end note
    
    note right of ReviewTitleByScriptIdea
        Stage 4: Review title (no conditional)
        Always proceeds to Stage 5
    end note
    
    note right of ReviewScriptByTitleIdea
        Stage 5: Review script (no conditional)
        Always proceeds to Stage 6
    end note
    
    note right of ReviewScriptGrammar
        Stages 10-16: Local AI reviews
        All failures loop through
        Script Refinement → Title Review
    end note
    
    note right of StoryReview
        Stages 17-18: GPT Expert Review
        Final quality gate
        Iterates until accepted
    end note
```

## State Definitions

### Primary States

| State | Full Name | Stage | Location |
|-------|-----------|-------|----------|
| IdeaCreation | PrismQ.T.Idea.Creation | 1 | T/Idea/Creation/ |
| TitleFromIdea | PrismQ.T.Title.From.Idea | 2 | T/Title/FromIdea/ |
| ScriptFromTitleIdea | PrismQ.T.Script.From.Title.Idea | 3 | T/Script/FromIdeaAndTitle/ |
| ReviewTitleByScriptIdea | PrismQ.T.Review.Title.By.Script.Idea | 4 | T/Review/Title/ByScriptIdea/ |
| TitleFromScriptReviewTitle | PrismQ.T.Title.From.Script.Review.Title | 5 | T/Title/FromOriginalTitleAndReviewAndScript/ |
| ReviewScriptByTitleIdea | PrismQ.T.Review.Script.By.Title.Idea | 6 | T/Review/Script/ByTitleIdea/ |
| ScriptFromTitleReviewScript | PrismQ.T.Script.From.Title.Review.Script | 7 | T/Script/FromOriginalScriptAndReviewAndTitle/ |
| ReviewTitleByScript | PrismQ.T.Review.Title.By.Script | 8 | T/Review/Title/ByScript/ |
| ReviewScriptByTitle | PrismQ.T.Review.Script.By.Title | 9 | T/Review/Script/ByTitle/ |

### Quality Review States

| State | Full Name | Stage | Location |
|-------|-----------|-------|----------|
| ReviewScriptGrammar | PrismQ.T.Review.Script.Grammar | 10 | T/Review/Grammar/ |
| ReviewScriptTone | PrismQ.T.Review.Script.Tone | 11 | T/Review/Tone/ |
| ReviewScriptContent | PrismQ.T.Review.Script.Content | 12 | T/Review/Content/ |
| ReviewScriptConsistency | PrismQ.T.Review.Script.Consistency | 13 | T/Review/Consistency/ |
| ReviewScriptEditing | PrismQ.T.Review.Script.Editing | 14 | T/Review/Editing/ |
| ReviewTitleReadability | PrismQ.T.Review.Title.Readability | 15 | T/Review/Readability/ |
| ReviewScriptReadability | PrismQ.T.Review.Script.Readability | 16 | T/Review/Readability/ |

### Expert Review Loop States

| State | Full Name | Stage | Location |
|-------|-----------|-------|----------|
| StoryReview | PrismQ.T.Story.Review | 17 | T/Story/ExpertReview/ |
| StoryPolish | PrismQ.T.Story.Polish | 18 | T/Story/Polish/ or T/Story/ExpertPolish/ |

### Terminal State

| State | Full Name | Description |
|-------|-----------|-------------|
| Publishing | PrismQ.T.Publishing | Final stage leading to publication |

## State Transitions

### Linear Progression

Initial linear flow through the workflow:

```
IdeaCreation 
  → TitleFromIdea 
  → ScriptFromTitleIdea 
  → ReviewTitleByScriptIdea
```

### Conditional Branches

#### Title Review Branch
```
ReviewTitleByScriptIdea
  ├─ accepted → ReviewScriptByTitleIdea
  └─ not accepted → TitleFromScriptReviewTitle → ReviewScriptByTitleIdea
```

#### Script Review Branch
```
ReviewScriptByTitleIdea
  ├─ accepted → ReviewTitleByScript
  └─ not accepted → ScriptFromTitleReviewScript → ReviewTitleByScript
```

#### Title Re-Review Branch
```
ReviewTitleByScript
  ├─ accepted → ReviewScriptByTitle
  └─ not accepted → TitleFromScriptReviewTitle → ReviewScriptByTitle
```

#### Script Re-Review Branch
```
ReviewScriptByTitle
  ├─ accepted → QualityReviews (ReviewScriptGrammar)
  └─ not accepted → ScriptFromTitleReviewScript → ReviewScriptByTitle
```

### Quality Review Sequence

Sequential quality reviews with failure feedback:

```
QualityReviews:
  ReviewScriptGrammar
    ├─ passes → ReviewScriptTone
    └─ fails → ScriptFromTitleReviewScript
    
  ReviewScriptTone
    ├─ passes → ReviewScriptContent
    └─ fails → ScriptFromTitleReviewScript
    
  ReviewScriptContent
    ├─ passes → ReviewScriptConsistency
    └─ fails → ScriptFromTitleReviewScript
    
  ReviewScriptConsistency
    ├─ passes → ReviewScriptEditing
    └─ fails → ScriptFromTitleReviewScript
    
  ReviewScriptEditing
    ├─ passes → ReviewTitleReadability
    └─ fails → ScriptFromTitleReviewScript
    
  ReviewTitleReadability
    ├─ passes → ReviewScriptReadability
    └─ fails → TitleFromScriptReviewTitle
    
  ReviewScriptReadability
    ├─ passes → ExpertReviewLoop (StoryReview)
    └─ fails → ScriptFromTitleReviewScript
```

### Expert Review Loop

Iterative loop until expert acceptance:

```
ExpertReviewLoop:
  StoryReview
    ├─ accepted → Publishing
    └─ not accepted → StoryPolish → StoryReview (loop)
```

## Workflow Paths

### Ideal Path (All Reviews Pass First Time)

```
IdeaCreation
→ TitleFromIdea
→ ScriptFromTitleIdea
→ ReviewTitleByScriptIdea (accepted)
→ ReviewScriptByTitleIdea (accepted)
→ ReviewTitleByScript (accepted)
→ ReviewScriptByTitle (accepted)
→ ReviewScriptGrammar (passes)
→ ReviewScriptTone (passes)
→ ReviewScriptContent (passes)
→ ReviewScriptConsistency (passes)
→ ReviewScriptEditing (passes)
→ ReviewTitleReadability (passes)
→ ReviewScriptReadability (passes)
→ StoryReview (accepted)
→ Publishing
```

**Total Stages**: 14 stages

### Realistic Path (Some Reviews Require Refinement)

```
IdeaCreation
→ TitleFromIdea
→ ScriptFromTitleIdea
→ ReviewTitleByScriptIdea (not accepted)
→ TitleFromScriptReviewTitle
→ ReviewScriptByTitleIdea (accepted)
→ ReviewTitleByScript (accepted)
→ ReviewScriptByTitle (not accepted)
→ ScriptFromTitleReviewScript
→ ReviewScriptByTitle (accepted)
→ ReviewScriptGrammar (passes)
→ ReviewScriptTone (fails)
→ ScriptFromTitleReviewScript
→ ReviewScriptByTitle (accepted)
→ ReviewScriptGrammar (passes)
→ ReviewScriptTone (passes)
→ ReviewScriptContent (passes)
→ ReviewScriptConsistency (passes)
→ ReviewScriptEditing (passes)
→ ReviewTitleReadability (passes)
→ ReviewScriptReadability (passes)
→ StoryReview (not accepted)
→ StoryPolish
→ StoryReview (accepted)
→ Publishing
```

**Total Stages**: ~22 stages (including loops)

### Maximum Iteration Path

If every review initially fails, the workflow could involve significantly more iterations. The workflow is designed to converge through iterative improvements.

## Composite States

### QualityReviews Composite State

The QualityReviews state encapsulates 7 sequential review stages (10-16). This composite state:
- Has a single entry point (ReviewScriptGrammar)
- Has two exit conditions:
  - Success: All reviews pass → exits to StoryReview
  - Failure: Any review fails → exits to appropriate refinement stage
- Maintains internal sequential flow
- Represents the "quality gate" before expert review

### ExpertReviewLoop Composite State

The ExpertReviewLoop state encapsulates the final expert review cycle (17-18). This composite state:
- Has a single entry point (StoryReview)
- Has one exit condition: StoryReview accepted → Publishing
- Contains an internal loop: StoryReview → StoryPolish → StoryReview
- Represents the final quality gate before publication

## State Characteristics

### Entry Points
- **IdeaCreation**: The single entry point to the workflow

### Refinement States
States that improve artifacts based on feedback:
- **TitleFromScriptReviewTitle**: Title refinement (used multiple times)
- **ScriptFromTitleReviewScript**: Script refinement (used multiple times)
- **StoryPolish**: Expert-level polish

### Review States
States that evaluate quality and make accept/reject decisions:
- **ReviewTitleByScriptIdea**: Title review with full context
- **ReviewScriptByTitleIdea**: Script review with full context
- **ReviewTitleByScript**: Title review against script
- **ReviewScriptByTitle**: Script review against title
- **ReviewScriptGrammar**: Grammar validation
- **ReviewScriptTone**: Tone validation
- **ReviewScriptContent**: Content validation
- **ReviewScriptConsistency**: Consistency validation
- **ReviewScriptEditing**: Editing validation
- **ReviewTitleReadability**: Title readability validation
- **ReviewScriptReadability**: Script readability validation
- **StoryReview**: Expert holistic review

### Terminal State
- **Publishing**: End of workflow, leads to publication

## Quality Gates

### Gate 1: Title-Script Initial Alignment (Stages 4-6)
- Ensures title and script are initially aligned with idea
- First iteration of mutual consistency

### Gate 2: Title-Script Refined Alignment (Stages 8-10)
- Ensures refined title and script are mutually aligned
- Second iteration of mutual consistency
- Final check before quality reviews

### Gate 3: Local AI Quality Reviews (Stages 10-16)
- Seven-dimensional quality assessment
- Grammar, Tone, Content, Consistency, Editing
- Readability for both Title and Script
- All must pass to proceed

### Gate 4: Expert Review (Stages 17-18)
- GPT-based holistic review
- Professional quality standard
- Final gate before publishing

## Workflow Properties

### Iterative Refinement
The workflow supports multiple iterations of refinement:
- Title can be refined multiple times
- Script can be refined multiple times
- Each refinement is informed by review feedback

### Progressive Quality
Quality increases through the workflow:
1. Initial creation (rough drafts acceptable)
2. Mutual alignment (title-script consistency)
3. Local quality checks (automated reviews)
4. Expert polish (professional standards)

### Fail-Fast Principles
- Reviews fail early if quality issues exist
- Immediate feedback loops to refinement stages
- Prevents low-quality content from progressing

### Convergence
The workflow is designed to converge:
- Each iteration improves quality
- Review feedback is specific and actionable
- Eventually all reviews pass

## Related Documentation

- **[Detailed Workflow Documentation](./WORKFLOW_DETAILED.md)** - Complete stage descriptions
- **[T Module Overview](./README.md)** - Text pipeline overview
- **[State Machine (Main)](_meta/docs/workflow/state-machine.md)** - Overall PrismQ state machine
- **[MVP Stages](_meta/docs/workflow/mvp-stages.md)** - 26-stage workflow

---

**Version:** 1.0  
**Created:** 2025-11-24  
**Part of:** PrismQ.T Text Generation Pipeline
