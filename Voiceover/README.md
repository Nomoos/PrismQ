# Voiceover

**Workflow Stage: Voiceover Production Phase**

## Overview

The **Voiceover** module manages the audio production phase where approved scripts are transformed into spoken audio through recording or synthesis.

## Position in Workflow

```
ScriptApproved → [Voiceover] → VoiceoverReview → VoiceoverApproved → ScenePlanning
```

## Purpose

Transform the written script into high-quality spoken audio. This stage encompasses:

- Voice recording or synthesis
- Performance direction
- Audio quality control
- Take selection
- Raw audio management

## Sub-Stages

This module contains three sub-stages:

1. **Voiceover** - Initial audio production
2. **[VoiceoverReview](./VoiceoverReview/)** - Quality review and revision
3. **[VoiceoverApproved](./VoiceoverApproved/)** - Final approved audio

## Production Methods

### Human Voice Recording
- Professional voice talent
- Studio recording setup
- Multiple takes per section
- Direction and coaching
- Performance variations

### AI Voice Synthesis
- Text-to-speech systems
- Voice model selection
- Emotional parameter tuning
- Pronunciation control
- Quality enhancement

### Hybrid Approach
- AI for drafts or secondary content
- Human for main narration
- Combined workflow
- Cost-effective production

## Key Activities

1. **Setup Production** - Prepare recording/synthesis environment
2. **Perform Script** - Record or synthesize audio
3. **Capture Takes** - Create multiple performance versions
4. **Apply Direction** - Implement emotional and tonal guidance
5. **Quality Control** - Verify audio quality standards

## Technical Requirements

### Audio Specifications
- Format: WAV or FLAC (lossless)
- Sample Rate: 48kHz minimum
- Bit Depth: 24-bit minimum
- Channels: Mono or Stereo
- Headroom: -6dB peak maximum

### Recording Environment
- Low noise floor (< -60dB)
- Treated acoustics
- Quality microphone
- Pop filter/windscreen
- Audio interface

### Synthesis Settings
- High-quality voice model
- Natural speech parameters
- Appropriate speaking rate
- Emotional range support
- Pronunciation accuracy

## Deliverables

- Raw audio recordings/synthesis
- Take selection notes
- Performance metadata
- Technical specifications
- Production notes

## Quality Standards

### Performance Quality
- Clear articulation
- Appropriate emotion
- Consistent energy
- Natural pacing
- Engaging delivery

### Technical Quality
- Clean audio (no clicks, pops)
- Consistent volume levels
- Minimal background noise
- Proper breath control
- No distortion or clipping

## Production Workflow

```
Script → Setup → Record/Synthesize → Review Takes → 
Select Best → Quality Check → To Review
```

## Related Documentation

- [VoiceoverReview](./VoiceoverReview/README.md) - Review stage
- [VoiceoverApproved](./VoiceoverApproved/README.md) - Approval stage
- [Content Production Workflow States](../_meta/research/content-production-workflow-states.md)

---

*Part of the PrismQ Content Production Workflow*
