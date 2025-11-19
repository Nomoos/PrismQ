"""Tests for the ContentFunnel content transformation system.

This module tests the funnel concept where content flows through
transformation stages: Video → Audio → Text, Audio → Text, or Text (passthrough).
"""

import sys
from pathlib import Path
import pytest
from typing import Optional, Dict, Any

# Add paths for imports
source_path = Path(__file__).parent.parent.parent.parent / "src"
model_path = Path(__file__).parent.parent.parent.parent.parent / "Model" / "src"
if str(source_path) not in sys.path:
    sys.path.insert(0, str(source_path))
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from core.content_funnel import (  # noqa: E402
    ContentFunnel,
    TransformationStage,
    TransformationMetadata,
    AudioExtractor,  # Protocol, imported for type hints
    AudioTranscriber,  # Protocol, imported for type hints
    SubtitleExtractor,  # Protocol, imported for type hints
)
from idea_inspiration import IdeaInspiration, ContentType  # noqa: E402


class MockAudioExtractor:
    """Mock audio extractor for testing."""

    def __init__(self, should_succeed: bool = True):
        self.should_succeed = should_succeed
        self.call_count = 0

    def extract_audio(
        self,
        video_url: str,
        video_id: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Mock audio extraction."""
        self.call_count += 1
        if not self.should_succeed:
            return None

        return {
            'audio_url': f"{video_url}.audio",
            'audio_format': 'mp3',
            'duration': 180,
        }


class MockAudioTranscriber:
    """Mock audio transcriber for testing."""

    def __init__(self, should_succeed: bool = True, confidence: float = 95.0):
        self.should_succeed = should_succeed
        self.confidence = confidence
        self.call_count = 0

    def transcribe_audio(
        self,
        audio_url: str,
        audio_id: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Mock audio transcription."""
        self.call_count += 1
        if not self.should_succeed:
            return None

        return {
            'text': f"Transcribed text from {audio_url}",
            'confidence': self.confidence,
            'language': language or 'en',
        }


class MockSubtitleExtractor:
    """Mock subtitle extractor for testing."""

    def __init__(self, should_succeed: bool = True):
        self.should_succeed = should_succeed
        self.call_count = 0

    def extract_subtitles(
        self,
        video_url: str,
        video_id: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Mock subtitle extraction."""
        self.call_count += 1
        if not self.should_succeed:
            return None

        return {
            'text': f"Subtitle text from {video_url}",
            'format': 'srt',
            'language': language or 'en',
            'confidence': 98.0,
        }


class TestContentFunnel:
    """Test suite for ContentFunnel."""

    def test_funnel_initialization(self):
        """Test basic funnel initialization."""
        funnel = ContentFunnel()
        assert funnel.audio_extractor is None
        assert funnel.audio_transcriber is None
        assert funnel.subtitle_extractor is None

    def test_funnel_with_extractors(self):
        """Test funnel initialization with extractors."""
        audio_extractor = MockAudioExtractor()
        audio_transcriber = MockAudioTranscriber()
        subtitle_extractor = MockSubtitleExtractor()

        funnel = ContentFunnel(
            audio_extractor=audio_extractor,
            audio_transcriber=audio_transcriber,
            subtitle_extractor=subtitle_extractor
        )

        assert funnel.audio_extractor is audio_extractor
        assert funnel.audio_transcriber is audio_transcriber
        assert funnel.subtitle_extractor is subtitle_extractor

    def test_text_passthrough(self):
        """Test that text content passes through unchanged."""
        funnel = ContentFunnel()

        text_idea = IdeaInspiration.from_text(
            title="Test Article",
            text_content="Original text content",
            keywords=["test", "article"]
        )

        result = funnel.process(text_idea)

        assert result.title == "Test Article"
        assert result.content == "Original text content"
        assert result.source_type == ContentType.TEXT
        # No transformations should occur
        assert 'transformation_chain' not in result.metadata

    def test_video_subtitle_extraction(self):
        """Test video content with subtitle extraction."""
        subtitle_extractor = MockSubtitleExtractor()
        funnel = ContentFunnel(subtitle_extractor=subtitle_extractor)

        video_idea = IdeaInspiration.from_video(
            title="Test Video",
            description="A test video",
            source_url="https://example.com/video123",
            source_id="video123"
        )

        result = funnel.process(video_idea, extract_subtitles=True)

        # Subtitle extraction should have been called
        assert subtitle_extractor.call_count == 1
        # Content should contain subtitle text
        assert "Subtitle text from" in result.content
        # Metadata should track the transformation
        assert 'transformation_chain' in result.metadata
        assert 'subtitle_format' in result.metadata
        assert result.metadata['subtitle_format'] == 'srt'
        assert result.metadata['subtitle_language'] == 'en'

    def test_video_audio_extraction_and_transcription(self):
        """Test video content with audio extraction and transcription."""
        audio_extractor = MockAudioExtractor()
        audio_transcriber = MockAudioTranscriber()
        funnel = ContentFunnel(
            audio_extractor=audio_extractor,
            audio_transcriber=audio_transcriber
        )

        video_idea = IdeaInspiration.from_video(
            title="Test Video",
            description="A test video",
            source_url="https://example.com/video123",
            source_id="video123"
        )

        result = funnel.process(
            video_idea,
            extract_audio=True,
            transcribe_audio=True,
            extract_subtitles=False  # Skip subtitle extraction
        )

        # Audio extraction should have been called
        assert audio_extractor.call_count == 1
        # Transcription should have been called
        assert audio_transcriber.call_count == 1
        # Content should contain transcribed text
        assert "Transcribed text from" in result.content
        # Metadata should track both transformations
        assert 'transformation_chain' in result.metadata
        assert 'audio_format' in result.metadata
        assert result.metadata['audio_format'] == 'mp3'
        assert 'transcription_language' in result.metadata

    def test_video_subtitle_preferred_over_transcription(self):
        """Test that subtitle extraction is preferred over audio transcription."""
        audio_extractor = MockAudioExtractor()
        audio_transcriber = MockAudioTranscriber()
        subtitle_extractor = MockSubtitleExtractor()

        funnel = ContentFunnel(
            audio_extractor=audio_extractor,
            audio_transcriber=audio_transcriber,
            subtitle_extractor=subtitle_extractor
        )

        video_idea = IdeaInspiration.from_video(
            title="Test Video",
            source_url="https://example.com/video123",
            source_id="video123"
        )

        result = funnel.process(
            video_idea,
            extract_audio=True,
            transcribe_audio=True,
            extract_subtitles=True
        )

        # Subtitle extraction should have been called
        assert subtitle_extractor.call_count == 1
        # Audio extraction should NOT have been called (subtitle took priority)
        assert audio_extractor.call_count == 0
        assert audio_transcriber.call_count == 0
        # Content should contain subtitle text
        assert "Subtitle text from" in result.content

    def test_video_fallback_to_transcription(self):
        """Test fallback to transcription when subtitle extraction fails."""
        audio_extractor = MockAudioExtractor()
        audio_transcriber = MockAudioTranscriber()
        subtitle_extractor = MockSubtitleExtractor(should_succeed=False)

        funnel = ContentFunnel(
            audio_extractor=audio_extractor,
            audio_transcriber=audio_transcriber,
            subtitle_extractor=subtitle_extractor
        )

        video_idea = IdeaInspiration.from_video(
            title="Test Video",
            source_url="https://example.com/video123",
            source_id="video123"
        )

        result = funnel.process(
            video_idea,
            extract_audio=True,
            transcribe_audio=True,
            extract_subtitles=True
        )

        # Both subtitle and audio extraction should have been attempted
        assert subtitle_extractor.call_count == 1
        assert audio_extractor.call_count == 1
        assert audio_transcriber.call_count == 1
        # Content should contain transcribed text (fallback)
        assert "Transcribed text from" in result.content

    def test_audio_transcription(self):
        """Test audio content transcription."""
        audio_transcriber = MockAudioTranscriber()
        funnel = ContentFunnel(audio_transcriber=audio_transcriber)

        audio_idea = IdeaInspiration.from_audio(
            title="Test Podcast",
            description="A test podcast episode",
            source_url="https://example.com/podcast.mp3",
            source_id="podcast123"
        )

        result = funnel.process(audio_idea, transcribe_audio=True)

        # Transcription should have been called
        assert audio_transcriber.call_count == 1
        # Content should contain transcribed text
        assert "Transcribed text from" in result.content
        # Metadata should track the transformation
        assert 'transformation_chain' in result.metadata
        assert 'transcription_language' in result.metadata

    def test_audio_without_transcription(self):
        """Test audio content without transcription enabled."""
        audio_transcriber = MockAudioTranscriber()
        funnel = ContentFunnel(audio_transcriber=audio_transcriber)

        audio_idea = IdeaInspiration.from_audio(
            title="Test Podcast",
            source_url="https://example.com/podcast.mp3"
        )

        result = funnel.process(audio_idea, transcribe_audio=False)

        # Transcription should NOT have been called
        assert audio_transcriber.call_count == 0
        # Content should remain empty
        assert result.content == ""
        # No transformation chain
        assert 'transformation_chain' not in result.metadata

    def test_video_with_existing_content(self):
        """Test that existing content is not overwritten."""
        subtitle_extractor = MockSubtitleExtractor()
        funnel = ContentFunnel(subtitle_extractor=subtitle_extractor)

        video_idea = IdeaInspiration.from_video(
            title="Test Video",
            subtitle_text="Existing subtitle content",
            source_url="https://example.com/video123"
        )

        result = funnel.process(video_idea, extract_subtitles=True)

        # Subtitle extraction should NOT have been called
        assert subtitle_extractor.call_count == 0
        # Existing content should be preserved
        assert result.content == "Existing subtitle content"

    def test_transformation_metadata(self):
        """Test transformation metadata tracking."""
        subtitle_extractor = MockSubtitleExtractor()
        funnel = ContentFunnel(subtitle_extractor=subtitle_extractor)

        video_idea = IdeaInspiration.from_video(
            title="Test Video",
            source_url="https://example.com/video123"
        )

        result = funnel.process(video_idea, extract_subtitles=True)

        # Check transformation history
        history = funnel.get_transformation_history()
        assert len(history) == 1
        assert history[0]['from_stage'] == 'video_source'
        assert history[0]['to_stage'] == 'text_subtitled'
        assert history[0]['method'] == 'subtitle_extraction'
        assert history[0]['confidence'] == 98.0

    def test_transformation_chain_format(self):
        """Test transformation chain string formatting."""
        audio_extractor = MockAudioExtractor()
        audio_transcriber = MockAudioTranscriber(confidence=92.5)
        funnel = ContentFunnel(
            audio_extractor=audio_extractor,
            audio_transcriber=audio_transcriber
        )

        video_idea = IdeaInspiration.from_video(
            title="Test Video",
            source_url="https://example.com/video123"
        )

        result = funnel.process(
            video_idea,
            extract_audio=True,
            transcribe_audio=True,
            extract_subtitles=False
        )

        # Check transformation chain format
        chain = result.metadata['transformation_chain']
        assert 'video_source→audio_extracted' in chain
        assert 'audio_extracted→text_transcribed' in chain
        assert '[92.5%]' in chain

    def test_language_parameter(self):
        """Test language parameter passing through the funnel."""
        audio_transcriber = MockAudioTranscriber()
        funnel = ContentFunnel(audio_transcriber=audio_transcriber)

        audio_idea = IdeaInspiration.from_audio(
            title="Test Podcast",
            source_url="https://example.com/podcast.mp3"
        )

        result = funnel.process(audio_idea, transcribe_audio=True, language='es')

        # Language should be stored in metadata
        assert result.metadata['transcription_language'] == 'es'

    def test_error_handling_audio_extraction_failure(self):
        """Test graceful error handling when audio extraction fails."""
        audio_extractor = MockAudioExtractor(should_succeed=False)
        audio_transcriber = MockAudioTranscriber()
        funnel = ContentFunnel(
            audio_extractor=audio_extractor,
            audio_transcriber=audio_transcriber
        )

        video_idea = IdeaInspiration.from_video(
            title="Test Video",
            source_url="https://example.com/video123"
        )

        # Should not raise an exception
        result = funnel.process(
            video_idea,
            extract_audio=True,
            transcribe_audio=True,
            extract_subtitles=False
        )

        # Content should remain empty
        assert result.content == ""
        # Transcription should not have been attempted
        assert audio_transcriber.call_count == 0

    def test_error_handling_transcription_failure(self):
        """Test graceful error handling when transcription fails."""
        audio_extractor = MockAudioExtractor()
        audio_transcriber = MockAudioTranscriber(should_succeed=False)
        funnel = ContentFunnel(
            audio_extractor=audio_extractor,
            audio_transcriber=audio_transcriber
        )

        video_idea = IdeaInspiration.from_video(
            title="Test Video",
            source_url="https://example.com/video123"
        )

        # Should not raise an exception
        result = funnel.process(
            video_idea,
            extract_audio=True,
            transcribe_audio=True,
            extract_subtitles=False
        )

        # Audio extraction should have occurred
        assert audio_extractor.call_count == 1
        # But content should remain empty since transcription failed
        assert result.content == ""


class TestTransformationMetadata:
    """Test suite for TransformationMetadata."""

    def test_transformation_metadata_creation(self):
        """Test creating transformation metadata."""
        metadata = TransformationMetadata(
            from_stage=TransformationStage.VIDEO_SOURCE,
            to_stage=TransformationStage.AUDIO_EXTRACTED,
            method="ffmpeg",
            confidence=95.0,
            timestamp="2024-01-01T12:00:00Z"
        )

        assert metadata.from_stage == TransformationStage.VIDEO_SOURCE
        assert metadata.to_stage == TransformationStage.AUDIO_EXTRACTED
        assert metadata.method == "ffmpeg"
        assert metadata.confidence == 95.0
        assert metadata.timestamp == "2024-01-01T12:00:00Z"

    def test_transformation_metadata_to_dict(self):
        """Test converting transformation metadata to dictionary."""
        metadata = TransformationMetadata(
            from_stage=TransformationStage.AUDIO_SOURCE,
            to_stage=TransformationStage.TEXT_TRANSCRIBED,
            method="whisper",
            confidence=92.5,
            additional_info={'model': 'large-v2'}
        )

        data = metadata.to_dict()

        assert data['from_stage'] == 'audio_source'
        assert data['to_stage'] == 'text_transcribed'
        assert data['method'] == 'whisper'
        assert data['confidence'] == 92.5
        assert data['additional_info']['model'] == 'large-v2'


class TestTransformationStage:
    """Test suite for TransformationStage enum."""

    def test_transformation_stages(self):
        """Test all transformation stages are defined."""
        assert TransformationStage.VIDEO_SOURCE.value == "video_source"
        assert TransformationStage.AUDIO_EXTRACTED.value == "audio_extracted"
        assert TransformationStage.AUDIO_SOURCE.value == "audio_source"
        assert TransformationStage.TEXT_TRANSCRIBED.value == "text_transcribed"
        assert TransformationStage.TEXT_SUBTITLED.value == "text_subtitled"
        assert TransformationStage.TEXT_SOURCE.value == "text_source"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
