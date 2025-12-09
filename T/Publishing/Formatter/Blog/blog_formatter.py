"""Blog Format Optimizer for PrismQ.T.Script.Formatter.Blog.

This module transforms scripts into blog-optimized format with proper heading
hierarchy, sections, and formatting suitable for platforms like Medium,
WordPress, Ghost, and others.

Workflow Position:
    Post-MVP Enhancement (POST-003): Blog Format Optimization
    Published Script → Blog Formatter → Platform-Ready Blog Content
"""

import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class BlogMetadata:
    """Metadata for a blog post.

    Attributes:
        excerpt: Short excerpt (150-200 chars)
        reading_time: Estimated reading time (e.g., "5 min read")
        word_count: Total word count
        char_count: Total character count
        paragraph_count: Number of paragraphs
        heading_count: Number of headings
        featured_image_suggestions: Suggested featured image placements
    """

    excerpt: str = ""
    reading_time: str = ""
    word_count: int = 0
    char_count: int = 0
    paragraph_count: int = 0
    heading_count: int = 0
    featured_image_suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)


@dataclass
class BlogFormattedContent:
    """Result of blog formatting operation.

    Attributes:
        content_id: Identifier of the formatted content
        title: Blog post title
        formatted_content: Blog-formatted content (Markdown or HTML)
        metadata: Blog metadata
        format_type: Output format (markdown or html)
        platform: Target platform (generic, medium, wordpress, ghost)
        timestamp: When formatting was performed
        success: Whether formatting succeeded
        errors: List of any errors encountered
    """

    content_id: str
    title: str
    formatted_content: str
    metadata: BlogMetadata
    format_type: str = "markdown"
    platform: str = "generic"
    # Note: Lambda in default_factory is called at instance creation, not field definition
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    success: bool = True
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = asdict(self)
        data["metadata"] = self.metadata.to_dict()
        return data


class BlogFormatter:
    """Format scripts into blog-optimized content.

    Transforms narrative scripts into well-structured blog posts with:
    - Proper heading hierarchy (H1, H2, H3)
    - Readable paragraph breaks (3-4 sentences max)
    - Strategic CTA placement
    - Blog-specific metadata
    - Platform-specific optimizations
    """

    # Reading speed in words per minute (average)
    READING_SPEED_WPM = 225

    # Formatting rules
    MAX_SENTENCES_PER_PARAGRAPH = 4
    WORDS_BETWEEN_HEADINGS = 350  # Target words between H2 headings

    def __init__(self):
        """Initialize the blog formatter."""
        pass

    def format_blog(
        self,
        script: str,
        title: str,
        content_id: str,
        platform: str = "generic",
        format_type: str = "markdown",
        cta_text: Optional[str] = None,
    ) -> BlogFormattedContent:
        """Format script into blog-optimized content.

        Args:
            script: The script content to format
            title: Blog post title
            content_id: Unique identifier for the content
            platform: Target platform (generic, medium, wordpress, ghost)
            format_type: Output format (markdown or html)
            cta_text: Optional custom CTA text

        Returns:
            BlogFormattedContent with formatted blog and metadata
        """
        result = BlogFormattedContent(
            content_id=content_id,
            title=title,
            formatted_content="",
            metadata=BlogMetadata(),
            format_type=format_type,
            platform=platform,
        )

        try:
            # Step 1: Parse and structure the content
            sections = self._parse_content_into_sections(script)

            # Step 2: Format paragraphs for readability
            formatted_sections = self._format_paragraphs(sections)

            # Step 3: Add heading hierarchy
            structured_content = self._add_heading_hierarchy(formatted_sections, title)

            # Step 4: Add CTAs at strategic points
            if cta_text:
                structured_content = self._add_cta_sections(structured_content, cta_text)

            # Step 5: Generate metadata
            result.metadata = self._generate_metadata(structured_content, title)

            # Step 6: Apply platform-specific formatting
            if format_type == "markdown":
                result.formatted_content = self._format_as_markdown(structured_content, platform)
            elif format_type == "html":
                result.formatted_content = self._format_as_html(structured_content, platform)
            else:
                raise ValueError(f"Unknown format type: {format_type}")

        except Exception as e:
            result.errors.append(f"Formatting error: {str(e)}")
            result.success = False

        return result

    def _parse_content_into_sections(self, script: str) -> List[Dict[str, Any]]:
        """Parse script into logical sections.

        Args:
            script: Raw script content

        Returns:
            List of section dictionaries with content and metadata
        """
        # Split by double newlines to identify paragraphs
        paragraphs = [p.strip() for p in script.split("\n\n") if p.strip()]

        # Group paragraphs into sections (rough grouping by content length)
        sections = []
        current_section = []
        current_word_count = 0

        for para in paragraphs:
            words = len(para.split())

            # Start new section if we've accumulated enough content
            if current_word_count > self.WORDS_BETWEEN_HEADINGS and current_section:
                sections.append(
                    {
                        "type": "content",
                        "paragraphs": current_section,
                        "word_count": current_word_count,
                    }
                )
                current_section = []
                current_word_count = 0

            current_section.append(para)
            current_word_count += words

        # Add remaining content
        if current_section:
            sections.append(
                {"type": "content", "paragraphs": current_section, "word_count": current_word_count}
            )

        return sections

    def _format_paragraphs(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format paragraphs for readability.

        Ensures paragraphs have max 3-4 sentences for better readability.

        Args:
            sections: List of content sections

        Returns:
            Sections with formatted paragraphs
        """
        formatted_sections = []

        for section in sections:
            formatted_paragraphs = []

            for para in section["paragraphs"]:
                # Split into sentences
                sentences = self._split_into_sentences(para)

                # Group into readable paragraphs (max 4 sentences)
                for i in range(0, len(sentences), self.MAX_SENTENCES_PER_PARAGRAPH):
                    chunk = sentences[i : i + self.MAX_SENTENCES_PER_PARAGRAPH]
                    formatted_paragraphs.append(" ".join(chunk))

            formatted_sections.append(
                {
                    "type": section["type"],
                    "paragraphs": formatted_paragraphs,
                    "word_count": section["word_count"],
                }
            )

        return formatted_sections

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences.

        Uses basic regex for sentence splitting. Known limitations:
        - May split incorrectly on abbreviations (e.g., 'Dr.', 'Mr.', 'U.S.')
        - May not handle decimal numbers correctly (e.g., '3.14')
        - Does not handle ellipses as sentence boundaries

        For production use with complex content, consider using
        an NLP library like spaCy or NLTK for more robust sentence detection.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        # Simple sentence splitter (handles . ! ?)
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _add_heading_hierarchy(self, sections: List[Dict[str, Any]], title: str) -> Dict[str, Any]:
        """Add heading hierarchy to content.

        Creates H1 for title, H2 for main sections, H3 for subsections.

        Args:
            sections: Formatted content sections
            title: Blog post title

        Returns:
            Structured content with headings
        """
        structured = {"title": title, "sections": []}

        # Determine section headings based on content position
        section_headings = self._generate_section_headings(sections)

        for i, section in enumerate(sections):
            structured_section = {
                "heading": section_headings[i] if i < len(section_headings) else f"Section {i+1}",
                "heading_level": 2,  # H2 for main sections
                "paragraphs": section["paragraphs"],
            }
            structured["sections"].append(structured_section)

        return structured

    def _generate_section_headings(self, sections: List[Dict[str, Any]]) -> List[str]:
        """Generate appropriate headings for sections.

        Args:
            sections: Content sections

        Returns:
            List of heading strings
        """
        num_sections = len(sections)

        # Default section heading templates
        if num_sections <= 2:
            return ["Introduction", "Conclusion"]
        elif num_sections == 3:
            return ["Introduction", "Main Content", "Conclusion"]
        elif num_sections == 4:
            return ["Introduction", "Key Points", "Analysis", "Conclusion"]
        else:
            # For more sections, use generic numbering with some special ones
            headings = ["Introduction"]
            for i in range(1, num_sections - 1):
                headings.append(f"Section {i}")
            headings.append("Conclusion")
            return headings

    def _add_cta_sections(self, content: Dict[str, Any], cta_text: str) -> Dict[str, Any]:
        """Add Call-to-Action sections at strategic points.

        CTAs are placed:
        - After introduction (first section)
        - Mid-content
        - At the end

        Args:
            content: Structured content
            cta_text: CTA text to insert

        Returns:
            Content with CTA sections added
        """
        num_sections = len(content["sections"])

        # Determine CTA insertion points
        cta_positions = []

        if num_sections >= 2:
            # After introduction
            cta_positions.append(1)

        if num_sections >= 4:
            # Mid-content
            mid_point = num_sections // 2
            cta_positions.append(mid_point)

        # Always at the end
        cta_positions.append(num_sections)

        # Insert CTAs (in reverse order to maintain indices)
        for pos in reversed(sorted(set(cta_positions))):
            cta_section = {
                "heading": None,  # CTAs don't have headings
                "heading_level": 0,
                "paragraphs": [cta_text],
                "is_cta": True,
            }
            content["sections"].insert(pos, cta_section)

        return content

    def _generate_metadata(self, content: Dict[str, Any], title: str) -> BlogMetadata:
        """Generate blog metadata.

        Args:
            content: Structured content
            title: Blog post title

        Returns:
            BlogMetadata with calculated values
        """
        # Collect all text
        all_text = title + " "
        paragraph_count = 0

        for section in content["sections"]:
            for para in section["paragraphs"]:
                all_text += para + " "
                paragraph_count += 1

        # Calculate metrics
        word_count = len(all_text.split())
        char_count = len(all_text)
        reading_time = self._calculate_reading_time(word_count)
        excerpt = self._generate_excerpt(content)
        heading_count = sum(1 for s in content["sections"] if s.get("heading"))

        return BlogMetadata(
            excerpt=excerpt,
            reading_time=reading_time,
            word_count=word_count,
            char_count=char_count,
            paragraph_count=paragraph_count,
            heading_count=heading_count,
            featured_image_suggestions=["After title", "After introduction"],
        )

    def _calculate_reading_time(self, word_count: int) -> str:
        """Calculate reading time estimate.

        Args:
            word_count: Total word count

        Returns:
            Reading time string (e.g., "5 min read")
        """
        minutes = max(1, round(word_count / self.READING_SPEED_WPM))
        return f"{minutes} min read"

    def _generate_excerpt(self, content: Dict[str, Any]) -> str:
        """Generate excerpt from content.

        Args:
            content: Structured content

        Returns:
            Excerpt string (150-200 chars)
        """
        # Get first paragraph from first section
        if content["sections"] and content["sections"][0]["paragraphs"]:
            first_para = content["sections"][0]["paragraphs"][0]

            # Truncate to ~180 characters
            if len(first_para) > 180:
                excerpt = first_para[:177] + "..."
            else:
                excerpt = first_para

            return excerpt

        return ""

    def _format_as_markdown(self, content: Dict[str, Any], platform: str) -> str:
        """Format content as Markdown.

        Args:
            content: Structured content
            platform: Target platform

        Returns:
            Markdown-formatted string
        """
        lines = []

        # Title (H1)
        lines.append(f"# {content['title']}")
        lines.append("")

        # Platform-specific featured image placeholder
        if platform == "medium":
            lines.append("[Featured Image - Add via Medium editor]")
        else:
            lines.append("[Featured Image]")
        lines.append("")

        # Content sections
        for section in content["sections"]:
            # Add heading if present
            if section.get("heading"):
                heading_level = section.get("heading_level", 2)
                heading_marker = "#" * heading_level
                lines.append(f"{heading_marker} {section['heading']}")
                lines.append("")

            # Add paragraphs
            for para in section["paragraphs"]:
                lines.append(para)
                lines.append("")

            # CTA sections get a separator for Medium
            if section.get("is_cta") and platform == "medium":
                lines.append("---")
                lines.append("")

        return "\n".join(lines)

    def _format_as_html(self, content: Dict[str, Any], platform: str) -> str:
        """Format content as HTML.

        Args:
            content: Structured content
            platform: Target platform

        Returns:
            HTML-formatted string
        """
        import html as html_module

        lines = []

        # Title
        title_escaped = html_module.escape(content["title"])
        lines.append(f"<h1>{title_escaped}</h1>")
        lines.append("")

        # Featured image placeholder
        lines.append('<div class="featured-image">')
        lines.append("  <!-- Featured Image Here -->")
        lines.append("</div>")
        lines.append("")

        # Content sections
        for section in content["sections"]:
            # Add heading if present
            if section.get("heading"):
                heading_level = section.get("heading_level", 2)
                heading_escaped = html_module.escape(section["heading"])
                lines.append(f"<h{heading_level}>{heading_escaped}</h{heading_level}>")
                lines.append("")

            # Add paragraphs
            for para in section["paragraphs"]:
                para_escaped = html_module.escape(para)

                # CTA sections get special styling
                if section.get("is_cta"):
                    lines.append(f'<div class="cta">')
                    lines.append(f"  <p>{para_escaped}</p>")
                    lines.append("</div>")
                else:
                    lines.append(f"<p>{para_escaped}</p>")

                lines.append("")

        return "\n".join(lines)


def format_blog(
    script: str,
    title: str,
    content_id: str,
    platform: str = "generic",
    format_type: str = "markdown",
    cta_text: Optional[str] = None,
) -> BlogFormattedContent:
    """Convenience function to format blog content.

    Args:
        script: The script content to format
        title: Blog post title
        content_id: Unique identifier for the content
        platform: Target platform (generic, medium, wordpress, ghost)
        format_type: Output format (markdown or html)
        cta_text: Optional custom CTA text

    Returns:
        BlogFormattedContent with formatted blog and metadata

    Example:
        >>> result = format_blog(
        ...     script="This is a story about innovation...",
        ...     title="Innovation in Action",
        ...     content_id="story-001",
        ...     platform="medium",
        ...     format_type="markdown"
        ... )
        >>> print(result.metadata.reading_time)
        >>> print(result.formatted_content)
    """
    formatter = BlogFormatter()
    return formatter.format_blog(script, title, content_id, platform, format_type, cta_text)
