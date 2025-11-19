# KeyframePlanning

**Workflow Stage: Visual Production Phase - Keyframe Design**

## Overview

The **KeyframePlanning** stage represents the phase where specific keyframes are designed and specified for generation or creation.

## Position in Workflow

```
ScenePlanning → [KeyframePlanning] → KeyframeGeneration → VideoAssembly
```

## Purpose

Design specific keyframes (key visual moments) that will serve as the foundation for each scene. This stage creates:

- Detailed keyframe specifications
- Visual reference frames
- Style consistency templates
- Generation prompts (for AI)
- Asset sourcing instructions

## Key Activities

1. **Identify Key Frames** - Determine which frames need detailed design
2. **Create Specifications** - Detail visual requirements for each keyframe
3. **Design Reference** - Sketch or mock up keyframe concepts
4. **Write Prompts** - Create AI generation prompts (if using AI)
5. **Plan Sourcing** - Identify stock or custom asset needs

## Keyframe Types

### Hero Keyframes
- Main visual focus of a scene
- High detail and quality
- Establish scene tone
- Duration on screen: 3-8 seconds

### Transition Keyframes
- Bridge between scenes
- Visual continuity elements
- Smooth flow design
- Duration on screen: 1-3 seconds

### Supporting Keyframes
- Secondary visual elements
- B-roll and context
- Variety and pacing
- Duration on screen: 2-5 seconds

### Title/Text Keyframes
- Typography-focused
- Minimal imagery
- Clear messaging
- Duration on screen: 2-6 seconds

## Keyframe Specification Template

```
Keyframe ID: [KF-001]
Scene: [Scene Number/Name]
Type: [Hero/Transition/Supporting/Title]
Timing: [Start Time] - [End Time]
Duration: [XX seconds]

Visual Description:
[Detailed description of what should be visible]

Composition:
- Foreground: [Elements]
- Midground: [Elements]
- Background: [Elements]
- Focal Point: [Primary focus]

Style Requirements:
- Color Palette: [Colors]
- Mood: [Emotional tone]
- Lighting: [Bright/Dark/Dramatic/etc.]
- Perspective: [Angle/viewpoint]

Technical Specs:
- Resolution: [1920x1080, etc.]
- Format: [PNG/JPEG]
- Aspect Ratio: [16:9, 9:16, 1:1]

AI Generation Prompt (if applicable):
[Detailed prompt for AI image generation]

Alternative Sourcing:
- Stock search terms
- Custom creation brief
- Reference images

Quality Requirements:
[Specific quality criteria]
```

## Planning Process

1. **Review Scene Plan** - Understand each scene's requirements
2. **Identify Keyframes** - Determine which moments need specific design
3. **Prioritize Frames** - Rank by importance and complexity
4. **Create Specifications** - Detail each keyframe's requirements
5. **Prepare Generation Strategy** - Plan how each will be created

## AI Generation Planning

### Prompt Engineering
- Positive prompts (what to include)
- Negative prompts (what to avoid)
- Style keywords
- Quality modifiers
- Technical parameters

### Example AI Prompt Structure
```
[Subject], [Action], [Environment], 
[Style], [Lighting], [Mood], [Quality modifiers]

Example:
"Cyberpunk detective standing in rain-soaked neon city street,
noir style, dramatic rim lighting, moody atmosphere, 
cinematic composition, high detail, professional photography,
8k resolution"
```

### Batch Generation Planning
- Group similar styles
- Consistent parameters
- Seed management
- Variation strategy

## Stock Asset Planning

### Search Strategy
- Primary keywords
- Alternative terms
- Filter requirements
- License needs

### Selection Criteria
- Quality standards
- Style consistency
- Resolution requirements
- License compatibility

## Custom Creation Planning

### Illustration Briefs
- Visual concept
- Style reference
- Color specifications
- Delivery format

### Motion Graphics Specs
- Animation type
- Duration
- Frame rate
- Export format

## Deliverables

- Keyframe specification document
- Reference sketches or mockups
- AI generation prompts
- Stock search terms list
- Custom creation briefs
- Quality control checklist

## Quality Checkpoints

Before moving to KeyframeGeneration:
- [ ] All keyframes identified and specified
- [ ] Generation strategy defined for each
- [ ] Prompts or briefs are detailed
- [ ] Style consistency ensured
- [ ] Technical specs documented
- [ ] Resource requirements clear
- [ ] Timeline is realistic

## Transition Criteria

Planning moves to KeyframeGeneration when:
- ✅ Complete keyframe specifications exist
- ✅ All generation methods determined
- ✅ Prompts/briefs are finalized
- ✅ Style guide compliance verified
- ✅ Resource allocation approved
- ✅ Quality standards defined
- ✅ Ready for production execution

## Organization Best Practices

### File Naming
```
[ProjectID]_KF[Number]_[SceneName]_[Type]_v[Version]

Example:
PQ001_KF003_Opening_Hero_v1
```

### Folder Structure
```
KeyframePlanning/
├── [ProjectID]/
│   ├── specifications/  # Detailed specs
│   ├── references/      # Visual references
│   ├── prompts/         # AI prompts
│   └── briefs/          # Creation briefs
```

## Related Documentation

- [Visual Overview](../README.md)
- [ScenePlanning](../ScenePlanning/README.md) - Previous stage
- [KeyframeGeneration](../KeyframeGeneration/README.md) - Next stage
- [Content Production Workflow States](../../_meta/research/content-production-workflow-states.md)

---

*Part of the PrismQ Content Production Workflow*
