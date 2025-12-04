# MANUAL-TEST-003: V (Video Generation Pipeline) Manual Testing

**Module**: PrismQ.V  
**Type**: Manual Testing  
**Priority**: High  
**Status**: 🧪 READY FOR TESTING

---

## Overview

Manual testing issue for the V (Video Generation Pipeline) module. The user will run the video generation workflow in a preview environment and provide logs for analysis.

---

## Module Description

The **V (Video Generation Pipeline)** transforms published audio into engaging video content with synchronized visuals, optimized for video platforms. This is the **third and final stage** of the sequential progressive enrichment workflow.

### Key Components

| Component | Path | Description |
|-----------|------|-------------|
| **Scene** | `V/Scene/` | Scene planning from published audio |
| **Keyframe** | `V/Keyframe/` | Keyframe planning and generation |
| **Video** | `V/Video/` | Video assembly and production |

### Workflow Stages

```
PublishedAudio → Visual (ScenePlanning → KeyframePlanning → KeyframeGeneration) 
    ↓
Assembly (Timeline → Review → Finalized) 
    ↓
Publishing 
    ↓
PublishedVideo
```

### Input Source

This pipeline uses published audio from the Audio Generation pipeline:
```
PrismQ.A.PublishedAudio → PrismQ.V.ScenePlanning
```

---

## Testing Checklist

### 1. Scene Module Tests
- [ ] **Scene Planning**: Plan scenes based on published audio
- [ ] **Scene From Subtitles**: Generate scenes from subtitles/transcript
- [ ] **Visual Style**: Define visual style and timing
- [ ] **Scene Transitions**: Plan transitions between scenes

### 2. Keyframe Module Tests
- [ ] **Keyframe Planning**: Identify key visual moments
- [ ] **From Text Scenes**: Generate keyframes from text scenes
- [ ] **Combined Generation**: Test combined keyframe generation
- [ ] **Keyframe Timing**: Verify keyframe timing alignment with audio

### 3. Video Module Tests
- [ ] **Video Assembly**: Assemble visuals with audio
- [ ] **Audio Sync**: Verify audio synchronization
- [ ] **Transitions**: Apply transitions and effects
- [ ] **Final Render**: Test final video rendering

### 4. Publishing Tests
- [ ] **YouTube Export**: Test 1920x1080 (16:9) format
- [ ] **TikTok Export**: Test 1080x1920 (9:16) format
- [ ] **Instagram Export**: Test 1080x1080 (1:1) format
- [ ] **Thumbnail Generation**: Test thumbnail creation

---

## Test Commands

```bash
# Navigate to repository
cd /home/runner/work/PrismQ/PrismQ

# Run V module tests
python -m pytest V/ -v

# Run specific submodule tests
python -m pytest V/Scene/_meta/tests/ -v
python -m pytest V/Keyframe/_meta/tests/ -v
python -m pytest V/Video/_meta/tests/ -v

# Test integration
python -m pytest tests/test_integration.py -k "video" -v
```

---

## Expected Logs to Capture

When running the preview, please capture:

1. **Scene Planning Logs**: Scene breakdown and timing
2. **Keyframe Generation Logs**: Keyframe creation output
3. **Rendering Logs**: Video assembly and rendering progress
4. **Format Conversion Logs**: Platform-specific format conversions
5. **Error Logs**: Any errors or warnings
6. **Output Logs**: Final video file details

---

## Platform Specifications to Verify

| Platform | Resolution | Aspect Ratio | Notes |
|----------|------------|--------------|-------|
| YouTube | 1920x1080 | 16:9 | Thumbnails, CTR optimization |
| TikTok | 1080x1920 | 9:16 | Hook in first 3 seconds |
| Instagram Reels | 1080x1920 | 9:16 | Retention focus |
| Instagram Square | 1080x1080 | 1:1 | Alternative format |

- **Frame Rate**: 24fps (cinematic), 30fps (standard), 60fps (smooth)

---

## Log Submission Format

Please provide logs in the following format:

```
### Environment
- Date: YYYY-MM-DD
- Python Version: X.X.X
- OS: [Windows/Linux/macOS]
- Video Libraries: [list installed video libs - ffmpeg, etc.]

### Test Executed
[Description of what was tested]

### Logs
[Paste logs here]

### Video Output Details
- Resolution: 
- Aspect Ratio:
- Frame Rate:
- Duration:
- File Size:
- Codec:

### Observations
[Any observations or issues noted]

### Status
- [ ] All tests passed
- [ ] Some tests failed (list which)
- [ ] Errors encountered (describe)
```

---

## Related Documentation

- [V Module README](../../V/README.md)
- [Scene Module README](../../V/Scene/README.md)
- [Keyframe Module README](../../V/Keyframe/README.md)
- [Video Module README](../../V/Video/README.md)

---

**Created**: 2025-12-04  
**Assigned To**: Human Tester  
**Status**: 🧪 READY FOR TESTING
