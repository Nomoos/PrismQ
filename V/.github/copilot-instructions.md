# PrismQ.V - Video Generation Pipeline - GitHub Copilot Instructions

> **Note**: For general project guidelines, see the [main repository's copilot instructions](../../.github/copilot-instructions.md).

## Module Context

**Namespace**: `PrismQ.V` (Video)

The Video Generation Pipeline combines audio with visuals to create complete video content. This is the **third stage** of the sequential progressive enrichment workflow.

### Workflow Position
```
PublishedAudio → Video Pipeline → PublishedVideo
```

---

## Module Structure

```
V/
├── src/                     # Video foundation layer (shared Video utilities, if any)
├── Scene/                  # Scene planning and composition
│   ├── Planning/          # Scene breakdown
│   ├── Keyframe/          # Keyframe generation
│   └── Composition/       # Scene assembly
├── Visual/                 # Visual generation
│   ├── Image/             # Image generation
│   ├── Animation/         # Animation creation
│   └── Effects/           # Visual effects
├── Assembly/               # Video assembly
│   ├── Timeline/          # Timeline construction
│   ├── Sync/              # Audio-visual synchronization
│   └── Rendering/         # Final video rendering
└── Publishing/             # Video publishing
```

---

## Module Responsibilities

### What Belongs Here
- **Scene Planning** - Breaking down audio into visual scenes
- **Visual Generation** - Creating images and animations
- **Video Assembly** - Combining audio with visuals
- **Video Publishing** - Publishing video to platforms

### What Doesn't Belong Here
- Text generation → Move to `T/` (Text module)
- Audio recording → Move to `A/` (Audio module)
- Generic utilities → Move to `src/` (root)

---

## Key Design Patterns

### Input Source
This pipeline **uses published audio** from the Audio pipeline:
```
PrismQ.A.PublishedAudio → PrismQ.V.Scene
```

### Workflow Stages
```
PublishedAudio → Scene Planning → Visual Generation → Assembly → Rendering → PublishedVideo
```

### Dependency Flow
```
V/<Submodule>  (specialized video operations)
        ↓
V/src (Video foundation, currently not needed but available for shared utilities)
        ↓
src/ (root)    (generic utilities)
```

---

## Common Operations

### Processing Published Audio
```python
# ✅ Consume from Audio module
from A.Publishing import get_published_audio

# Process into video
scenes = plan_scenes(published_audio)
visuals = generate_visuals(scenes)
video = assemble_video(visuals, published_audio)
```

### Video Quality Standards
- Resolution: 1080p (1920x1080) or 4K (3840x2160)
- Frame rate: 24fps, 30fps, or 60fps
- Codec: H.264 or H.265/HEVC
- Audio codec: AAC
- Container: MP4 or MOV

### Working with Scenes
- Scene detection from audio pacing
- Keyframe generation for important moments
- Visual consistency across scenes
- Transition effects between scenes

---

## Integration Points

### Inputs
- **PublishedAudio** from `A/` (Audio Pipeline)
- Visual style preferences
- Platform-specific requirements

### Outputs
- **PublishedVideo** → Final deliverable
- Publishing data → Sent to `P/` (Publishing module)
- Performance metrics → Reported to `M/` (Metrics module)

---

## Target Platform Optimization

### Video Processing Hardware
- **GPU**: NVIDIA RTX 5090 (for rendering and AI-based generation)
  - CUDA cores for rendering
  - Tensor cores for AI image/video generation
  - 32GB VRAM for 4K processing
- **CPU**: AMD Ryzen (for encoding and effects)
- **RAM**: 64GB (for video buffers and preview)

### Performance Considerations
- Use GPU acceleration for rendering (CUDA/NVENC)
- AI-based scene detection and keyframe generation
- Parallel processing for multiple scenes
- Efficient VRAM management for 4K content
- Use NVENC for fast H.264/HEVC encoding

---

## Platform-Specific Considerations

### YouTube
- Aspect ratio: 16:9
- Recommended resolution: 1080p or 4K
- Max file size: 128GB (or 12 hours)
- Thumbnail requirements

### TikTok / Instagram Reels
- Aspect ratio: 9:16 (vertical)
- Duration: 15-60 seconds
- Resolution: 1080x1920

### Platform Optimization
- Different encoding settings per platform
- Automated thumbnail generation
- Platform-specific metadata

---

## Project Guidelines Reference

For detailed project-wide guidelines:
- **[Root Copilot Instructions](../../.github/copilot-instructions.md)** - Core principles and hierarchy
- **[Coding Guidelines](../../_meta/docs/guidelines/CODING_GUIDELINES.md)** - Module placement rules
- **[Module Hierarchy](../../_meta/docs/guidelines/MODULE_HIERARCHY_UPDATED.md)** - Dependency diagrams

### Quick Rules
1. **Dependencies**: Specialized → Generic (never reversed)
2. **Input Source**: Always consume from `A/PublishedAudio`
3. **Output**: Produce `PublishedVideo` as final deliverable
4. **Module Structure**: `src/` for production, `_meta/` for tests/docs
5. **GPU Optimization**: Leverage RTX 5090 for rendering and AI generation

---

## Questions to Ask

When working on this module:
- Does this operate on published audio from `A/`?
- Is this video-specific, or should it be in a generic utility module?
- Am I following the sequential workflow (Text → Audio → Video)?
- Have I considered video quality and platform requirements?
- Am I leveraging GPU acceleration effectively?
- Is the output compatible with target platforms?
- Have I optimized VRAM usage for 4K processing?

---

## Module Documentation

- **[V Module README](../README.md)** - Detailed video workflow
- **[Main Project README](../../README.md)** - Overall project context
