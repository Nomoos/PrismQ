# KeyframeGeneration

**Workflow Stage: Visual Production Phase - Asset Creation**

## Overview

The **KeyframeGeneration** stage represents the execution phase where planned keyframes are generated, created, or sourced as production-ready visual assets.

## Position in Workflow

```
KeyframePlanning → [KeyframeGeneration] → VideoAssembly
```

## Purpose

Generate or create the actual visual assets specified in the keyframe planning phase. This stage produces:

- High-quality visual assets
- Style-consistent imagery
- Production-ready files
- Asset metadata
- Quality-controlled deliverables

## Key Activities

1. **Generate AI Images** - Create images using AI tools (Stable Diffusion, DALL-E, etc.)
2. **Source Stock Media** - Acquire licensed stock photos/videos
3. **Commission Custom Work** - Brief and receive custom illustrations/designs
4. **Quality Control** - Verify all assets meet standards
5. **Asset Management** - Organize and prepare files for video assembly

## Generation Methods

### AI Image Generation

**Tools**
- Stable Diffusion (Local or Cloud)
- DALL-E 3
- Midjourney
- Leonardo.ai
- Firefly

**Process**
1. Load generation prompts from KeyframePlanning
2. Configure generation parameters
3. Generate initial batch
4. Review and select best results
5. Refine with additional generations if needed
6. Upscale to production resolution
7. Apply any post-processing

**Quality Control**
- Resolution check (1920x1080 minimum)
- Style consistency with scene plan
- No visible artifacts or errors
- Appropriate for content rating
- Matches prompt specifications

### Stock Media Sourcing

**Sources**
- Shutterstock
- Adobe Stock
- Pexels (free)
- Unsplash (free)
- Pixabay (free)
- Storyblocks

**Process**
1. Use search terms from KeyframePlanning
2. Filter by quality and license
3. Preview and select assets
4. Download in highest resolution
5. Verify license compatibility
6. Document attribution if required

**License Management**
- Track license type (royalty-free, rights-managed, creative commons)
- Store license documentation
- Note attribution requirements
- Maintain purchase records

### Custom Creation

**Process**
1. Send brief from KeyframePlanning to creator
2. Review initial concepts/drafts
3. Request revisions if needed
4. Receive final assets
5. Verify deliverables match specifications
6. Archive source files

**File Formats**
- Vector: AI, EPS, SVG
- Raster: PSD, PNG, TIFF
- Export: PNG (transparency), JPEG (final)

## Technical Specifications

### Image Requirements

**Resolution**
- Full HD: 1920x1080 pixels
- 4K: 3840x2160 pixels
- Vertical (TikTok/Reels): 1080x1920
- Square (Instagram): 1080x1080

**Format**
- PNG: For transparency, text overlays, graphics
- JPEG: For photographs, backgrounds
- TIFF: For archival/source files

**Color**
- Color Space: sRGB
- Bit Depth: 8-bit minimum, 16-bit for editing
- Profile: sRGB IEC61966-2.1

**Quality**
- No compression artifacts
- Sharp focus (or intentional blur)
- Proper exposure and color balance
- Clean edges (no generation artifacts)

### Video Requirements (if applicable)

**Specifications**
- Resolution: 1920x1080 or 3840x2160
- Frame Rate: 24, 30, or 60 fps
- Codec: H.264 or ProRes
- Format: MP4 or MOV
- Duration: As specified in planning

## File Organization

### Naming Convention
```
[ProjectID]_[SceneName]_KF[Number]_[Version]_[Resolution].[ext]

Example:
PQ001_Opening_KF003_v2_1920x1080.png
```

### Folder Structure
```
KeyframeGeneration/
├── [ProjectID]/
│   ├── master/           # Original high-res files
│   ├── production/       # Production-ready exports
│   ├── sources/          # Source files (PSD, AI, etc.)
│   ├── metadata/         # Asset metadata and licenses
│   └── rejected/         # Discarded generations
```

### Metadata Tracking

Each asset should have:
- Keyframe ID
- Scene reference
- Generation method (AI/Stock/Custom)
- Source (tool name, stock site, artist)
- License information
- Creation date
- Version number
- Technical specs
- Quality approval status

## Quality Assurance

### Pre-Delivery Checklist
- [ ] Correct resolution and format
- [ ] Style matches scene plan
- [ ] No visible artifacts or errors
- [ ] Appropriate content rating
- [ ] License/usage rights confirmed
- [ ] Metadata documented
- [ ] File naming convention followed
- [ ] Backup copies secured

### Common Issues to Check

**AI-Generated Images**
- Anatomical errors (hands, faces)
- Text/sign gibberish
- Inconsistent lighting/shadows
- Style drift from prompt
- Low resolution or blur

**Stock Images**
- Watermarks present
- Wrong license type
- Low resolution
- Style mismatch
- Overused/cliché imagery

**Custom Assets**
- Off-brief elements
- Technical format issues
- Resolution insufficient
- Color space incorrect

## Deliverables

- All keyframe assets (production-ready)
- Asset metadata spreadsheet
- License documentation
- Source files (archived)
- Quality control report
- Production handoff package

## Post-Processing

### Enhancement Steps
- Color correction/grading
- Sharpening or noise reduction
- Cropping/composition adjustment
- Text or graphic overlays
- Export optimization

### Tools
- Photoshop
- GIMP (free)
- Affinity Photo
- DaVinci Resolve
- After Effects

## Transition Criteria

Assets move to VideoAssembly when:
- ✅ All planned keyframes generated
- ✅ Quality standards met
- ✅ Licenses documented
- ✅ Files properly organized
- ✅ Metadata complete
- ✅ Production specs verified
- ✅ Approval received

## Related Documentation

- [Visual Overview](../README.md)
- [KeyframePlanning](../KeyframePlanning/README.md) - Previous stage
- [VideoAssembly](../../Video/VideoAssembly/README.md) - Next stage
- [Content Production Workflow States](../../_meta/research/content-production-workflow-states.md)

---

*Part of the PrismQ Content Production Workflow*
