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

## 📁 Modules

### [Voiceover](./Voiceover/)
**Professional audio recording from published text**

Voice talent records from published text script with quality review.

- Recording from published text
- Quality check and retakes
- Audio editing
- Final approval for production

**[→ View Voiceover Metadata](./Voiceover/_meta/)**

---

### [Narrator](./Narrator/)
**Narrator selection and management**

Select and manage voice talent for audio production.

- [Selection](./Narrator/Selection/) - Voice talent selection

**[→ View Narrator Metadata](./Narrator/_meta/)**

---

### [Normalized](./Normalized/)
**Audio normalization**

Volume leveling and loudness standards (LUFS).

**[→ View Normalized Metadata](./Normalized/_meta/)**

---

### [Enhancement](./Enhancement/)
**Audio enhancement**

EQ, compression, and final polish for podcast/streaming platforms.

**[→ View Enhancement Metadata](./Enhancement/_meta/)**

---

### [Publishing](./Publishing/)
**Audio distribution**

Platform-specific exports and RSS feed preparation.

- [SEO](./Publishing/SEO/) - Audio SEO optimization
- [Finalization](./Publishing/Finalization/) - Final publication preparation

**[→ View Publishing Metadata](./Publishing/_meta/)**

---

## 📖 Module Metadata

### Documentation
Technical documentation and implementation guides.

**[→ View A/_meta/docs/](./_meta/docs/)**

### Examples
Usage examples and sample implementations.

**[→ View A/_meta/examples/](./_meta/examples/)**

### Tests
Test suites and test data.

**[→ View A/_meta/tests/](./_meta/tests/)**

---

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

- **Previous Stage**: [PrismQ.T](../T/README.md) (Text Generation) - Provides published text source
- **Next Stage**: [PrismQ.V](../V/README.md) (Video Generation) - Uses published audio for video sync

---

## Navigation

**[← Back to Main](../README.md)** | **[← Text Pipeline](../T/README.md)** | **[Video Pipeline →](../V/README.md)** | **[Workflow](../WORKFLOW.md)**

---

*Part of the PrismQ sequential progressive enrichment workflow: Text → Audio → Video*
