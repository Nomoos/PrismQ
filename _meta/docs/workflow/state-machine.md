# PrismQ Content Production Workflow

**Complete State Machine for Content Production from Inspiration to Archive**

> 📖 **See also**: 
> - [MVP Workflow Overview](./mvp-overview.md) for detailed 26-stage workflow principles
> - [Workflow Documentation Index](./README.md) for complete navigation

## Overview

This document defines the complete workflow state machine for PrismQ content production, from initial inspiration through publication and analytics to final archival.

## Workflow State Diagram

```mermaid
stateDiagram-v2
    [*] --> IdeaInspiration
    IdeaInspiration --> Idea
    IdeaInspiration --> Archived

    state Idea {
        [*] --> Creation
        Creation --> Outline
        Outline --> Title

        Title --> [*]   %% Title is the final substate before exiting Idea
    }

    Idea --> ScriptDraft
    Idea --> IdeaInspiration
    Idea --> Archived
    
    ScriptDraft --> ScriptReview
    ScriptDraft --> Idea
    ScriptDraft --> Archived

    ScriptReview --> ScriptApproved
    ScriptReview --> ScriptDraft
    ScriptReview --> Idea
    ScriptReview --> Archived

    ScriptApproved --> TextPublishing
    ScriptApproved --> ScriptReview
    ScriptApproved --> Archived

    %% Text Publication Branch
    TextPublishing --> PublishedText
    TextPublishing --> ScriptApproved
    TextPublishing --> Archived

    PublishedText --> Voiceover
    PublishedText --> AnalyticsReviewText
    PublishedText --> Archived

    AnalyticsReviewText --> Archived
    AnalyticsReviewText --> IdeaInspiration

    %% Audio Production uses published text
    Voiceover --> VoiceoverReview
    Voiceover --> PublishedText
    Voiceover --> Archived

    VoiceoverReview --> VoiceoverApproved
    VoiceoverReview --> Voiceover
    VoiceoverReview --> PublishedText
    VoiceoverReview --> Archived

    VoiceoverApproved --> AudioPublishing
    VoiceoverApproved --> VoiceoverReview
    VoiceoverApproved --> Archived

    %% Audio Publication Branch
    AudioPublishing --> PublishedAudio
    AudioPublishing --> VoiceoverApproved
    AudioPublishing --> Archived

    PublishedAudio --> ScenePlanning
    PublishedAudio --> AnalyticsReviewAudio
    PublishedAudio --> Archived

    AnalyticsReviewAudio --> Archived
    AnalyticsReviewAudio --> IdeaInspiration

    %% Video Production uses published audio
    ScenePlanning --> KeyframePlanning
    ScenePlanning --> PublishedAudio
    ScenePlanning --> Archived

    KeyframePlanning --> KeyframeGeneration
    KeyframePlanning --> ScenePlanning
    KeyframePlanning --> Archived

    KeyframeGeneration --> VideoAssembly
    KeyframeGeneration --> KeyframePlanning
    KeyframeGeneration --> Archived

    VideoAssembly --> VideoReview
    VideoAssembly --> KeyframeGeneration
    VideoAssembly --> Archived

    VideoReview --> VideoFinalized
    VideoReview --> VideoAssembly
    VideoReview --> KeyframeGeneration
    VideoReview --> Archived

    VideoFinalized --> PublishPlanning
    VideoFinalized --> VideoReview
    VideoFinalized --> Archived

    %% Video Publication Branch
    PublishPlanning --> PublishedVideo
    PublishPlanning --> VideoFinalized
    PublishPlanning --> Archived

    PublishedVideo --> AnalyticsReviewVideo
    PublishedVideo --> Archived

    AnalyticsReviewVideo --> Archived
    AnalyticsReviewVideo --> IdeaInspiration
```

