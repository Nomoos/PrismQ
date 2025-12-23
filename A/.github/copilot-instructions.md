# PrismQ.A - Audio Generation Pipeline - GitHub Copilot Instructions

> **Note**: For general project guidelines, see the [main repository's copilot instructions](../../.github/copilot-instructions.md).

## Module Context

**Namespace**: `PrismQ.A` (Audio)

The Audio Generation Pipeline transforms published text into high-quality audio content. This is the **second stage** of the sequential progressive enrichment workflow.

### Workflow Position
```
PublishedText → Audio Pipeline → PublishedAudio → Video Pipeline
```

---

## Module Structure

```
A/
├── src/                     # Audio foundation layer (if needed)
├── Voiceover/              # Professional audio recording
│   ├── Recording/         # Voice recording from text
│   ├── Review/            # Quality check and retakes
│   └── Approved/          # Final approval
├── Narrator/               # Narrator management
├── Processing/             # Audio processing
│   ├── Normalization/     # Audio normalization
│   └── Mastering/         # Audio mastering
└── Publishing/             # Audio publishing
```

---

## Module Responsibilities

### What Belongs Here
- **Audio Recording** - Voiceover recording from published text
- **Audio Processing** - Normalization, mastering, effects
- **Narrator Management** - Voice talent selection and management
- **Audio Publishing** - Publishing audio to platforms

### What Doesn't Belong Here
- Text generation → Move to `T/` (Text module)
- Video processing → Move to `V/` (Video module)
- Generic utilities → Move to `src/` (root)

---

## Key Design Patterns

### Input Source
This pipeline **uses published text** from the Text Generation pipeline:
```
PrismQ.T.PublishedText → PrismQ.A.Voiceover
```

### Workflow Stages
```
PublishedText → Voiceover → Processing → Publishing → PublishedAudio
```

### Dependency Flow
```
A/<Submodule>  (specialized audio operations)
        ↓
A/src (Audio foundation, if needed)
        ↓
src/ (root)    (generic utilities)
```

---

## Common Operations

### Processing Published Text
```python
# ✅ Consume from Text module
from T.Publishing import get_published_text

# Process into audio
voiceover = create_voiceover(published_text)
```

### Audio Quality Standards
- Sample rate: 44.1kHz or 48kHz
- Bit depth: 16-bit or 24-bit
- Format: WAV for processing, MP3/AAC for publishing
- Normalization: -16 LUFS for podcasts, -14 LUFS for music

### Working with Narrators
- Narrator selection based on content type
- Voice consistency across series
- Quality review and retakes
- Performance tracking

---

## Integration Points

### Inputs
- **PublishedText** from `T/` (Text Pipeline)
- Narrator profiles and preferences
- Audio processing settings

### Outputs
- **PublishedAudio** → Consumed by `V/` (Video Pipeline)
- Publishing data → Sent to `P/` (Publishing module)
- Performance metrics → Reported to `M/` (Metrics module)

---

## Target Platform Optimization

### Audio Processing Hardware
- **GPU**: NVIDIA RTX 5090 (for AI-based processing)
- **CPU**: AMD Ryzen (for traditional audio processing)
- **RAM**: 64GB (for large audio buffers)

### Performance Considerations
- Use GPU acceleration for AI-based noise reduction
- Batch processing for multiple audio files
- Streaming for real-time preview
- Efficient memory management for long recordings

---

## Project Guidelines Reference

For detailed project-wide guidelines:
- **[Root Copilot Instructions](../../.github/copilot-instructions.md)** - Core principles and hierarchy
- **[Coding Guidelines](../../_meta/docs/guidelines/CODING_GUIDELINES.md)** - Module placement rules
- **[Module Hierarchy](../../_meta/docs/guidelines/MODULE_HIERARCHY_UPDATED.md)** - Dependency diagrams

### Quick Rules
1. **Dependencies**: Specialized → Generic (never reversed)
2. **Input Source**: Always consume from `T/PublishedText`
3. **Output**: Produce `PublishedAudio` for `V/` module
4. **Module Structure**: `src/` for production, `_meta/` for tests/docs

---

## Questions to Ask

When working on this module:
- Does this operate on published text from `T/`?
- Is this audio-specific, or should it be in a generic utility module?
- Am I following the sequential workflow (Text → Audio → Video)?
- Have I considered audio quality standards?
- Is this compatible with the video pipeline's requirements?
- Are performance characteristics optimized for the target hardware?

---

## Module Documentation

- **[A Module README](../README.md)** - Detailed audio workflow
- **[Main Project README](../../README.md)** - Overall project context
