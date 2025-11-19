# VoiceoverApproved

**Workflow Stage: Voiceover Production Phase - Final Approval**

## Overview

The **VoiceoverApproved** stage contains voiceover audio that has completed quality review and is approved for video production.

## Position in Workflow

```
VoiceoverReview → [VoiceoverApproved] → ScenePlanning
```

## Purpose

Maintain a repository of production-ready voiceover audio files that have passed all quality gates and are ready for video assembly.

## Key Characteristics

### Audio Status
- ✅ Quality review complete
- ✅ All revisions implemented
- ✅ Performance approved
- ✅ Technical standards met
- ✅ Locked for production

### Production Readiness
- Final mixed audio
- Proper file format
- Metadata complete
- Timing verified
- Backup copies secured

## File Management

### Naming Convention
```
[ProjectID]_[Title]_Voiceover_v[Version]_[Date].wav

Example:
PQ001_DigitalDetective_Voiceover_v1_20250119.wav
```

### File Organization
```
VoiceoverApproved/
├── [ProjectID]/
│   ├── master/           # Master audio files
│   ├── exports/          # Various format exports
│   ├── backups/          # Backup copies
│   └── metadata/         # Audio metadata
```

### File Formats

**Master Files**
- Format: WAV or FLAC
- Sample Rate: 48kHz
- Bit Depth: 24-bit
- Channels: Mono (preferred) or Stereo

**Export Files**
- MP3 (320kbps) for preview
- AAC for mobile/web
- Platform-specific formats as needed

## Metadata Requirements

Each approved voiceover must include:
- Project ID and title
- Duration (exact timing)
- Voice talent/model name
- Recording/synthesis date
- Approval date and approver
- Version number
- Technical specifications
- Word count and timing markers
- Associated script version

## Approval Process

1. **Final Quality Check** - Last verification
2. **Stakeholder Sign-Off** - Required approvals
3. **Version Lock** - Audio frozen for production
4. **Export Generation** - Create all needed formats
5. **Backup Creation** - Secure copies made
6. **Production Handoff** - Transfer to video team

## Version Control

### Approved Audio Management
- Approved files are locked (read-only)
- Changes require new review cycle
- All versions archived
- Original approval metadata preserved

### Post-Approval Changes
If changes are needed after approval:
1. Create new version
2. Document reason for change
3. Return to VoiceoverReview
4. Re-approval required
5. Update version number

## Deliverables

- Master audio file (locked)
- Export variants (multiple formats)
- Metadata document
- Timing breakdown with markers
- Approval documentation
- Production handoff package

## Integration Points

### Transcript Alignment
- Word-level timing markers
- Subtitle generation data
- Caption synchronization
- Scene timing reference

### Video Production
- Clean audio stems
- Scene-specific segments
- Timing reference files
- Audio specifications document

## Quality Assurance

### Final QA Checklist
- [ ] Audio quality meets standards
- [ ] Performance is approved
- [ ] Timing is accurate
- [ ] File formats correct
- [ ] Metadata complete
- [ ] Backups secured
- [ ] Approval documented
- [ ] Production package ready

## Transition Criteria

Audio moves to ScenePlanning stage when:
- ✅ Final approval documented
- ✅ Master files locked and archived
- ✅ All export formats generated
- ✅ Metadata complete
- ✅ Video team is ready
- ✅ Timing markers available
- ✅ Production specs finalized

## Related Documentation

- [Voiceover Overview](../README.md)
- [VoiceoverReview](../VoiceoverReview/README.md) - Previous stage
- [ScenePlanning](../../Visual/ScenePlanning/README.md) - Next stage
- [Content Production Workflow States](../../_meta/research/content-production-workflow-states.md)

---

*Part of the PrismQ Content Production Workflow*
