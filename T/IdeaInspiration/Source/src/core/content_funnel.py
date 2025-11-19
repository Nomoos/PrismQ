"""Content Funnel for transforming media through processing stages.

This module implements the IdeaInspiration funnel concept where content
flows through transformation stages:
    Video → Audio → Text
    Audio → Text
    Text (final form)

The funnel tracks the transformation chain and enriches IdeaInspiration
objects with derived content at each stage.

This follows the Single Responsibility Principle by focusing solely on
content transformation orchestration.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any, Protocol, List
from dataclasses import dataclass
from enum import Enum

# Add Model path to sys.path to import IdeaInspiration
model_path = Path(__file__).parent.parent.parent.parent / "Model" / "src"
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration import IdeaInspiration, ContentType  # noqa: E402


class TransformationStage(Enum):
    """Stages in the content funnel transformation pipeline."""

    VIDEO_SOURCE = "video_source"          # Original video content
    AUDIO_EXTRACTED = "audio_extracted"    # Audio extracted from video
    AUDIO_SOURCE = "audio_source"          # Original audio content
    TEXT_TRANSCRIBED = "text_transcribed"  # Text from audio transcription
    TEXT_SUBTITLED = "text_subtitled"      # Text from video subtitles/captions
    TEXT_SOURCE = "text_source"            # Original text content


@dataclass
class TransformationMetadata:
    """Metadata about a content transformation.

    Tracks information about how content was transformed from one form
    to another in the funnel.

    Attributes:
        from_stage: The starting stage of the transformation
        to_stage: The resulting stage after transformation
        method: The method/tool used for transformation
        confidence: Optional confidence score (0-100) for the transformation
        timestamp: ISO 8601 timestamp of when transformation occurred
        additional_info: Any additional metadata about the transformation
    """

    from_stage: TransformationStage
    to_stage: TransformationStage
    method: str
    confidence: Optional[float] = None
    timestamp: Optional[str] = None
    additional_info: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'from_stage': self.from_stage.value,
            'to_stage': self.to_stage.value,
            'method': self.method,
            'confidence': self.confidence,
            'timestamp': self.timestamp,
            'additional_info': self.additional_info or {}
        }


class AudioExtractor(Protocol):
    """Protocol for audio extraction from video content.

    Implementations should extract audio from video files or streams
    and return audio data that can be used for transcription.
    """

    def extract_audio(
        self,
        video_url: str,
        video_id: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Extract audio from video.

        Args:
            video_url: URL or path to video content
            video_id: Optional video identifier
            **kwargs: Additional extraction parameters

        Returns:
            Dictionary containing audio data or None if extraction failed
            Expected keys: 'audio_url', 'audio_format', 'duration', etc.
        """
        ...


class AudioTranscriber(Protocol):
    """Protocol for transcribing audio content to text.

    Implementations should transcribe audio and return text transcription
    with optional timing information and confidence scores.
    """

    def transcribe_audio(
        self,
        audio_url: str,
        audio_id: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Transcribe audio to text.

        Args:
            audio_url: URL or path to audio content
            audio_id: Optional audio identifier
            language: Optional language code for transcription
            **kwargs: Additional transcription parameters

        Returns:
            Dictionary containing transcription data or None if failed
            Expected keys: 'text', 'confidence', 'language', 'timestamps', etc.
        """
        ...


class SubtitleExtractor(Protocol):
    """Protocol for extracting subtitles/captions from video content.

    Implementations should extract subtitles or captions from videos
    and return formatted text content.
    """

    def extract_subtitles(
        self,
        video_url: str,
        video_id: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Extract subtitles from video.

        Args:
            video_url: URL or path to video content
            video_id: Optional video identifier
            language: Optional language code for subtitles
            **kwargs: Additional extraction parameters

        Returns:
            Dictionary containing subtitle data or None if failed
            Expected keys: 'text', 'format', 'language', 'timestamps', etc.
        """
        ...


class ContentFunnel:
    """Orchestrates content transformation through the funnel pipeline.

    The ContentFunnel manages the transformation of content from one form
    to another, following the pattern:
        Video → Audio → Text (with subtitle extraction as alternative)
        Audio → Text
        Text (passthrough)

    It tracks transformation history and enriches IdeaInspiration objects
    with derived content at each stage.

    Example:
        >>> funnel = ContentFunnel(
        ...     audio_extractor=my_audio_extractor,
        ...     audio_transcriber=my_transcriber,
        ...     subtitle_extractor=my_subtitle_extractor
        ... )
        >>> video_idea = IdeaInspiration.from_video(
        ...     title="Python Tutorial",
        ...     source_url="https://youtube.com/watch?v=abc123"
        ... )
        >>> enriched_idea = funnel.process(video_idea)
        >>> # enriched_idea.content now contains transcribed text

    Attributes:
        audio_extractor: Optional audio extraction implementation
        audio_transcriber: Optional audio transcription implementation
        subtitle_extractor: Optional subtitle extraction implementation
    """

    def __init__(
        self,
        audio_extractor: Optional[AudioExtractor] = None,
        audio_transcriber: Optional[AudioTranscriber] = None,
        subtitle_extractor: Optional[SubtitleExtractor] = None
    ):
        """Initialize ContentFunnel with optional extractors/transcribers.

        Args:
            audio_extractor: Implementation for extracting audio from video
            audio_transcriber: Implementation for transcribing audio to text
            subtitle_extractor: Implementation for extracting subtitles
        """
        self.audio_extractor = audio_extractor
        self.audio_transcriber = audio_transcriber
        self.subtitle_extractor = subtitle_extractor
        self._transformation_history: List[TransformationMetadata] = []

    def process(
        self,
        idea: IdeaInspiration,
        extract_audio: bool = False,
        transcribe_audio: bool = False,
        extract_subtitles: bool = True,
        language: Optional[str] = None
    ) -> IdeaInspiration:
        """Process an IdeaInspiration through the content funnel.

        Depending on the source_type and available extractors/transcribers,
        this method will enrich the IdeaInspiration with derived content.

        Processing logic:
        - VIDEO: Try subtitle extraction first (faster), fallback to audio
                 transcription if requested and subtitles unavailable
        - AUDIO: Transcribe to text if transcriber available
        - TEXT: Return as-is (already at final stage)

        Args:
            idea: IdeaInspiration instance to process
            extract_audio: Whether to extract audio from video (default: False)
            transcribe_audio: Whether to transcribe audio to text (default: False)
            extract_subtitles: Whether to extract subtitles from video (default: True)
            language: Optional language code for transcription/subtitles

        Returns:
            Enriched IdeaInspiration with derived content

        Raises:
            ValueError: If required extractors/transcribers are not configured
        """
        self._transformation_history.clear()

        if idea.source_type == ContentType.VIDEO:
            return self._process_video(
                idea,
                extract_audio=extract_audio,
                transcribe_audio=transcribe_audio,
                extract_subtitles=extract_subtitles,
                language=language
            )
        elif idea.source_type == ContentType.AUDIO:
            return self._process_audio(
                idea,
                transcribe_audio=transcribe_audio,
                language=language
            )
        else:  # TEXT or UNKNOWN
            # Text is already at the final stage
            return idea

    def _process_video(
        self,
        idea: IdeaInspiration,
        extract_audio: bool,
        transcribe_audio: bool,
        extract_subtitles: bool,
        language: Optional[str]
    ) -> IdeaInspiration:
        """Process video content through the funnel.

        Priority order:
        1. Extract subtitles (if extract_subtitles=True and extractor available)
        2. Extract audio and transcribe (if requested and available)

        Args:
            idea: Video IdeaInspiration
            extract_audio: Whether to extract audio
            transcribe_audio: Whether to transcribe audio
            extract_subtitles: Whether to extract subtitles
            language: Optional language code

        Returns:
            Enriched IdeaInspiration with text content
        """
        # Try subtitle extraction first (faster and more accurate)
        if extract_subtitles and self.subtitle_extractor and not idea.content:
            subtitle_data = self._extract_subtitles_from_video(idea, language)
            if subtitle_data and subtitle_data.get('text'):
                idea.content = subtitle_data['text']
                self._record_transformation(
                    TransformationStage.VIDEO_SOURCE,
                    TransformationStage.TEXT_SUBTITLED,
                    "subtitle_extraction",
                    confidence=subtitle_data.get('confidence')
                )
                # Store subtitle metadata
                if 'format' in subtitle_data:
                    idea.metadata['subtitle_format'] = subtitle_data['format']
                if 'language' in subtitle_data:
                    idea.metadata['subtitle_language'] = subtitle_data['language']

        # Fallback to audio extraction and transcription if needed
        if not idea.content and transcribe_audio:
            if extract_audio and self.audio_extractor:
                audio_data = self._extract_audio_from_video(idea)
                if audio_data:
                    self._record_transformation(
                        TransformationStage.VIDEO_SOURCE,
                        TransformationStage.AUDIO_EXTRACTED,
                        "audio_extraction"
                    )
                    # Store audio metadata
                    if 'audio_format' in audio_data:
                        idea.metadata['audio_format'] = audio_data['audio_format']
                    if 'duration' in audio_data:
                        idea.metadata['audio_duration'] = str(audio_data['duration'])

                    # Now transcribe the extracted audio
                    if self.audio_transcriber and audio_data.get('audio_url'):
                        transcription_data = self._transcribe_audio(
                            audio_data['audio_url'],
                            idea.source_id,
                            language
                        )
                        if transcription_data and transcription_data.get('text'):
                            idea.content = transcription_data['text']
                            self._record_transformation(
                                TransformationStage.AUDIO_EXTRACTED,
                                TransformationStage.TEXT_TRANSCRIBED,
                                "audio_transcription",
                                confidence=transcription_data.get('confidence')
                            )
                            # Store transcription metadata
                            if 'language' in transcription_data:
                                lang = transcription_data['language']
                                idea.metadata['transcription_language'] = lang

        # Store transformation history in metadata
        if self._transformation_history:
            idea.metadata['transformation_chain'] = self._format_transformation_chain()

        return idea

    def _process_audio(
        self,
        idea: IdeaInspiration,
        transcribe_audio: bool,
        language: Optional[str]
    ) -> IdeaInspiration:
        """Process audio content through the funnel.

        Transcribes audio to text if transcriber is available and requested.

        Args:
            idea: Audio IdeaInspiration
            transcribe_audio: Whether to transcribe audio
            language: Optional language code

        Returns:
            Enriched IdeaInspiration with transcribed text
        """
        if transcribe_audio and self.audio_transcriber and not idea.content:
            if idea.source_url:
                transcription_data = self._transcribe_audio(
                    idea.source_url,
                    idea.source_id,
                    language
                )
                if transcription_data and transcription_data.get('text'):
                    idea.content = transcription_data['text']
                    self._record_transformation(
                        TransformationStage.AUDIO_SOURCE,
                        TransformationStage.TEXT_TRANSCRIBED,
                        "audio_transcription",
                        confidence=transcription_data.get('confidence')
                    )
                    # Store transcription metadata
                    if 'language' in transcription_data:
                        idea.metadata['transcription_language'] = transcription_data['language']

        # Store transformation history in metadata
        if self._transformation_history:
            idea.metadata['transformation_chain'] = self._format_transformation_chain()

        return idea

    def _extract_audio_from_video(
        self,
        idea: IdeaInspiration
    ) -> Optional[Dict[str, Any]]:
        """Extract audio from video content.

        Args:
            idea: Video IdeaInspiration

        Returns:
            Audio data dictionary or None if extraction failed
        """
        if not self.audio_extractor or not idea.source_url:
            return None

        try:
            return self.audio_extractor.extract_audio(
                video_url=idea.source_url,
                video_id=idea.source_id
            )
        except Exception as e:
            # Log error but don't raise - allow processing to continue
            print(f"Audio extraction failed: {e}")
            return None

    def _transcribe_audio(
        self,
        audio_url: str,
        audio_id: Optional[str],
        language: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Transcribe audio to text.

        Args:
            audio_url: URL or path to audio
            audio_id: Optional audio identifier
            language: Optional language code

        Returns:
            Transcription data dictionary or None if failed
        """
        if not self.audio_transcriber:
            return None

        try:
            return self.audio_transcriber.transcribe_audio(
                audio_url=audio_url,
                audio_id=audio_id,
                language=language
            )
        except Exception as e:
            # Log error but don't raise - allow processing to continue
            print(f"Audio transcription failed: {e}")
            return None

    def _extract_subtitles_from_video(
        self,
        idea: IdeaInspiration,
        language: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Extract subtitles from video content.

        Args:
            idea: Video IdeaInspiration
            language: Optional language code

        Returns:
            Subtitle data dictionary or None if extraction failed
        """
        if not self.subtitle_extractor or not idea.source_url:
            return None

        try:
            return self.subtitle_extractor.extract_subtitles(
                video_url=idea.source_url,
                video_id=idea.source_id,
                language=language
            )
        except Exception as e:
            # Log error but don't raise - allow processing to continue
            print(f"Subtitle extraction failed: {e}")
            return None

    def _record_transformation(
        self,
        from_stage: TransformationStage,
        to_stage: TransformationStage,
        method: str,
        confidence: Optional[float] = None
    ) -> None:
        """Record a transformation in the history.

        Args:
            from_stage: Starting stage
            to_stage: Resulting stage
            method: Method used for transformation
            confidence: Optional confidence score
        """
        from datetime import datetime, timezone

        metadata = TransformationMetadata(
            from_stage=from_stage,
            to_stage=to_stage,
            method=method,
            confidence=confidence,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        self._transformation_history.append(metadata)

    def _format_transformation_chain(self) -> str:
        """Format transformation history as a string for metadata storage.

        Returns:
            String representation of transformation chain
        """
        if not self._transformation_history:
            return ""

        chain_parts = []
        for trans in self._transformation_history:
            part = f"{trans.from_stage.value}→{trans.to_stage.value}({trans.method})"
            if trans.confidence:
                part += f"[{trans.confidence:.1f}%]"
            chain_parts.append(part)

        return " → ".join(chain_parts)

    def get_transformation_history(self) -> List[Dict[str, Any]]:
        """Get the transformation history for the last processed item.

        Returns:
            List of transformation metadata dictionaries
        """
        return [trans.to_dict() for trans in self._transformation_history]
