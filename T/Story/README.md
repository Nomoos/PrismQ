# T/Story - Story-Level Expert Review and Polish

**Namespace**: `PrismQ.T.Story`

Final GPT-based expert review and polishing of complete story (title + script + audience context).

## Purpose

After all local AI reviews pass, the complete story undergoes a final expert-level review and polish using GPT (GPT-4/GPT-5) to ensure professional quality before publishing.

## Workflow Position

**Stages 21-22** in MVP workflow: Between local AI reviews and publishing

```
Stage 20: Script Readability (Local AI) ✓ PASSES
    ↓
Stage 21: Story.ExpertReview (GPT-based) ← Expert review
    ↓
    ├─ Improvements needed → Stage 22: Story.Polish
    │                             ↓
    │                        Return to Stage 21
    ↓ Ready for publishing
Stage 23: Publishing.Finalization
```

## Key Differentiators

### Local AI Loop (Stages 1-20)
- Fast iterations
- Multiple specific reviews (Grammar, Tone, Content, etc.)
- Focused improvements
- Cost-effective

### GPT Expert Loop (Stages 21-22)
- Final expert-level review
- Holistic story assessment
- Professional polish
- Reviews complete package: title + script + audience
- GPT-4 or GPT-5 powered

## Submodules

### [ExpertReview](./ExpertReview/)
**Stage 21: GPT-based expert review**

Final expert-level review of the complete story package (title, script, audience) using GPT.

**[→ View ExpertReview Documentation](./ExpertReview/README.md)**
**[→ View ExpertReview Metadata](./ExpertReview/_meta/)**

### [Polish](./Polish/)
**Stage 22: GPT-based expert polishing**

Apply expert-level improvements to title and script based on GPT review feedback.

**[→ View Polish Documentation](./Polish/README.md)**
**[→ View Polish Metadata](./Polish/_meta/)**

## Module Metadata

**[→ View Story/_meta/docs/](./_meta/docs/)**
**[→ View Story/_meta/examples/](./_meta/examples/)**
**[→ View Story/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to T](../README.md)** | **[→ T/_meta](../_meta/)**
