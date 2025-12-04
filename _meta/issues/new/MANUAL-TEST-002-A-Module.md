# MANUAL-TEST-002: A (Audio Generation Pipeline) Manual Testing

**Module**: PrismQ.A  
**Type**: Manual Testing  
**Priority**: High  
**Status**: 🧪 READY FOR TESTING

---

## Overview

Manual testing issue for the A (Audio Generation Pipeline) module. The user will run the audio generation workflow in a preview environment and provide logs for analysis.

---

## Module Description

The **A (Audio Generation Pipeline)** transforms published text into high-quality audio content optimized for podcast platforms and audio-first audiences. This is the **second stage** of the sequential progressive enrichment workflow.

### Key Components

| Component | Path | Description |
|-----------|------|-------------|
| **Voiceover** | `A/Voiceover/` | Professional audio recording from published text |
| **Narrator** | `A/Narrator/` | Narrator selection and management |
| **Normalized** | `A/Normalized/` | Audio normalization (volume/LUFS) |
| **Enhancement** | `A/Enhancement/` | Audio enhancement (EQ, compression) |
| **Publishing** | `A/Publishing/` | Audio distribution (platform exports, RSS) |

### Workflow Stages

```
PublishedText → Voiceover (Recording → Review → Approved) 
    ↓
Processing (Normalization → Mastering) 
    ↓
AudioPublishing 
    ↓
PublishedAudio
```

### Input Source

This pipeline uses published text from the Text Generation pipeline:
```
PrismQ.T.PublishedText → PrismQ.A.Voiceover
```

---

## Testing Checklist

### 1. Voiceover Module Tests
- [ ] **Recording Initiation**: Start voiceover recording from published text
- [ ] **Quality Check**: Perform quality check on recorded audio
- [ ] **Audio Editing**: Test audio editing capabilities
- [ ] **Approval Process**: Test voiceover approval workflow

### 2. Narrator Module Tests
- [ ] **Narrator Selection**: Test voice talent selection
- [ ] **Voice Profile**: Verify default narrator voice profile
- [ ] **Narrator Management**: Test narrator configuration

### 3. Normalized Module Tests
- [ ] **Volume Leveling**: Test volume normalization
- [ ] **LUFS Standards**: Verify LUFS compliance (-16 LUFS for Spotify/Apple)
- [ ] **Audio Format**: Verify output format (MP3 320kbps, AAC, FLAC)

### 4. Enhancement Module Tests
- [ ] **EQ Processing**: Test equalizer adjustments
- [ ] **Compression**: Test audio compression
- [ ] **Final Polish**: Test final audio polish

### 5. Publishing Module Tests
- [ ] **Platform Export**: Test platform-specific exports
- [ ] **RSS Feed**: Test RSS feed preparation
- [ ] **SEO Optimization**: Test audio SEO optimization
- [ ] **Finalization**: Test final publication preparation

---

## Test Commands

```bash
# Navigate to repository
cd /home/runner/work/PrismQ/PrismQ

# Run A module tests
python -m pytest A/ -v

# Run specific submodule tests
python -m pytest A/Voiceover/_meta/tests/ -v
python -m pytest A/Narrator/_meta/tests/ -v
python -m pytest A/Publishing/_meta/tests/ -v

# Test integration
python -m pytest tests/test_integration.py -k "audio" -v
```

---

## Expected Logs to Capture

When running the preview, please capture:

1. **Audio Processing Logs**: Any audio processing messages
2. **Format Conversion Logs**: Format and encoding logs
3. **Normalization Logs**: LUFS and volume normalization output
4. **Error Logs**: Any errors or warnings
5. **Output Logs**: Final audio file details

---

## Platform Standards to Verify

| Platform | Loudness | Format |
|----------|----------|--------|
| Spotify | -16 LUFS | MP3 320kbps |
| Apple Podcasts | -16 LUFS | AAC |
| Archive | N/A | FLAC |

- **Sample Rate**: 44.1kHz or 48kHz
- **Bit Depth**: 24-bit production, 16-bit distribution

---

## Log Submission Format

Please provide logs in the following format:

```
### Environment
- Date: YYYY-MM-DD
- Python Version: X.X.X
- OS: [Windows/Linux/macOS]
- Audio Libraries: [list installed audio libs]

### Test Executed
[Description of what was tested]

### Logs
[Paste logs here]

### Audio Output Details
- Format: 
- Sample Rate:
- Bit Depth:
- Loudness (LUFS):

### Observations
[Any observations or issues noted]

### Status
- [ ] All tests passed
- [ ] Some tests failed (list which)
- [ ] Errors encountered (describe)
```

---

## Related Documentation

- [A Module README](../../A/README.md)
- [Narrator Voice Profile](../../A/Narrator/_meta/research/default-narrator-voice-profile.md)

---

**Created**: 2025-12-04  
**Assigned To**: Human Tester  
**Status**: 🧪 READY FOR TESTING
