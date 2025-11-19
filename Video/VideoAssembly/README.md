# VideoAssembly

**Workflow Stage: Video Production Phase - Assembly & Editing**

## Overview

The **VideoAssembly** stage represents the phase where audio, visuals, and effects are combined into a cohesive video sequence.

## Position in Workflow

```
KeyframeGeneration → [VideoAssembly] → VideoReview → VideoFinalized
```

## Purpose

Synchronize voices, visuals, and pacing to form the final video. This stage focuses on:

- Timeline construction
- Audio-visual synchronization
- Effect and transition application
- Initial color correction
- Preliminary audio mixing

## Key Activities

1. **Setup Project** - Configure editor with correct settings
2. **Import Assets** - Load all audio, visual, and supporting files
3. **Build Timeline** - Arrange clips in sequence
4. **Sync Audio-Visual** - Align visuals to voiceover timing
5. **Add Effects** - Apply transitions, text, graphics, animations
6. **Initial Color** - Basic color correction and grading
7. **Audio Mix** - Balance voice, music, sound effects
8. **Test Render** - Create preview for review

## Assembly Process

### 1. Project Setup

**Create New Project**
```
Project Name: [ProjectID]_[Title]_[Date]
Resolution: 1920x1080 (or target resolution)
Frame Rate: 30 fps (or target frame rate)
Audio: 48kHz, Stereo
Color Space: Rec. 709
```

**Import Organization**
```
Timeline/
├── Audio/
│   ├── Voiceover/
│   ├── Music/
│   └── SFX/
├── Video/
│   ├── Keyframes/
│   ├── B-Roll/
│   └── Graphics/
└── Sequences/
    └── Master/
```

### 2. Timeline Construction

**Track Layout** (typical)
```
V5: Upper Graphics/Text
V4: Lower Graphics/Text  
V3: Effects/Overlays
V2: B-Roll/Secondary Visuals
V1: Primary Visuals (Keyframes)

A3: Sound Effects
A2: Background Music
A1: Voiceover (Master)
```

**Timing Reference**
- Use voiceover audio as timing foundation
- Mark key beats and transitions
- Place visual cuts at natural audio pauses
- Maintain visual-audio sync throughout

### 3. Visual Sequence

**Scene Assembly**
1. Place keyframes according to scene plan
2. Trim to match audio timing
3. Add transition effects between scenes
4. Adjust duration for pacing

**Transitions**
- Cuts (instant, most common)
- Crossfades (dissolve, 0.5-1.5 seconds)
- Wipes (directional, stylistic)
- Custom (creative effects)

**Text/Graphics**
- Lower thirds for context
- Title cards for sections
- Callouts for emphasis
- Credits and attribution

### 4. Effects Application

**Visual Effects**
- Zoom/pan (Ken Burns effect)
- Color filters
- Vignettes
- Blur/focus effects
- Speed ramping

**Motion Graphics**
- Animated text
- Logo animations
- Infographics
- Transitions
- Overlays

**Audio Effects**
- Voiceover EQ and compression
- Music ducking (under voice)
- Sound effect levels
- Fade ins/outs
- Room tone/ambience

### 5. Synchronization

**Audio-Visual Alignment**
- Visuals change on audio cues
- Emphasis visuals match voice emphasis
- Pacing visuals match audio energy
- Transitions align with audio breaks

**Timing Markers**
```
00:00 - Opening/Hook
00:15 - Title/Branding
00:30 - Introduction
02:00 - Main Content Pt. 1
05:00 - Transition
05:15 - Main Content Pt. 2
08:00 - Conclusion
09:30 - Call to Action
10:00 - End Card
```

### 6. Music & Sound Design

**Background Music**
- Start under opening
- Duck (reduce volume) during voiceover
- Swell during transitions or key moments
- Fade out before end

**Sound Effects**
- Transition whooshes
- Emphasis sounds (ding, pop)
- Ambient sounds for context
- Don't overuse - less is more

**Audio Levels**
- Voiceover: -6 dB to -3 dB peak
- Music: -20 dB to -15 dB (under voice)
- SFX: -12 dB to -6 dB (brief)
- Final Mix: -14 LUFS (web standard)

### 7. Color Correction

**Basic Correction**
- Exposure adjustment
- White balance
- Contrast enhancement
- Saturation adjustment

**Consistency**
- Match keyframes in same scene
- Consistent skin tones (if applicable)
- Maintain mood/atmosphere
- Platform color space compliance

### 8. Preview Render

**Test Export Settings**
- Resolution: 1920x1080
- Codec: H.264
- Bitrate: 10 Mbps
- Quality: Preview/Draft
- Purpose: Review and feedback

## Deliverables

- Assembled timeline (project file)
- Preview render (draft quality)
- Edit decision list (EDL)
- Assembly notes document
- Asset usage report

## Quality Checkpoints

Before moving to VideoReview:
- [ ] All assets imported and placed
- [ ] Audio-visual sync is correct
- [ ] All scenes included per plan
- [ ] Transitions applied appropriately
- [ ] Text/graphics are visible and clear
- [ ] Audio levels are balanced
- [ ] Basic color correction applied
- [ ] No technical errors (dropped frames, artifacts)
- [ ] Preview render complete

## Common Issues

### Sync Problems
- Visuals don't match audio timing
- Music overlaps voiceover awkwardly
- Transitions interrupt audio flow

### Visual Issues
- Text hard to read (size, contrast)
- Too fast cuts (viewer can't process)
- Too slow pacing (viewer loses interest)
- Inconsistent style between scenes

### Audio Issues
- Music too loud (drowns voice)
- Inconsistent volume levels
- Abrupt cuts without fades
- Background noise audible

## Transition Criteria

Assembly moves to VideoReview when:
- ✅ Complete timeline assembled
- ✅ All planned scenes included
- ✅ Audio-visual sync verified
- ✅ Effects and transitions applied
- ✅ Preview render generated
- ✅ Self-QA completed
- ✅ Ready for editorial review

## Related Documentation

- [Video Overview](../README.md)
- [VideoReview](../VideoReview/README.md) - Next stage
- [Content Production Workflow States](../../_meta/research/content-production-workflow-states.md)

---

*Part of the PrismQ Content Production Workflow*
