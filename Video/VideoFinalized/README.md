# VideoFinalized

**Workflow Stage: Video Production Phase - Final Approval**

## Overview

The **VideoFinalized** stage contains videos that have completed all quality review and corrections, and are approved for publication.

## Position in Workflow

```
VideoReview → [VideoFinalized] → PublishPlanning
```

## Purpose

Maintain a repository of publication-ready video files that have passed all quality gates and are ready for distribution to target platforms.

## Key Characteristics

### Video Status
- ✅ All review feedback addressed
- ✅ Quality standards met
- ✅ Platform compatibility verified
- ✅ Final approval received
- ✅ Locked for publication

### Production Readiness
- Master export files
- Platform-specific versions
- Thumbnail images
- Caption/subtitle files
- Complete metadata package

## File Management

### Naming Convention
```
[ProjectID]_[Title]_[Platform]_[Resolution]_v[Version]_[Date].[ext]

Examples:
PQ001_DigitalDetective_YouTube_1920x1080_v1_20250119.mp4
PQ001_DigitalDetective_TikTok_1080x1920_v1_20250119.mp4
PQ001_DigitalDetective_Instagram_1080x1080_v1_20250119.mp4
```

### File Organization
```
VideoFinalized/
├── [ProjectID]/
│   ├── master/              # Master export (highest quality)
│   ├── youtube/             # YouTube-optimized
│   ├── tiktok/              # TikTok/Reels vertical
│   ├── instagram/           # Instagram formats
│   ├── thumbnails/          # Thumbnail images
│   ├── captions/            # SRT, VTT caption files
│   ├── metadata/            # Descriptions, tags, etc.
│   └── project_archive/     # Editor project files
```

## Export Specifications

### Master Export (Archive)

**Settings**
- Codec: ProRes 422 HQ or H.264 High Profile
- Resolution: Native (1920x1080 or 3840x2160)
- Bitrate: High (50+ Mbps for 1080p, 100+ Mbps for 4K)
- Audio: Uncompressed or AAC 320 kbps
- Purpose: Archive, future re-exports

### YouTube Export

**Settings**
- Codec: H.264
- Resolution: 1920x1080 or 3840x2160
- Frame Rate: Match source (24, 30, or 60 fps)
- Bitrate: 8-15 Mbps (1080p), 35-45 Mbps (4K)
- Audio: AAC 192-320 kbps, 48kHz stereo
- Container: MP4
- Profile: High
- Pixel Format: YUV 4:2:0

### TikTok/Instagram Reels

**Settings**
- Codec: H.264
- Resolution: 1080x1920 (9:16 vertical)
- Frame Rate: 30 fps
- Bitrate: 5-8 Mbps
- Audio: AAC 192 kbps, 48kHz stereo
- Container: MP4
- Max Duration: 60 seconds (TikTok), 90 seconds (Reels)

### Instagram Feed

**Settings**
- Codec: H.264
- Resolution: 1080x1080 (1:1 square)
- Frame Rate: 30 fps
- Bitrate: 5-8 Mbps
- Audio: AAC 192 kbps
- Container: MP4
- Max Duration: 60 seconds

### Facebook

**Settings**
- Codec: H.264
- Resolution: 1920x1080 or 1080x1920
- Frame Rate: 30 fps
- Bitrate: 8-10 Mbps
- Audio: AAC 192 kbps
- Container: MP4

## Thumbnail Creation

### Specifications

**YouTube**
- Resolution: 1280x720 pixels
- Format: JPG or PNG
- Aspect Ratio: 16:9
- File Size: Under 2MB
- Safe Area: Avoid placing text near edges

**TikTok/Instagram**
- Resolution: 1080x1920 (vertical) or 1080x1080 (square)
- Format: JPG or PNG
- File Size: Under 1MB

### Design Guidelines
- Bold, clear imagery
- Readable text (if any)
- High contrast
- Intriguing or informative
- Brand consistent
- Face close-ups work well (if applicable)
- Avoid misleading/clickbait

## Caption Files

### Formats

**SRT (SubRip Text)**
```
1
00:00:00,000 --> 00:00:03,500
Welcome to our investigation into digital mysteries.

2
00:00:03,500 --> 00:00:07,000
Today we're exploring unsolved internet cases.
```

**VTT (WebVTT)**
```
WEBVTT

00:00:00.000 --> 00:00:03.500
Welcome to our investigation into digital mysteries.

00:00:03.500 --> 00:00:07.000
Today we're exploring unsolved internet cases.
```

**YouTube SBV**
```
0:00:00.000,0:00:03.500
Welcome to our investigation into digital mysteries.

0:00:03.500,0:00:07.000
Today we're exploring unsolved internet cases.
```

### Caption Guidelines
- Accurate transcription
- Proper punctuation
- Speaker identification (if needed)
- Sound effects noted [if relevant]
- Line breaks at natural pauses
- Readable duration (3-7 seconds typical)

## Metadata Package

### Required Metadata

**Title**
- Primary title (platform-optimized)
- Title variations per platform
- Character limits respected

**Description**
- Full description (YouTube: 5000 chars)
- Short description (Instagram: 2200 chars)
- Keywords naturally included
- Links and CTAs included
- Timestamps (for YouTube)

**Tags/Keywords**
- 10-15 relevant tags (YouTube)
- Hashtags (Instagram/TikTok: 3-5 main + 5-10 secondary)
- Category selection

**Technical Info**
- Duration
- File size
- Resolution
- Upload date
- Content rating
- Language
- License info

### Platform-Specific Metadata

**YouTube**
```
Title: [60 chars max]
Description: [Full description with timestamps]
Tags: [Comma-separated keywords]
Category: [Education, Entertainment, etc.]
Thumbnail: [Filename]
End Screen: [Template or links]
Cards: [Timestamps and links]
Chapters: [Timestamp list]
```

**TikTok**
```
Caption: [150 chars recommended]
Hashtags: [3-5 relevant tags]
Cover: [Selected frame or custom]
Privacy: [Public/Friends/Private]
Comments: [Enabled/Disabled]
Duet/Stitch: [Allowed/Not Allowed]
```

**Instagram**
```
Caption: [2200 chars max]
Hashtags: [30 max, 5-10 recommended]
Location: [Optional]
Tag People: [If applicable]
Alt Text: [Accessibility description]
```

## Version Control

### Approved Video Management
- Finalized videos are locked (read-only)
- Changes require new production cycle
- All versions archived
- Export settings documented

### Re-Export Protocol
If re-export needed after finalization:
1. Document reason for re-export
2. Update version number
3. Re-run quality checks
4. Update metadata
5. Archive previous version

## Deliverables

- Master video file (archived)
- All platform-specific exports
- Thumbnail images (all sizes)
- Caption files (all formats)
- Complete metadata package
- Export settings documentation
- Project archive (compressed)
- Publication checklist

## Quality Assurance

### Final QA Checklist
- [ ] Master file exported and archived
- [ ] All platform versions exported
- [ ] Thumbnails created for all platforms
- [ ] Captions generated and timed
- [ ] Metadata complete for all platforms
- [ ] File naming convention followed
- [ ] Project files archived
- [ ] Backup copies secured
- [ ] Ready for publication

## Transition Criteria

Video moves to PublishPlanning when:
- ✅ All export files generated
- ✅ Thumbnails created
- ✅ Captions finalized
- ✅ Complete metadata prepared
- ✅ Quality verification passed
- ✅ Archive backups secured
- ✅ Publication checklist complete
- ✅ Publishing team is ready

## Archive Storage

### Short-Term (Active)
- All finalized videos and assets
- Easily accessible for publishing
- Local and cloud storage
- 1-3 month retention

### Long-Term (Archive)
- Master files and project files
- Full metadata
- Compressed and deduplicated
- Cloud archive storage
- Indefinite retention

## Related Documentation

- [Video Overview](../README.md)
- [VideoReview](../VideoReview/README.md) - Previous stage
- [PublishPlanning](../../Publishing/PublishPlanning/README.md) - Next stage
- [Content Production Workflow States](../../_meta/research/content-production-workflow-states.md)

---

*Part of the PrismQ Content Production Workflow*
