# PrismQ Content Production Workflow

**Complete State Machine for Content Production from Inspiration to Archive**

## Overview

This document defines the complete workflow state machine for PrismQ content production, from initial inspiration through publication and analytics to final archival.

## Workflow State Diagram

```mermaid
stateDiagram-v2
    [*] --> IdeaInspiration
    IdeaInspiration --> Idea
    IdeaInspiration --> Archived

    state Idea {
        [*] --> Outline
        Outline --> Skeleton
        Skeleton --> Title

        Title --> [*]   %% Title is the final substate before exiting Idea
    }

    Idea --> ScriptDraft
    Idea --> IdeaInspiration
    Idea --> Archived
    
    ScriptDraft --> ScriptReview
    ScriptDraft --> Idea
    ScriptDraft --> Archived

    ScriptReview --> ScriptApproved
    ScriptReview --> ScriptDraft
    ScriptReview --> Idea
    ScriptReview --> Archived

    ScriptApproved --> Voiceover
    ScriptApproved --> ScriptReview
    ScriptApproved --> Archived

    Voiceover --> VoiceoverReview
    Voiceover --> ScriptApproved
    Voiceover --> Archived

    VoiceoverReview --> VoiceoverApproved
    VoiceoverReview --> Voiceover
    VoiceoverReview --> ScriptApproved
    VoiceoverReview --> Archived

    VoiceoverApproved --> ScenePlanning
    VoiceoverApproved --> Archived

    ScenePlanning --> KeyframePlanning
    ScenePlanning --> VoiceoverApproved
    ScenePlanning --> Archived

    KeyframePlanning --> KeyframeGeneration
    KeyframePlanning --> ScenePlanning
    KeyframePlanning --> Archived

    KeyframeGeneration --> VideoAssembly
    KeyframeGeneration --> KeyframePlanning
    KeyframeGeneration --> Archived

    VideoAssembly --> VideoReview
    VideoAssembly --> KeyframeGeneration
    VideoAssembly --> Archived

    VideoReview --> VideoFinalized
    VideoReview --> VideoAssembly
    VideoReview --> KeyframeGeneration
    VideoReview --> Archived

    VideoFinalized --> PublishPlanning
    VideoFinalized --> VideoReview
    VideoFinalized --> Archived

    PublishPlanning --> Published
    PublishPlanning --> VideoFinalized
    PublishPlanning --> Archived

    Published --> AnalyticsReview
    Published --> Archived

    AnalyticsReview --> Archived
    AnalyticsReview --> IdeaInspiration
```

## Workflow Phases

The workflow is organized into 7 major phases:

### Phase 1: Inspiration & Ideation
- **[IdeaInspiration](./IdeaInspiration/)** - Content idea collection and scoring
- **[Idea](./Idea/)** - Distilled concept with sub-states:
  - **[Outline](./Outline/)** - Structured content outline
  - **[Skeleton](./Skeleton/)** - Basic structural framework
  - **[Title](./Title/)** - Finalized title and metadata

### Phase 2: Script Development
- **[ScriptDraft](./Script/ScriptDraft/)** - Initial script writing
- **[ScriptReview](./Script/ScriptReview/)** - Editorial review and enhancement
- **[ScriptApproved](./Script/ScriptApproved/)** - Final approved script

### Phase 3: Audio Production
- **[Voiceover](./Voiceover/)** - Voice recording/synthesis
- **[VoiceoverReview](./Voiceover/VoiceoverReview/)** - Audio quality review
- **[VoiceoverApproved](./Voiceover/VoiceoverApproved/)** - Final approved audio

### Phase 4: Visual Production
- **[ScenePlanning](./Visual/ScenePlanning/)** - Visual design and scene structure
- **[KeyframePlanning](./Visual/KeyframePlanning/)** - Keyframe design and specification
- **[KeyframeGeneration](./Visual/KeyframeGeneration/)** - Visual asset creation

### Phase 5: Video Assembly
- **[VideoAssembly](./Video/VideoAssembly/)** - Timeline editing and assembly
- **[VideoReview](./Video/VideoReview/)** - Quality review and corrections
- **[VideoFinalized](./Video/VideoFinalized/)** - Final approved video

### Phase 6: Publishing
- **[PublishPlanning](./Publishing/PublishPlanning/)** - Publication strategy
- **[Published](./Publishing/Published/)** - Live content management
- **[AnalyticsReview](./Publishing/AnalyticsReview/)** - Performance analysis

### Phase 7: Archive
- **[Archived](./Archived/)** - Terminal state for completed/terminated content

## State Transitions

### Forward Progression (Happy Path)

The normal forward flow through the workflow:
```
IdeaInspiration → Idea (Outline → Skeleton → Title) → ScriptDraft → 
ScriptReview → ScriptApproved → Voiceover → VoiceoverReview → 
VoiceoverApproved → ScenePlanning → KeyframePlanning → 
KeyframeGeneration → VideoAssembly → VideoReview → VideoFinalized → 
PublishPlanning → Published → AnalyticsReview → Archived
```

### Backward Transitions (Revision Loops)

Quality issues or improvements trigger backward movement:

**Script Phase Revisions**
- `ScriptReview → ScriptDraft` - Major script revisions needed
- `ScriptReview → Idea` - Fundamental concept changes required
- `ScriptApproved → ScriptReview` - Issues found after approval

**Voiceover Phase Revisions**
- `VoiceoverReview → Voiceover` - Re-recording needed
- `VoiceoverReview → ScriptApproved` - Script changes affect voiceover
- `Voiceover → ScriptApproved` - Script errors discovered during recording

**Visual Phase Revisions**
- `KeyframePlanning → ScenePlanning` - Scene structure needs revision
- `KeyframeGeneration → KeyframePlanning` - Keyframe specs need adjustment
- `ScenePlanning → VoiceoverApproved` - Audio timing issues affect visuals

**Video Phase Revisions**
- `VideoReview → VideoAssembly` - Assembly/editing issues
- `VideoReview → KeyframeGeneration` - Visual asset problems
- `VideoFinalized → VideoReview` - Post-approval issues discovered

**Publishing Phase Revisions**
- `PublishPlanning → VideoFinalized` - Video changes needed before publish
- `Published → Archived` - Immediate archive (remove from platforms)

### Feedback Loops

**Learning Loop**
- `AnalyticsReview → IdeaInspiration` - Insights inform new content
- Performance data feeds back to improve future content

**Concept Refinement Loop**
- `ScriptDraft → Idea` - Concept needs fundamental rework
- `Idea → IdeaInspiration` - Return to inspiration sources

### Early Termination

Content can be archived from any stage:
```
[Any State] → Archived
```

**Reasons for Early Archive:**
- Concept no longer viable
- Resource constraints
- Strategic pivot
- Quality issues unresolvable
- Duplicate content
- External factors

## State Characteristics

### Entry States
- **IdeaInspiration** - Initial entry point for new content

### Intermediate States
- All states between IdeaInspiration and Archived
- Can transition forward, backward, or to Archived
- Support iterative refinement

### Composite States
- **Idea** - Contains sub-states (Outline → Skeleton → Title)
- Must complete all sub-states before exiting

### Terminal State
- **Archived** - Final destination for all content
- No exits from this state

## State Documentation

Each state has comprehensive documentation covering:

1. **Purpose** - What this state achieves
2. **Key Activities** - Actions performed in this state
3. **Deliverables** - Outputs produced
4. **Quality Gates** - Criteria for moving forward
5. **Transition Criteria** - When to move to next state
6. **Common Issues** - Typical problems and solutions

## Workflow Management

### Progress Tracking

**Status Indicators**
- ⏳ Not Started
- 🔄 In Progress
- ⏸️ Blocked/Waiting
- ✅ Complete
- ⚠️ Issues/Review Needed
- 🗄️ Archived

**Metadata Tracking**
```json
{
  "project_id": "PQ001",
  "current_state": "ScriptReview",
  "state_history": [
    {"state": "IdeaInspiration", "entered": "2025-01-01", "exited": "2025-01-02"},
    {"state": "Idea", "entered": "2025-01-02", "exited": "2025-01-03"},
    {"state": "ScriptDraft", "entered": "2025-01-03", "exited": "2025-01-05"},
    {"state": "ScriptReview", "entered": "2025-01-05", "exited": null}
  ],
  "revision_count": 2,
  "days_in_production": 5,
  "team_assigned": ["Writer A", "Editor B", "Reviewer C"]
}
```

### Quality Gates

Each state has defined quality criteria that must be met before progression:

**Documentation Gates**
- All required fields completed
- Metadata accurate and complete
- Version control updated

**Review Gates**
- Peer review completed
- Stakeholder approval received
- Quality standards verified

**Technical Gates**
- File formats correct
- Technical specifications met
- No critical errors present

### Automation Opportunities

**Automated Transitions**
- File upload triggers state change
- Approval workflows trigger progression
- Scheduled tasks (e.g., publication timing)
- Analytics collection and reporting

**Manual Transitions**
- Creative decisions
- Quality assessments
- Strategic pivots
- Resource allocation

## Best Practices

### General Principles

1. **Complete Each State** - Don't skip quality gates
2. **Document Everything** - Track decisions and changes
3. **Iterate When Needed** - Use backward transitions to improve
4. **Archive Promptly** - Don't let dead projects linger
5. **Learn Continuously** - Feed insights back to ideation

### State-Specific Tips

**Idea Phase**
- Invest time in outline and skeleton
- Clear title before moving to script
- Validate concept with stakeholders early

**Script Phase**
- Multiple review passes prevent downstream issues
- Lock approved scripts to prevent scope creep
- Keep revision history for learning

**Production Phase**
- Audio and visual quality gates are critical
- Test on target platforms early
- Build in buffer time for revisions

**Publishing Phase**
- Plan timing strategically
- Monitor early performance closely
- Engage with audience actively

**Analytics Phase**
- Collect comprehensive data
- Extract actionable insights
- Feed learnings back to ideation

## Metrics & Monitoring

### Workflow Efficiency Metrics

**Time Metrics**
- Average time per state
- Total production time
- Bottleneck identification
- Revision cycle time

**Quality Metrics**
- Revision frequency per state
- Defect escape rate
- Final quality scores
- Stakeholder satisfaction

**Resource Metrics**
- Team utilization
- Cost per state
- Asset reuse rate
- Automation savings

### Performance Dashboards

Track workflow health with key indicators:
- Projects by state (distribution)
- Average time in each state
- Revision/rework rate
- Completion rate
- Archive reasons breakdown

## Related Documentation

- **[IdeaInspiration Module](./IdeaInspiration/README.md)** - Inspiration and collection
- **[Idea Model](./Idea/Model/README.md)** - Core data model
- **[Content Production Workflow States Research](./_ meta/research/content-production-workflow-states.md)** - Detailed research
- **[YouTube Metadata Optimization](../_meta/research/youtube-metadata-optimization-smart-strategy.md)** - Platform strategy

## Version History

- **v2.0** (2025-01-19) - Complete state machine with Mermaid diagram
- **v1.0** (2025-01-10) - Initial 14-stage workflow documentation

---

*PrismQ Content Production Workflow - Complete State Machine Documentation*
