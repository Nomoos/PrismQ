"""Content Export module for PrismQ.T.Publishing.ContentExport.

This module provides functionality to export finalized content in multiple formats:
- JSON: Complete data structure for programmatic access
- Markdown: Human-readable documentation format
- HTML: Web-ready display format

Workflow Position:
    Stage 23 (MVP-023): Content Export
    Polished Content → Export to Formats → Stage 24 (Report Generation)
"""

import json
import html
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class ContentExportResult:
    """Result of content export operation.
    
    Attributes:
        content_id: Identifier of the exported content
        export_timestamp: When the export was performed
        formats_exported: List of formats successfully exported
        export_paths: Dictionary mapping format to file path
        success: Whether all exports succeeded
        errors: List of any errors encountered
    """
    
    content_id: str
    export_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    formats_exported: List[str] = field(default_factory=list)
    export_paths: Dict[str, str] = field(default_factory=dict)
    success: bool = True
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ContentExportResult(id={self.content_id}, "
            f"formats={len(self.formats_exported)}, "
            f"success={'YES' if self.success else 'NO'})"
        )


class ContentExporter:
    """Export content to multiple formats.
    
    Supports exporting text content to:
    - JSON: Complete structured data
    - Markdown: Documentation format
    - HTML: Web display format
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize the content exporter.
        
        Args:
            output_dir: Base directory for exports (default: current directory)
        """
        self.output_dir = output_dir or Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_content(
        self,
        content: Dict[str, Any],
        content_id: str,
        formats: Optional[List[str]] = None
    ) -> ContentExportResult:
        """Export content in specified formats.
        
        Args:
            content: Content dictionary with keys: id, title, script, metadata
            content_id: Unique identifier for the content
            formats: List of formats to export (default: all)
        
        Returns:
            ContentExportResult with export status and paths
        """
        if formats is None:
            formats = ["json", "markdown", "html"]
        
        result = ContentExportResult(content_id=content_id)
        
        for fmt in formats:
            try:
                if fmt == "json":
                    path = self._export_json(content, content_id)
                elif fmt == "markdown":
                    path = self._export_markdown(content, content_id)
                elif fmt == "html":
                    path = self._export_html(content, content_id)
                else:
                    result.errors.append(f"Unknown format: {fmt}")
                    result.success = False
                    continue
                
                result.formats_exported.append(fmt)
                result.export_paths[fmt] = str(path)
                
            except Exception as e:
                result.errors.append(f"Error exporting {fmt}: {str(e)}")
                result.success = False
        
        return result
    
    def _export_json(self, content: Dict[str, Any], content_id: str) -> Path:
        """Export content as JSON.
        
        Args:
            content: Content dictionary
            content_id: Content identifier
        
        Returns:
            Path to exported JSON file
        """
        output_path = self.output_dir / f"{content_id}.json"
        
        # Create a clean export structure
        export_data = {
            "id": content.get("id", content_id),
            "title": content.get("title", ""),
            "script": content.get("script", ""),
            "metadata": content.get("metadata", {}),
            "export_timestamp": datetime.now().isoformat(),
            "format": "json",
            "version": content.get("version", "1.0")
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def _export_markdown(self, content: Dict[str, Any], content_id: str) -> Path:
        """Export content as Markdown.
        
        Args:
            content: Content dictionary
            content_id: Content identifier
        
        Returns:
            Path to exported Markdown file
        """
        output_path = self.output_dir / f"{content_id}.md"
        
        title = content.get("title", "Untitled")
        script = content.get("script", "")
        metadata = content.get("metadata", {})
        
        # Build Markdown content
        md_lines = [
            f"# {title}",
            "",
            "## Metadata",
            ""
        ]
        
        # Add metadata
        for key, value in metadata.items():
            md_lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
        
        md_lines.extend([
            "",
            "## Content",
            "",
            script,
            "",
            "---",
            "",
            f"*Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(md_lines))
        
        return output_path
    
    def _export_html(self, content: Dict[str, Any], content_id: str) -> Path:
        """Export content as HTML.
        
        Args:
            content: Content dictionary
            content_id: Content identifier
        
        Returns:
            Path to exported HTML file
        """
        output_path = self.output_dir / f"{content_id}.html"
        
        title = html.escape(content.get("title", "Untitled"))
        script = html.escape(content.get("script", ""))
        metadata = content.get("metadata", {})
        
        # Build HTML content
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .metadata {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .metadata-item {{
            margin: 8px 0;
        }}
        .metadata-label {{
            font-weight: bold;
            color: #555;
        }}
        .content {{
            margin-top: 30px;
            white-space: pre-wrap;
            font-size: 1.1em;
            line-height: 1.8;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #777;
            font-size: 0.9em;
            text-align: center;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    
    <div class="metadata">
        <h2>Metadata</h2>
"""
        
        # Add metadata
        for key, value in metadata.items():
            label = key.replace('_', ' ').title()
            html_content += f'        <div class="metadata-item"><span class="metadata-label">{html.escape(label)}:</span> {html.escape(str(value))}</div>\n'
        
        html_content += f"""    </div>
    
    <div class="content">
{script}
    </div>
    
    <div class="footer">
        <p>Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>PrismQ Content Production Platform</p>
    </div>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def validate_export(self, export_result: ContentExportResult) -> bool:
        """Validate that exported files exist and are readable.
        
        Args:
            export_result: Result from export_content()
        
        Returns:
            True if all exported files are valid
        """
        for format_name, path_str in export_result.export_paths.items():
            path = Path(path_str)
            
            # Check file exists
            if not path.exists():
                export_result.errors.append(f"{format_name}: File not found at {path}")
                export_result.success = False
                continue
            
            # Check file is readable
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not content:
                        export_result.errors.append(f"{format_name}: File is empty")
                        export_result.success = False
            except Exception as e:
                export_result.errors.append(f"{format_name}: Read error - {str(e)}")
                export_result.success = False
        
        return export_result.success


def export_content(
    content: Dict[str, Any],
    content_id: str,
    output_dir: Optional[Path] = None,
    formats: Optional[List[str]] = None
) -> ContentExportResult:
    """Convenience function to export content.
    
    Args:
        content: Content dictionary with keys: id, title, script, metadata
        content_id: Unique identifier for the content
        output_dir: Output directory for exports
        formats: List of formats to export (default: all)
    
    Returns:
        ContentExportResult with export status and paths
    
    Example:
        >>> content = {
        ...     "id": "story-001",
        ...     "title": "My Story",
        ...     "script": "Once upon a time...",
        ...     "metadata": {"author": "John Doe", "date": "2025-11-22"}
        ... }
        >>> result = export_content(content, "story-001")
        >>> print(f"Exported {len(result.formats_exported)} formats")
        >>> print(f"Paths: {result.export_paths}")
    """
    exporter = ContentExporter(output_dir)
    result = exporter.export_content(content, content_id, formats)
    exporter.validate_export(result)
    return result
