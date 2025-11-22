# State Transitions


### Forward Progression (Sequential Format Enrichment)

The workflow follows a **progressive enrichment model**:

**Text-Only Path (Fastest - Stop after text):**
```
IdeaInspiration → Idea (Creation → Outline → Title) → ScriptDraft → 
ScriptReview → ScriptApproved → TextPublishing → PublishedText → 
AnalyticsReviewText → Archived
```

**Text + Audio Path (Medium - Stop after audio):**
```
... → ScriptApproved → TextPublishing → PublishedText → Voiceover → 
VoiceoverReview → VoiceoverApproved → AudioPublishing → PublishedAudio → 
AnalyticsReviewAudio → Archived
```

**Full Production Path (Complete - All formats):**
```
... → PublishedText → Voiceover → ... → PublishedAudio → ScenePlanning → 
KeyframePlanning → KeyframeGeneration → VideoAssembly → VideoReview → 
VideoFinalized → PublishPlanning → PublishedVideo → AnalyticsReviewVideo → 
Archived
```

**Key Data Flow:**
```
ScriptApproved
    ↓
TextPublishing → PublishedText (text is published)
    ↓
Voiceover (uses published text as source)
    ↓
VoiceoverApproved → AudioPublishing → PublishedAudio (audio is published)
    ↓
ScenePlanning (uses published audio as foundation)
    ↓
... → PublishedVideo (video is published)
```

### Backward Transitions (Revision Loops)

Quality issues or improvements trigger backward movement:

**Script Phase Revisions**
- `ScriptReview → ScriptDraft` - Major script revisions needed
- `ScriptReview → Idea` - Fundamental concept changes required
- `ScriptApproved → ScriptReview` - Issues found after approval

**Text Publishing Revisions**
- `TextPublishing → ScriptApproved` - Text formatting issues, need script revision
- `Voiceover → PublishedText` - Voiceover issues with published text source

**Voiceover Phase Revisions**
- `VoiceoverReview → Voiceover` - Re-recording needed
- `VoiceoverReview → PublishedText` - Need to revise published text source
- `Voiceover → PublishedText` - Published text has errors discovered during recording

**Audio Publishing Revisions**
- `AudioPublishing → VoiceoverApproved` - Audio file issues, need re-export
- `ScenePlanning → PublishedAudio` - Video planning issues with audio source

**Visual Phase Revisions**
- `KeyframePlanning → ScenePlanning` - Scene structure needs revision
- `KeyframeGeneration → KeyframePlanning` - Keyframe specs need adjustment
- `ScenePlanning → PublishedAudio` - Audio timing issues affect visuals

**Video Phase Revisions**
- `VideoReview → VideoAssembly` - Assembly/editing issues
- `VideoReview → KeyframeGeneration` - Visual asset problems
- `VideoFinalized → VideoReview` - Post-approval issues discovered

**Publishing Phase Revisions**
- `PublishPlanning → VideoFinalized` - Video changes needed before publish

### Feedback Loops

**Format-Specific Learning Loops**
- `AnalyticsReviewText → IdeaInspiration` - Text performance insights
- `AnalyticsReviewAudio → IdeaInspiration` - Audio performance insights  
- `AnalyticsReviewVideo → IdeaInspiration` - Video performance insights
- Cross-format insights inform future content strategy
- Early format analytics inform production decisions for later formats
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

