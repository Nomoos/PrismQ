"""Example usage of the ContentFunnel for processing IdeaInspiration content.

This example demonstrates how to use the ContentFunnel to transform
content from Video → Audio → Text or Audio → Text.

Run this example:
    python Source/_meta/examples/content_funnel_example.py
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Add paths for imports
source_path = Path(__file__).parent.parent.parent / "src"
model_path = Path(__file__).parent.parent.parent.parent / "Model" / "src"
if str(source_path) not in sys.path:
    sys.path.insert(0, str(source_path))
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from core.content_funnel import (  # noqa: E402
    ContentFunnel,
    AudioExtractor,  # Protocol, used for type hints in docstrings
    AudioTranscriber,  # Protocol, used for type hints in docstrings
    SubtitleExtractor  # Protocol, used for type hints in docstrings
)
from idea_inspiration import IdeaInspiration, ContentType  # noqa: E402, F401


# Example implementation of extractors/transcribers
# In real usage, these would use actual tools like ffmpeg, Whisper, youtube-dl, etc.


class ExampleAudioExtractor:
    """Example audio extractor (would use ffmpeg in production)."""

    def extract_audio(
        self,
        video_url: str,
        video_id: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Extract audio from video."""
        print(f"  [AudioExtractor] Extracting audio from: {video_url}")

        # In production, this would use ffmpeg:
        # ffmpeg -i {video_url} -vn -acodec mp3 {output_path}

        return {
            'audio_url': f"/tmp/{video_id or 'audio'}.mp3",
            'audio_format': 'mp3',
            'duration': 180,
        }


class ExampleAudioTranscriber:
    """Example audio transcriber (would use Whisper in production)."""

    def transcribe_audio(
        self,
        audio_url: str,
        audio_id: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Transcribe audio to text."""
        print(f"  [AudioTranscriber] Transcribing: {audio_url}")

        # In production, this would use Whisper:
        # import whisper
        # model = whisper.load_model("base")
        # result = model.transcribe(audio_url, language=language)

        return {
            'text': f"[Transcribed content from {audio_url}]\n\n"
                   "This is an example transcription. In production, this would contain "
                   "the actual transcribed text from the audio using a tool like OpenAI Whisper.",
            'confidence': 92.5,
            'language': language or 'en',
        }


class ExampleSubtitleExtractor:
    """Example subtitle extractor (would use youtube-dl in production)."""

    def extract_subtitles(
        self,
        video_url: str,
        video_id: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Extract subtitles from video."""
        print(f"  [SubtitleExtractor] Extracting subtitles from: {video_url}")

        # In production, this would use youtube-dl or similar:
        # youtube_dl.extract_info(video_url, {'writesubtitles': True})

        return {
            'text': f"[Subtitle content from {video_url}]\n\n"
                   "This is an example subtitle text. In production, this would contain "
                   "the actual subtitle/caption text extracted from the video.",
            'format': 'srt',
            'language': language or 'en',
            'confidence': 98.0,
        }


def example_video_with_subtitles():
    """Example 1: Process video content with subtitle extraction."""
    print("\n" + "="*80)
    print("Example 1: Video → Text (via Subtitles)")
    print("="*80)

    # Create a video IdeaInspiration
    video_idea = IdeaInspiration.from_video(
        title="Python Machine Learning Tutorial",
        description="Learn how to build ML models with Python",
        source_url="https://youtube.com/watch?v=abc123",
        source_id="abc123",
        source_platform="youtube",
        keywords=["python", "machine learning", "tutorial"]
    )

    print(f"\nOriginal Video Idea:")
    print(f"  Title: {video_idea.title}")
    print(f"  Source: {video_idea.source_url}")
    print(f"  Content: {video_idea.content or '(empty)'}")
    print(f"  Source Type: {video_idea.source_type.value}")

    # Create funnel with subtitle extractor
    funnel = ContentFunnel(subtitle_extractor=ExampleSubtitleExtractor())

    print(f"\nProcessing through funnel...")
    enriched = funnel.process(video_idea, extract_subtitles=True)

    print(f"\nEnriched Video Idea:")
    print(f"  Title: {enriched.title}")
    print(f"  Content: {enriched.content[:100]}...")
    print(f"  Transformation Chain: {enriched.metadata.get('transformation_chain', 'N/A')}")
    print(f"  Subtitle Format: {enriched.metadata.get('subtitle_format', 'N/A')}")
    print(f"  Subtitle Language: {enriched.metadata.get('subtitle_language', 'N/A')}")


def example_video_with_audio_transcription():
    """Example 2: Process video content with audio extraction and transcription."""
    print("\n" + "="*80)
    print("Example 2: Video → Audio → Text (via Transcription)")
    print("="*80)

    # Create a video IdeaInspiration
    video_idea = IdeaInspiration.from_video(
        title="Podcast Interview",
        description="Interview with a tech entrepreneur",
        source_url="https://example.com/interview.mp4",
        source_id="interview123",
        source_platform="custom"
    )

    print(f"\nOriginal Video Idea:")
    print(f"  Title: {video_idea.title}")
    print(f"  Source: {video_idea.source_url}")
    print(f"  Content: {video_idea.content or '(empty)'}")

    # Create funnel with audio extractor and transcriber
    funnel = ContentFunnel(
        audio_extractor=ExampleAudioExtractor(),
        audio_transcriber=ExampleAudioTranscriber()
    )

    print(f"\nProcessing through funnel...")
    enriched = funnel.process(
        video_idea,
        extract_audio=True,
        transcribe_audio=True,
        extract_subtitles=False  # No subtitle extraction
    )

    print(f"\nEnriched Video Idea:")
    print(f"  Title: {enriched.title}")
    print(f"  Content: {enriched.content[:100]}...")
    print(f"  Transformation Chain: {enriched.metadata.get('transformation_chain', 'N/A')}")
    print(f"  Audio Format: {enriched.metadata.get('audio_format', 'N/A')}")
    print(f"  Transcription Language: {enriched.metadata.get('transcription_language', 'N/A')}")

    # Get detailed transformation history
    print(f"\nTransformation History:")
    for trans in funnel.get_transformation_history():
        print(f"  {trans['from_stage']} → {trans['to_stage']}")
        print(f"    Method: {trans['method']}")
        if trans['confidence']:
            print(f"    Confidence: {trans['confidence']}%")


def example_audio_transcription():
    """Example 3: Process audio content with transcription."""
    print("\n" + "="*80)
    print("Example 3: Audio → Text (via Transcription)")
    print("="*80)

    # Create an audio IdeaInspiration
    audio_idea = IdeaInspiration.from_audio(
        title="Daily Tech News Podcast",
        description="Latest news from the tech world",
        source_url="https://example.com/podcast.mp3",
        source_id="podcast456",
        source_platform="spotify",
        keywords=["tech", "news", "podcast"]
    )

    print(f"\nOriginal Audio Idea:")
    print(f"  Title: {audio_idea.title}")
    print(f"  Source: {audio_idea.source_url}")
    print(f"  Content: {audio_idea.content or '(empty)'}")
    print(f"  Source Type: {audio_idea.source_type.value}")

    # Create funnel with transcriber
    funnel = ContentFunnel(audio_transcriber=ExampleAudioTranscriber())

    print(f"\nProcessing through funnel...")
    enriched = funnel.process(audio_idea, transcribe_audio=True, language='en')

    print(f"\nEnriched Audio Idea:")
    print(f"  Title: {enriched.title}")
    print(f"  Content: {enriched.content[:100]}...")
    print(f"  Transformation Chain: {enriched.metadata.get('transformation_chain', 'N/A')}")
    print(f"  Transcription Language: {enriched.metadata.get('transcription_language', 'N/A')}")


def example_text_passthrough():
    """Example 4: Process text content (passthrough)."""
    print("\n" + "="*80)
    print("Example 4: Text Content (Passthrough)")
    print("="*80)

    # Create a text IdeaInspiration
    text_idea = IdeaInspiration.from_text(
        title="Best Python Libraries for 2024",
        description="Comprehensive guide to Python libraries",
        text_content="Python continues to be one of the most popular programming languages...",
        keywords=["python", "libraries", "guide"]
    )

    print(f"\nOriginal Text Idea:")
    print(f"  Title: {text_idea.title}")
    print(f"  Content: {text_idea.content[:50]}...")
    print(f"  Source Type: {text_idea.source_type.value}")

    # Create funnel
    funnel = ContentFunnel()

    print(f"\nProcessing through funnel...")
    enriched = funnel.process(text_idea)

    print(f"\nEnriched Text Idea:")
    print(f"  Title: {enriched.title}")
    print(f"  Content: {enriched.content[:50]}...")
    print(f"  Transformation Chain: {enriched.metadata.get('transformation_chain', '(none - text is final form)')}")
    print(f"\n  Note: Text content passes through unchanged - it's already at the final stage.")


def example_video_with_fallback():
    """Example 5: Video with subtitle extraction fallback to transcription."""
    print("\n" + "="*80)
    print("Example 5: Video with Fallback (Subtitles → Transcription)")
    print("="*80)

    # Create a video IdeaInspiration
    video_idea = IdeaInspiration.from_video(
        title="Conference Talk",
        description="Keynote presentation",
        source_url="https://example.com/talk.mp4",
        source_id="talk789"
    )

    print(f"\nOriginal Video Idea:")
    print(f"  Title: {video_idea.title}")
    print(f"  Source: {video_idea.source_url}")

    # Create funnel with all extractors
    funnel = ContentFunnel(
        audio_extractor=ExampleAudioExtractor(),
        audio_transcriber=ExampleAudioTranscriber(),
        subtitle_extractor=ExampleSubtitleExtractor()
    )

    print(f"\nProcessing through funnel (trying subtitles first)...")
    enriched = funnel.process(
        video_idea,
        extract_audio=True,
        transcribe_audio=True,
        extract_subtitles=True  # Will try subtitles first
    )

    print(f"\nEnriched Video Idea:")
    print(f"  Title: {enriched.title}")
    print(f"  Content: {enriched.content[:100]}...")
    print(f"  Transformation Chain: {enriched.metadata.get('transformation_chain', 'N/A')}")
    print(f"\n  Note: Subtitle extraction was prioritized (faster and more accurate).")


def main():
    """Run all examples."""
    print("\n" + "#"*80)
    print("# ContentFunnel Usage Examples")
    print("# Demonstrating Video → Audio → Text transformation pipeline")
    print("#"*80)

    example_video_with_subtitles()
    example_video_with_audio_transcription()
    example_audio_transcription()
    example_text_passthrough()
    example_video_with_fallback()

    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80)
    print("\nKey Takeaways:")
    print("  1. ContentFunnel provides a unified interface for content transformation")
    print("  2. Video content can be processed via subtitles or audio transcription")
    print("  3. Audio content can be transcribed to text")
    print("  4. Text content passes through unchanged (already final form)")
    print("  5. Transformation chain is tracked in metadata for transparency")
    print("  6. Subtitle extraction is prioritized over transcription (faster)")
    print("\nFor production use:")
    print("  - Implement extractors using tools like ffmpeg, Whisper, youtube-dl")
    print("  - Add error handling and retry logic")
    print("  - Consider caching extracted/transcribed content")
    print("  - Monitor API costs for transcription services")
    print()


if __name__ == "__main__":
    main()
