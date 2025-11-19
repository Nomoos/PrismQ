# Visual Production

**Workflow Phase: Visual Production**

## Overview

The **Visual** module manages the visual content creation phase where scenes are planned, designed, and generated for video assembly.

## Position in Workflow

```
VoiceoverApproved → [ScenePlanning] → KeyframePlanning → KeyframeGeneration → VideoAssembly
```

## Purpose

Create the visual elements that will be combined with voiceover audio to form the complete video content. This phase encompasses:

- Visual style definition
- Scene composition planning
- Keyframe design and generation
- Visual continuity establishment
- Asset preparation for video assembly

## Sub-Stages

This module contains three sub-stages:

1. **[ScenePlanning](./ScenePlanning/)** - Visual design and scene structure
2. **[KeyframePlanning](./KeyframePlanning/)** - Keyframe design and specification
3. **[KeyframeGeneration](./KeyframeGeneration/)** - Visual asset creation

## Visual Production Methods

### AI-Generated Imagery
- Stable Diffusion, DALL-E, Midjourney
- Style-consistent generation
- Batch processing
- Prompt engineering
- Quality control

### Stock Media
- Licensed stock photos/videos
- Curated collections
- Search and selection
- Rights management
- Attribution tracking

### Custom Creation
- Original illustrations
- Graphic design
- Animation assets
- Motion graphics
- 3D renders

### Hybrid Approach
- AI base + manual refinement
- Stock + custom overlays
- Multiple source integration
- Cost-effective production

## Key Activities

1. **Define Visual Style** - Establish aesthetic and mood
2. **Plan Scenes** - Design scene structure and composition
3. **Design Keyframes** - Create visual specifications
4. **Generate Assets** - Produce visual elements
5. **Quality Control** - Verify visual standards

## Technical Requirements

### Image Specifications
- Resolution: 1920x1080 minimum (Full HD)
- Format: PNG (transparency) or JPEG
- Color Space: sRGB
- Aspect Ratio: 16:9 (standard), 9:16 (vertical), 1:1 (square)
- DPI: 72+ for screen, 300+ for print

### Video Specifications
- Resolution: 1920x1080 or 3840x2160 (4K)
- Format: MP4, MOV, or ProRes
- Frame Rate: 24, 30, or 60 fps
- Codec: H.264 or H.265
- Bitrate: 10-50 Mbps depending on complexity

### File Organization
```
Visual/
├── ScenePlanning/       # Scene designs and plans
├── KeyframePlanning/    # Keyframe specifications
└── KeyframeGeneration/  # Final visual assets
```

## Deliverables

- Visual style guide
- Scene breakdown document
- Keyframe designs
- Generated visual assets
- Asset metadata and organization

## Quality Standards

### Visual Quality
- High resolution
- Consistent style
- Appropriate mood
- Clear composition
- Professional appearance

### Technical Quality
- Proper format and specs
- Consistent dimensions
- Color accuracy
- No artifacts
- Optimized file sizes

## Production Workflow

```
Approved Audio → Visual Style → Scene Design → Keyframe Planning → 
Asset Generation → Quality Check → To Video Assembly
```

## Related Documentation

- [ScenePlanning](./ScenePlanning/README.md) - Scene design stage
- [KeyframePlanning](./KeyframePlanning/README.md) - Keyframe planning stage
- [KeyframeGeneration](./KeyframeGeneration/README.md) - Asset generation stage
- [Content Production Workflow States](../_meta/research/content-production-workflow-states.md)

---

*Part of the PrismQ Content Production Workflow*
