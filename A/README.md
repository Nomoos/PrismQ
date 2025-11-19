# A - Audio Generation Pipeline

**Namespace**: `PrismQ.A`

This module handles the complete audio generation workflow from voiceover recording through to published audio content.

## Purpose

The Audio Generation pipeline transforms published text into high-quality audio content optimized for podcast platforms and audio-first audiences. This is the **second stage** of the sequential progressive enrichment workflow, where published audio serves as the foundation for subsequent video production.

## Workflow Stages

```
PublishedText → Voiceover (Recording → Review → Approved) → Processing (Normalization → Mastering) → AudioPublishing → PublishedAudio
```

## Input Source

This pipeline **uses published text** from the Text Generation pipeline as its source material:

```
PrismQ.T.PublishedText → PrismQ.A.Voiceover
```

## Modules

### Voiceover
Professional audio recording from published text:
- **Recording**: Voice talent records from published text script
- **Review**: Quality check, retakes, audio editing
- **Approved**: Final voiceover approved for production

### Processing
Platform-specific audio optimization:
- **Normalization**: Volume leveling, loudness standards (LUFS)
- **Mastering**: EQ, compression, final polish for podcast/streaming platforms

### Publishing
Audio distribution:
- **AudioPublishing**: Platform-specific exports, RSS feed preparation
- **PublishedAudio**: Live audio on podcast platforms

## Data Flow

Published audio from this pipeline serves as the **foundation** for the Video Generation pipeline:

```
PrismQ.A.PublishedAudio → PrismQ.V.ScenePlanning
```

## Key Features

- **Text-Driven**: Voiceover reads from stable published text
- **Platform Standards**: LUFS normalization for Spotify, Apple Podcasts
- **Quality Gates**: Review and approval ensure professional output
- **Medium Timeline**: Days to week from text to published audio
- **Analytics Integration**: Metrics inform video production decisions

## Usage Examples

### Python Namespace
```python
from PrismQ.A.Voiceover import Recording, Review, Approved
from PrismQ.A.Processing import Normalization, Mastering
from PrismQ.A import AudioPublishing
```

### State Transitions
```python
content = Content(status=ContentStatus.VOICEOVER)
# Record voiceover from published text...
content.status = ContentStatus.VOICEOVER_REVIEW
# Review and edit...
content.status = ContentStatus.VOICEOVER_APPROVED
# Process audio...
content.status = ContentStatus.AUDIO_PUBLISHING
```

## Target Platforms

- **Podcasts**: Spotify, Apple Podcasts, Google Podcasts
- **Audio Books**: Audible, Audiobook platforms
- **Streaming**: SoundCloud, Anchor
- **RSS**: Podcast feeds for distribution

## Processing Standards

- **Loudness**: -16 LUFS (Spotify), -16 LUFS (Apple Podcasts)
- **Format**: MP3 (320kbps), AAC, FLAC for archival
- **Sample Rate**: 44.1kHz or 48kHz
- **Bit Depth**: 24-bit for production, 16-bit for distribution

## Outputs

- **Published Audio**: Professional podcast/audio content
- **Analytics**: Downloads, completion rate, subscriber growth, retention
- **Foundation Material**: Stable audio for Video Generation pipeline

## Related Pipelines

- **Previous Stage**: `PrismQ.T` (Text Generation) - Provides published text source
- **Next Stage**: `PrismQ.V` (Video Generation) - Uses published audio for video sync

---

*Part of the PrismQ sequential progressive enrichment workflow: Text → Audio → Video*
