# PrismQ.T Workflow State Machine

**Visual State Diagram for Detailed Text Generation Workflow**

## State Machine Diagram

```mermaid
stateDiagram-v2
    [*] --> IdeaCreation
    
    IdeaCreation --> StoryFromIdea
    StoryFromIdea --> TitleFromIdea
    TitleFromIdea --> ContentFromIdeaTitle
    ContentFromIdeaTitle --> ReviewTitleFromContentIdea
    
    ReviewTitleFromContentIdea --> ReviewContentFromTitleIdea
    
    ReviewContentFromTitleIdea --> ReviewTitleFromContent
    
    ReviewTitleFromContent --> TitleFromTitleReviewContent
    ReviewTitleFromContent --> ReviewContentFromTitle
    
    TitleFromTitleReviewContent --> ContentFromTitleReviewContent
    
    ContentFromTitleReviewContent --> ReviewTitleFromContent
    
    ReviewContentFromTitle --> ContentFromTitleReviewContent
    ReviewContentFromTitle --> ReviewContentGrammar
    
    ReviewContentGrammar --> ReviewContentTone
    ReviewContentGrammar --> ContentFromTitleReviewContent
    
    ReviewContentTone --> ReviewContentContent
    ReviewContentTone --> ContentFromTitleReviewContent
    
    ReviewContentContent --> ReviewContentConsistency
    ReviewContentContent --> ContentFromTitleReviewContent
    
    ReviewContentConsistency --> ReviewContentEditing
    ReviewContentConsistency --> ContentFromTitleReviewContent
    
    ReviewContentEditing --> ReviewTitleReadability
    ReviewContentEditing --> ContentFromTitleReviewContent
    
    ReviewTitleReadability --> ReviewContentReadability
    ReviewTitleReadability --> TitleFromTitleReviewContent
    
    ReviewContentReadability --> StoryReview
    ReviewContentReadability --> ContentFromTitleReviewContent
    
    StoryReview --> StoryPolish
    StoryReview --> Publishing
    
    StoryPolish --> StoryReview
    
    Publishing --> [*]

    note right of IdeaCreation
        Stage 1: Initial idea capture
        Location: T/Idea/From/User/
    end note
    
    note right of StoryFromIdea
        Stage 1.5: Create 10 Stories per Idea
        Location: T/Story/From/Idea/
    end note
    
    note right of TitleFromIdea
        Stage 2: Generate title v1
        Location: T/Title/From/Idea/
    end note
    
    note right of ContentFromIdeaTitle
        Stage 3: Generate content v1
        Location: T/Content/From/Idea/Title/
    end note
    
    note right of ReviewTitleFromContentIdea
        Stage 4: Review title (no conditional)
        Always proceeds to Stage 5
    end note
    
    note right of ReviewContentFromTitleIdea
        Stage 5: Review content (no conditional)
        Always proceeds to Stage 6
    end note
    
    note right of ReviewContentGrammar
        Stages 10-16: Local AI reviews
        All failures loop through
        Content Refinement → Title Review
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
| IdeaCreation | PrismQ.T.Idea.From.User | 1 | T/Idea/From/User/ |
| StoryFromIdea | PrismQ.T.Story.From.Idea | 1.5 | T/Story/From/Idea/ |
| TitleFromIdea | PrismQ.T.Title.From.Idea | 2 | T/Title/From/Idea/ |
| ContentFromIdeaTitle | PrismQ.T.Content.From.Idea.Title | 3 | T/Content/From/Idea/Title/ |
| ReviewTitleFromContentIdea | PrismQ.T.Review.Title.From.Content.Idea | 4 | T/Review/Title/From/Content/Idea/ |
| ReviewContentFromTitleIdea | PrismQ.T.Review.Content.From.Title.Idea | 5 | T/Review/Content/From/Title/Idea/ |
| ReviewTitleFromContent | PrismQ.T.Review.Title.From.Content | 6 | T/Review/Title/From/Content/ |
| TitleFromTitleReviewContent | PrismQ.T.Title.From.Title.Review.Content | 7 | T/Title/From/Title/Review/Content/ |
| ContentFromTitleReviewContent | PrismQ.T.Content.From.Title.Review.Content | 8 | T/Content/From/Title/Review/Content/ |
| ReviewContentFromTitle | PrismQ.T.Review.Content.From.Title | 9 | T/Review/Content/From/Title/ |

### Quality Review States

| State | Full Name | Stage | Location |
|-------|-----------|-------|----------|
| ReviewContentGrammar | PrismQ.T.Review.Content.Grammar | 10 | T/Review/Grammar/ |
| ReviewContentTone | PrismQ.T.Review.Content.Tone | 11 | T/Review/Tone/ |
| ReviewContentContent | PrismQ.T.Review.Content.Content | 12 | T/Review/Content/ |
| ReviewContentConsistency | PrismQ.T.Review.Content.Consistency | 13 | T/Review/Consistency/ |
| ReviewContentEditing | PrismQ.T.Review.Content.Editing | 14 | T/Review/Editing/ |
| ReviewTitleReadability | PrismQ.T.Review.Title.Readability | 15 | T/Review/Readability/ |
| ReviewContentReadability | PrismQ.T.Review.Content.Readability | 16 | T/Review/Readability/ |

### Expert Review Loop States

| State | Full Name | Stage | Location |
|-------|-----------|-------|----------|
| StoryReview | PrismQ.T.Story.Review | 17 | T/Story/Review/ |
| StoryPolish | PrismQ.T.Story.Polish | 18 | T/Story/Polish/ |

### Terminal State

| State | Full Name | Description |
|-------|-----------|-------------|
| Publishing | PrismQ.T.Publishing | Final stage leading to publication |

## State Transitions

### Linear Progression

Initial linear flow through the workflow:

```
IdeaCreation 
  → StoryFromIdea
  → TitleFromIdea 
  → ContentFromIdeaTitle 
  → ReviewTitleFromContentIdea
```

### Conditional Branches

#### Title Review Branch
```
ReviewTitleFromContentIdea
  ├─ accepted → ReviewContentFromTitleIdea
  └─ not accepted → TitleFromTitleReviewContent → ReviewContentFromTitleIdea
```

#### Content Review Branch
```
ReviewContentFromTitleIdea
  ├─ accepted → ReviewTitleFromContent
  └─ not accepted → ContentFromTitleReviewContent → ReviewTitleFromContent
```

#### Title Re-Review Branch
```
ReviewTitleFromContent
  ├─ accepted → ReviewContentFromTitle
  └─ not accepted → TitleFromTitleReviewContent → ReviewContentFromTitle
```

#### Content Re-Review Branch
```
ReviewContentFromTitle
  ├─ accepted → QualityReviews (ReviewContentGrammar)
  └─ not accepted → ContentFromTitleReviewContent → ReviewContentFromTitle
```

### Quality Review Sequence

Sequential quality reviews with failure feedback:

```
QualityReviews:
  ReviewContentGrammar
    ├─ passes → ReviewContentTone
    └─ fails → ContentFromTitleReviewContent
    
  ReviewContentTone
    ├─ passes → ReviewContentContent
    └─ fails → ContentFromTitleReviewContent
    
  ReviewContentContent
    ├─ passes → ReviewContentConsistency
    └─ fails → ContentFromTitleReviewContent
    
  ReviewContentConsistency
    ├─ passes → ReviewContentEditing
    └─ fails → ContentFromTitleReviewContent
    
  ReviewContentEditing
    ├─ passes → ReviewTitleReadability
    └─ fails → ContentFromTitleReviewContent
    
  ReviewTitleReadability
    ├─ passes → ReviewContentReadability
    └─ fails → TitleFromContentReviewTitle
    
  ReviewContentReadability
    ├─ passes → ExpertReviewLoop (StoryReview)
    └─ fails → ContentFromTitleReviewContent
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
→ ContentFromIdeaTitle
→ ReviewTitleFromContentIdea (accepted)
→ ReviewContentFromTitleIdea (accepted)
→ ReviewTitleFromContent (accepted)
→ ReviewContentFromTitle (accepted)
→ ReviewContentGrammar (passes)
→ ReviewContentTone (passes)
→ ReviewContentContent (passes)
→ ReviewContentConsistency (passes)
→ ReviewContentEditing (passes)
→ ReviewTitleReadability (passes)
→ ReviewContentReadability (passes)
→ StoryReview (accepted)
→ Publishing
```

**Total Stages**: 14 stages

### Realistic Path (Some Reviews Require Refinement)

```
IdeaCreation
→ TitleFromIdea
→ ContentFromIdeaTitle
→ ReviewTitleFromContentIdea (not accepted)
→ TitleFromTitleReviewContent
→ ReviewContentFromTitleIdea (accepted)
→ ReviewTitleFromContent (accepted)
→ ReviewContentFromTitle (not accepted)
→ ContentFromTitleReviewContent
→ ReviewContentFromTitle (accepted)
→ ReviewContentGrammar (passes)
→ ReviewContentTone (fails)
→ ContentFromTitleReviewContent
→ ReviewContentFromTitle (accepted)
→ ReviewContentGrammar (passes)
→ ReviewContentTone (passes)
→ ReviewContentContent (passes)
→ ReviewContentConsistency (passes)
→ ReviewContentEditing (passes)
→ ReviewTitleReadability (passes)
→ ReviewContentReadability (passes)
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
- Has a single entry point (ReviewContentGrammar)
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
- **TitleFromTitleReviewContent**: Title refinement (used multiple times)
- **ContentFromTitleReviewContent**: Content refinement (used multiple times)
- **StoryPolish**: Expert-level polish

### Review States
States that evaluate quality and make accept/reject decisions:
- **ReviewTitleFromContentIdea**: Title review with full context
- **ReviewContentFromTitleIdea**: Content review with full context
- **ReviewTitleFromContent**: Title review against content
- **ReviewContentFromTitle**: Content review against title
- **ReviewContentGrammar**: Grammar validation
- **ReviewContentTone**: Tone validation
- **ReviewContentContent**: Content validation
- **ReviewContentConsistency**: Consistency validation
- **ReviewContentEditing**: Editing validation
- **ReviewTitleReadability**: Title readability validation
- **ReviewContentReadability**: Content readability validation
- **StoryReview**: Expert holistic review

### Terminal State
- **Publishing**: End of workflow, leads to publication

## Quality Gates

### Gate 1: Title-Content Initial Alignment (Stages 4-6)
- Ensures title and content are initially aligned with idea
- First iteration of mutual consistency

### Gate 2: Title-Content Refined Alignment (Stages 8-10)
- Ensures refined title and content are mutually aligned
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
