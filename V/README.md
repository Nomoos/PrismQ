# V - Video Generation Pipeline

**Namespace**: `PrismQ.V`

This module handles the complete video generation workflow from scene planning through to published video content.

## Purpose

The Video Generation pipeline transforms published audio into engaging video content with synchronized visuals, optimized for video platforms. This is the **third and final stage** of the sequential progressive enrichment workflow, combining audio with visual storytelling.

## Workflow Stages

```
PublishedAudio → Visual (ScenePlanning → KeyframePlanning → KeyframeGeneration) → Assembly (Timeline → Review → Finalized) → Publishing → PublishedVideo
```

## Input Source

This pipeline **uses published audio** from the Audio Generation pipeline as its foundation:

```
PrismQ.A.PublishedAudio → PrismQ.V.ScenePlanning
```

## Modules

### Visual
Visual content creation synchronized to audio:
- **ScenePlanning**: Plan scenes, visual style, and timing based on published audio
- **KeyframePlanning**: Identify key visual moments and transitions
- **KeyframeGeneration**: Generate or create keyframe visuals, graphics, footage

### Assembly
Video production and editing:
- **Timeline**: Assemble visuals, sync with audio, add transitions/effects
- **Review**: Quality check, revisions, refinements
- **Finalized**: Final rendered video ready for publication

### Publishing
Video distribution:
- **PublishPlanning**: Platform optimization, thumbnails, metadata, descriptions
- **PublishedVideo**: Live video on platforms (YouTube, TikTok, Instagram Reels)

## Data Flow

This is the final stage of the sequential enrichment workflow:

```
PrismQ.T.PublishedText → PrismQ.A.PublishedAudio → PrismQ.V.PublishedVideo
```

All analytics feed back to Text Generation for continuous improvement:

```
PrismQ.V.AnalyticsReviewVideo → PrismQ.T.IdeaInspiration
```

## Key Features

- **Audio-Driven**: Visuals planned and synced to published audio foundation
- **Platform Optimization**: Format, aspect ratio, thumbnails for each platform
- **Quality Gates**: Review and finalization ensure professional output
- **Longest Timeline**: Weeks from audio to published video
- **Complete Analytics**: Full funnel metrics across text, audio, and video

## Usage Examples

### Python Namespace
```python
from PrismQ.V.Visual import ScenePlanning, KeyframePlanning, KeyframeGeneration
from PrismQ.V.Assembly import Timeline, Review, Finalized
from PrismQ.V import Publishing
```

### State Transitions
```python
content = Content(status=ContentStatus.SCENE_PLANNING)
# Plan scenes based on published audio...
content.status = ContentStatus.KEYFRAME_PLANNING
# Identify keyframes...
content.status = ContentStatus.KEYFRAME_GENERATION
# Generate visuals...
content.status = ContentStatus.VIDEO_ASSEMBLY
```

## Target Platforms

- **Long-form**: YouTube (8-10 min educational/narrative)
- **Short-form**: TikTok, Instagram Reels, YouTube Shorts (60s)
- **Social**: Facebook Video, Twitter/X Video
- **Professional**: LinkedIn Video

## Platform Specifications

- **YouTube**: 1920x1080 (16:9), thumbnails, CTR optimization
- **TikTok/Reels**: 1080x1920 (9:16), hook in first 3 seconds, retention focus
- **Instagram**: 1080x1080 (1:1) or 1080x1920 (9:16)
- **Frame Rate**: 24fps (cinematic), 30fps (standard), 60fps (smooth)

## Outputs

- **Published Video**: Complete video content with audio + visuals
- **Analytics**: Views, watch time, CTR, engagement rate, retention curves
- **Performance Data**: Insights fed back to IdeaInspiration for next content

## Related Pipelines

- **First Stage**: `PrismQ.T` (Text Generation) - Originating published text
- **Second Stage**: `PrismQ.A` (Audio Generation) - Provides published audio foundation

---

*Part of the PrismQ sequential progressive enrichment workflow: Text → Audio → Video*
