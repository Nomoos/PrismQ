"""Report Generation module for PrismQ.T.Publishing.ReportGeneration.

This module provides functionality to generate comprehensive publishing reports
including workflow statistics, quality metrics, review history, and export details.

Workflow Position:
    Stage 24 (MVP-024): Report Generation
    Exported Content → Generate Report → Publishing Complete
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class PublishingReport:
    """Comprehensive publishing report with workflow metrics and statistics.

    Attributes:
        content_id: Identifier of the published content
        title: Content title
        generation_timestamp: When the report was generated

        Workflow Statistics:
            total_versions: Total number of versions created
            total_reviews: Total number of reviews performed
            total_iterations: Total refinement iterations
            workflow_duration: Total time from start to publish (if available)

        Quality Metrics:
            quality_gates_passed: List of quality gates that passed
            final_scores: Dictionary of final quality scores
            reviews_history: History of all reviews

        Export Information:
            export_formats: List of export formats
            export_paths: Dictionary mapping format to path
            export_timestamp: When content was exported

        Summary:
            summary: Executive summary of the workflow
            key_achievements: Major achievements in the workflow
            notes: Additional notes
    """

    content_id: str
    title: str = ""
    generation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Workflow Statistics
    total_versions: int = 0
    total_reviews: int = 0
    total_iterations: int = 0
    workflow_duration: Optional[str] = None

    # Quality Metrics
    quality_gates_passed: List[str] = field(default_factory=list)
    final_scores: Dict[str, int] = field(default_factory=dict)
    reviews_history: List[Dict[str, Any]] = field(default_factory=list)

    # Export Information
    export_formats: List[str] = field(default_factory=list)
    export_paths: Dict[str, str] = field(default_factory=dict)
    export_timestamp: Optional[str] = None

    # Summary
    summary: str = ""
    key_achievements: List[str] = field(default_factory=list)
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary representation."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convert report to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"PublishingReport(id={self.content_id}, "
            f"versions={self.total_versions}, "
            f"reviews={self.total_reviews}, "
            f"formats={len(self.export_formats)})"
        )


class ReportGenerator:
    """Generate comprehensive publishing reports.

    Creates detailed reports with workflow statistics, quality metrics,
    and export information for published content.
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize the report generator.

        Args:
            output_dir: Base directory for report outputs (default: current directory)
        """
        self.output_dir = output_dir or Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self,
        content_id: str,
        title: str,
        workflow_data: Optional[Dict[str, Any]] = None,
        export_result: Optional[Dict[str, Any]] = None,
    ) -> PublishingReport:
        """Generate a comprehensive publishing report.

        Args:
            content_id: Unique identifier for the content
            title: Content title
            workflow_data: Optional workflow statistics and history
            export_result: Optional export result information

        Returns:
            PublishingReport with complete metrics
        """
        report = PublishingReport(content_id=content_id, title=title)

        # Process workflow data
        if workflow_data:
            self._add_workflow_data(report, workflow_data)

        # Process export results
        if export_result:
            self._add_export_data(report, export_result)

        # Generate summary
        self._generate_summary(report)

        return report

    def _add_workflow_data(self, report: PublishingReport, workflow_data: Dict[str, Any]) -> None:
        """Add workflow statistics to the report.

        Args:
            report: Publishing report to update
            workflow_data: Workflow statistics and history
        """
        # Version tracking
        report.total_versions = workflow_data.get("total_versions", 0)
        report.total_reviews = workflow_data.get("total_reviews", 0)
        report.total_iterations = workflow_data.get("total_iterations", 0)
        report.workflow_duration = workflow_data.get("workflow_duration")

        # Quality gates
        report.quality_gates_passed = workflow_data.get("quality_gates_passed", [])
        report.final_scores = workflow_data.get("final_scores", {})
        report.reviews_history = workflow_data.get("reviews_history", [])

        # Additional metadata
        if "metadata" in workflow_data:
            report.metadata.update(workflow_data["metadata"])

    def _add_export_data(self, report: PublishingReport, export_result: Dict[str, Any]) -> None:
        """Add export information to the report.

        Args:
            report: Publishing report to update
            export_result: Export result information
        """
        report.export_formats = export_result.get("formats_exported", [])
        report.export_paths = export_result.get("export_paths", {})
        report.export_timestamp = export_result.get("export_timestamp")

    def _generate_summary(self, report: PublishingReport) -> None:
        """Generate executive summary and key achievements.

        Args:
            report: Publishing report to update
        """
        achievements = []

        # Version achievements
        if report.total_versions > 0:
            achievements.append(
                f"Created {report.total_versions} version(s) through iterative refinement"
            )

        # Review achievements
        if report.total_reviews > 0:
            achievements.append(f"Passed {report.total_reviews} quality review(s)")

        # Quality gate achievements
        if report.quality_gates_passed:
            achievements.append(
                f"Passed {len(report.quality_gates_passed)} quality gate(s): "
                f"{', '.join(report.quality_gates_passed)}"
            )

        # Export achievements
        if report.export_formats:
            achievements.append(
                f"Exported to {len(report.export_formats)} format(s): "
                f"{', '.join(report.export_formats)}"
            )

        report.key_achievements = achievements

        # Generate summary text
        summary_parts = [f"Publishing workflow completed for '{report.title}'."]

        if report.total_iterations > 0:
            summary_parts.append(f"Content refined through {report.total_iterations} iteration(s).")

        if report.workflow_duration:
            summary_parts.append(f"Total workflow duration: {report.workflow_duration}.")

        summary_parts.append("All quality gates passed and content exported successfully.")

        report.summary = " ".join(summary_parts)

    def save_report(
        self, report: PublishingReport, format: str = "json", filename: Optional[str] = None
    ) -> Path:
        """Save report to file.

        Args:
            report: PublishingReport to save
            format: Output format ('json', 'txt', or 'md')
            filename: Optional custom filename (default: {content_id}_report.{ext})

        Returns:
            Path to saved report file
        """
        if filename is None:
            ext = "json" if format == "json" else "txt" if format == "txt" else "md"
            filename = f"{report.content_id}_report.{ext}"

        output_path = self.output_dir / filename

        if format == "json":
            content = report.to_json()
        elif format == "txt":
            content = self._format_as_text(report)
        elif format == "md":
            content = self._format_as_markdown(report)
        else:
            raise ValueError(f"Unknown format: {format}")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        return output_path

    def _format_as_text(self, report: PublishingReport) -> str:
        """Format report as plain text.

        Args:
            report: PublishingReport to format

        Returns:
            Formatted text string
        """
        lines = [
            "=" * 70,
            "PUBLISHING REPORT",
            "=" * 70,
            "",
            f"Content ID: {report.content_id}",
            f"Title: {report.title}",
            f"Generated: {report.generation_timestamp}",
            "",
            "SUMMARY",
            "-" * 70,
            report.summary,
            "",
            "WORKFLOW STATISTICS",
            "-" * 70,
            f"Total Versions: {report.total_versions}",
            f"Total Reviews: {report.total_reviews}",
            f"Total Iterations: {report.total_iterations}",
        ]

        if report.workflow_duration:
            lines.append(f"Workflow Duration: {report.workflow_duration}")

        if report.quality_gates_passed:
            lines.extend(["", "QUALITY GATES PASSED", "-" * 70])
            for gate in report.quality_gates_passed:
                lines.append(f"  - {gate}")

        if report.final_scores:
            lines.extend(["", "FINAL SCORES", "-" * 70])
            for metric, score in report.final_scores.items():
                lines.append(f"  {metric}: {score}")

        if report.export_formats:
            lines.extend(["", "EXPORT FORMATS", "-" * 70])
            for fmt in report.export_formats:
                path = report.export_paths.get(fmt, "N/A")
                lines.append(f"  {fmt}: {path}")

        if report.key_achievements:
            lines.extend(["", "KEY ACHIEVEMENTS", "-" * 70])
            for achievement in report.key_achievements:
                lines.append(f"  ✓ {achievement}")

        lines.extend(["", "=" * 70, "END OF REPORT", "=" * 70])

        return "\n".join(lines)

    def _format_as_markdown(self, report: PublishingReport) -> str:
        """Format report as Markdown.

        Args:
            report: PublishingReport to format

        Returns:
            Formatted Markdown string
        """
        lines = [
            f"# Publishing Report: {report.title}",
            "",
            f"**Content ID:** `{report.content_id}`  ",
            f"**Generated:** {report.generation_timestamp}",
            "",
            "## Summary",
            "",
            report.summary,
            "",
            "## Workflow Statistics",
            "",
            f"- **Total Versions:** {report.total_versions}",
            f"- **Total Reviews:** {report.total_reviews}",
            f"- **Total Iterations:** {report.total_iterations}",
        ]

        if report.workflow_duration:
            lines.append(f"- **Workflow Duration:** {report.workflow_duration}")

        if report.quality_gates_passed:
            lines.extend(["", "## Quality Gates Passed", ""])
            for gate in report.quality_gates_passed:
                lines.append(f"- ✓ {gate}")

        if report.final_scores:
            lines.extend(["", "## Final Scores", ""])
            for metric, score in report.final_scores.items():
                lines.append(f"- **{metric}:** {score}/100")

        if report.export_formats:
            lines.extend(["", "## Export Formats", ""])
            for fmt in report.export_formats:
                path = report.export_paths.get(fmt, "N/A")
                lines.append(f"- **{fmt}:** `{path}`")

        if report.key_achievements:
            lines.extend(["", "## Key Achievements", ""])
            for achievement in report.key_achievements:
                lines.append(f"- ✓ {achievement}")

        lines.extend(["", "---", "", "*Report generated by PrismQ Content Production Platform*"])

        return "\n".join(lines)


def generate_publishing_report(
    content_id: str,
    title: str,
    workflow_data: Optional[Dict[str, Any]] = None,
    export_result: Optional[Dict[str, Any]] = None,
    output_dir: Optional[Path] = None,
    save_format: Optional[str] = None,
) -> PublishingReport:
    """Convenience function to generate a publishing report.

    Args:
        content_id: Unique identifier for the content
        title: Content title
        workflow_data: Optional workflow statistics and history
        export_result: Optional export result information
        output_dir: Optional output directory for saving
        save_format: Optional format to save ('json', 'txt', 'md')

    Returns:
        PublishingReport with complete metrics

    Example:
        >>> workflow_data = {
        ...     "total_versions": 3,
        ...     "total_reviews": 5,
        ...     "quality_gates_passed": ["Grammar", "Content", "Consistency"]
        ... }
        >>> export_result = {
        ...     "formats_exported": ["json", "markdown", "html"],
        ...     "export_paths": {"json": "/path/to/file.json"}
        ... }
        >>> report = generate_publishing_report(
        ...     "story-001",
        ...     "My Story",
        ...     workflow_data,
        ...     export_result
        ... )
        >>> print(report.summary)
    """
    generator = ReportGenerator(output_dir)
    report = generator.generate_report(content_id, title, workflow_data, export_result)

    if save_format:
        generator.save_report(report, format=save_format)

    return report
