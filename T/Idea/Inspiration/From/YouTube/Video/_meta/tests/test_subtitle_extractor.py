"""Unit tests for subtitle extraction functionality."""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.core.subtitle_extractor import SubtitleExtractor


class TestSubtitleExtractor:
    """Test suite for SubtitleExtractor."""

    def test_initialization_success(self):
        """Test successful initialization when yt-dlp is available."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            extractor = SubtitleExtractor()
            assert extractor is not None

    def test_initialization_failure(self):
        """Test initialization failure when yt-dlp is not available."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            with pytest.raises(ValueError, match="yt-dlp is not installed"):
                SubtitleExtractor()

    def test_parse_srt_to_text(self):
        """Test SRT parsing to plain text."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)
            extractor = SubtitleExtractor()

            srt_content = """1
00:00:00,000 --> 00:00:02,000
Hello world

2
00:00:02,000 --> 00:00:04,000
This is a test

3
00:00:04,000 --> 00:00:06,000
Multiple lines
of subtitle text
"""

            result = extractor._parse_srt_to_text(srt_content)

            assert "Hello world" in result
            assert "This is a test" in result
            assert "Multiple lines" in result
            assert "of subtitle text" in result
            # Should not contain timestamps or numbers
            assert "-->" not in result
            assert "00:00:00" not in result

    def test_extract_subtitles_success(self):
        """Test successful subtitle extraction."""
        with patch("subprocess.run") as mock_run:
            # First call: check yt-dlp version
            # Second call: extract subtitles
            mock_run.side_effect = [
                Mock(returncode=0),  # yt-dlp --version check
                Mock(returncode=0, stderr="", stdout=""),  # subtitle extraction
            ]

            extractor = SubtitleExtractor()

            # Create a temporary directory with mock SRT file
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                srt_file = temp_path / "yt_test123.en.srt"
                srt_file.write_text(
                    """1
00:00:00,000 --> 00:00:02,000
Test subtitle content

2
00:00:02,000 --> 00:00:04,000
More subtitle text
"""
                )

                # Mock extract_subtitles to use our temp directory
                with patch("tempfile.TemporaryDirectory") as mock_tempdir:
                    mock_tempdir.return_value.__enter__.return_value = temp_dir

                    result = extractor.extract_subtitles("test123")

                    assert result is not None
                    assert "Test subtitle content" in result
                    assert "More subtitle text" in result

    def test_extract_subtitles_no_subtitles(self):
        """Test when video has no subtitles."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                Mock(returncode=0),  # yt-dlp --version check
                Mock(returncode=0, stderr="", stdout=""),  # subtitle extraction (no files created)
            ]

            extractor = SubtitleExtractor()

            # No SRT files will be created
            result = extractor.extract_subtitles("test_no_subs")

            assert result is None

    def test_extract_subtitles_ytdlp_failure(self):
        """Test when yt-dlp fails to download."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                Mock(returncode=0),  # yt-dlp --version check
                Mock(returncode=1, stderr="ERROR: Video not found", stdout=""),
            ]

            extractor = SubtitleExtractor()
            result = extractor.extract_subtitles("invalid_video")

            assert result is None

    def test_extract_subtitles_timeout(self):
        """Test when yt-dlp times out."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                Mock(returncode=0),  # yt-dlp --version check
                subprocess.TimeoutExpired("yt-dlp", 60),
            ]

            extractor = SubtitleExtractor()
            result = extractor.extract_subtitles("timeout_video")

            assert result is None

    def test_extract_subtitles_exception(self):
        """Test when an unexpected exception occurs."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                Mock(returncode=0),  # yt-dlp --version check
                Exception("Unexpected error"),
            ]

            extractor = SubtitleExtractor()
            result = extractor.extract_subtitles("error_video")

            assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
