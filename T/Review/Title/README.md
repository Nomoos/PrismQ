# T/Review/Title - Title Review Module

**Namespace**: `PrismQ.T.Review.Title`

AI-powered title evaluation and feedback generation.

## Purpose

Provide comprehensive title review capabilities to ensure titles accurately represent content, engage audiences, and optimize for search and clickthrough.

## Submodules

### [ByScriptAndIdea](./ByScriptAndIdea/)
**Stage 4 (MVP-004): Review title v1 against script v1 and idea**

AI-powered title evaluation against script content and original idea intent.

**Key Features:**
- Dual alignment assessment (script + idea)
- Engagement and clickthrough optimization
- Expectation setting validation
- SEO recommendations
- Prioritized improvement feedback

**Workflow Position:**
```
Title v1 + Script v1 + Idea → Review (Stage 4) → Title v2 (Stage 6)
```

**[→ View ByScriptAndIdea Documentation](./ByScriptAndIdea/README.md)**
**[→ View ByScriptAndIdea Metadata](./ByScriptAndIdea/_meta/)**

### [Acceptance](./Acceptance/)
**Stage 12 (MVP-012): Title Acceptance Gate**

Acceptance gate that determines whether a title (at any version) is ready to proceed or needs further refinement.

**Key Features:**
- Three-criterion evaluation (clarity, engagement, script alignment)
- Automatic threshold checking
- Detailed feedback and recommendations
- Version tracking (v3, v4, v5, etc.)
- JSON-compatible output

**Workflow Position:**
```
Title (vN) + Script (vN) → Acceptance Gate (Stage 12) → {
    ACCEPTED: Proceed to Script Acceptance (Stage 13)
    NOT ACCEPTED: Loop to Title Review (Stage 8) → Title Refinement
}
```

**[→ View Acceptance Documentation](./Acceptance/README.md)**
**[→ View Acceptance Tests](./Acceptance/_meta/tests/)**

## Module Metadata

**[→ View Title/_meta/docs/](./_meta/docs/)**
**[→ View Title/_meta/examples/](./_meta/examples/)**
**[→ View Title/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Review](../README.md)** | **[→ Review/_meta](../_meta/)**
