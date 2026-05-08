"""Human-readable production review summary for thematic book runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from wordsearch.config.paths import build_output_file

PRODUCTION_REVIEW_SUMMARY_FILENAME = "production_review_summary.txt"
MAX_INSPECTION_ITEMS = 12


@dataclass(frozen=True)
class ReviewInspectionItem:
    """One generated page or asset that deserves manual inspection."""

    code: str
    severity: str
    page_type: str | None = None
    page_number: int | None = None
    puzzle_index: int | None = None
    title: str | None = None
    path: str | None = None
    message: str | None = None


@dataclass(frozen=True)
class ProductionReviewSummary:
    """Concise final review snapshot for a generated thematic book."""

    book_title: str
    pdf_path: str
    generation_report_path: str
    preflight_report_path: str
    visual_regression_report_path: str | None
    page_count: int
    puzzle_count: int
    preflight_error_count: int
    preflight_warning_count: int
    render_warning_count: int
    render_error_count: int
    render_info_count: int
    inspection_items: list[ReviewInspectionItem] = field(default_factory=list)
    recommendation: str = ""

    def to_text(self) -> str:
        """Return a readable, copy-friendly production review summary."""
        lines = [
            "=== Production review summary ===",
            f"Book: {self.book_title}",
            f"PDF: {self.pdf_path}",
            f"Pages: {self.page_count}",
            f"Puzzles: {self.puzzle_count}",
            f"Generation report: {self.generation_report_path}",
            f"Preflight report: {self.preflight_report_path}",
        ]
        if self.visual_regression_report_path:
            lines.append(f"Visual regression report: {self.visual_regression_report_path}")

        lines.extend(
            [
                "",
                "Preflight:",
                f"- errors: {self.preflight_error_count}",
                f"- warnings: {self.preflight_warning_count}",
                "",
                "Render quality:",
                f"- errors: {self.render_error_count}",
                f"- warnings: {self.render_warning_count}",
                f"- info: {self.render_info_count}",
            ]
        )

        if self.inspection_items:
            lines.extend(["", "Pages/assets to inspect:"])
            for item in self.inspection_items[:MAX_INSPECTION_ITEMS]:
                lines.append(f"- {_format_inspection_item(item)}")
            remaining = len(self.inspection_items) - MAX_INSPECTION_ITEMS
            if remaining > 0:
                lines.append(f"- ...and {remaining} more item(s).")
        else:
            lines.extend(["", "Pages/assets to inspect: none flagged."])

        lines.extend(["", "Recommendation:", self.recommendation])
        return "\n".join(lines) + "\n"

    def print_summary(self) -> None:
        print("\n" + self.to_text().rstrip())


def build_production_review_summary(
    *,
    book_title: str,
    pdf_path: str,
    generation_report_path: str,
    preflight_report_path: str,
    preflight_report: Any,
    render_quality_report: Any,
    puzzle_count: int,
    visual_regression_report_path: str | None = None,
) -> ProductionReviewSummary:
    """Build a final human-oriented review summary from existing reports."""
    preflight_errors = list(getattr(preflight_report, "errors", []) or [])
    preflight_warnings = list(getattr(preflight_report, "warnings", []) or [])
    render_warnings = list(getattr(render_quality_report, "warnings", []) or [])
    by_severity = dict(getattr(render_quality_report, "by_severity", {}) or {})

    inspection_items = [
        *_items_from_preflight(preflight_errors, severity="error"),
        *_items_from_preflight(preflight_warnings, severity="warning"),
        *_items_from_render_quality(render_warnings),
    ]

    page_count = int(getattr(preflight_report, "actual_page_count", 0) or getattr(preflight_report, "expected_page_count", 0) or 0)
    preflight_error_count = len(preflight_errors)
    preflight_warning_count = len(preflight_warnings)
    render_error_count = int(by_severity.get("error", 0))
    render_warning_count = int(by_severity.get("warning", 0))
    render_info_count = int(by_severity.get("info", 0))

    recommendation = _build_recommendation(
        preflight_error_count=preflight_error_count,
        preflight_warning_count=preflight_warning_count,
        render_error_count=render_error_count,
        render_warning_count=render_warning_count,
        render_info_count=render_info_count,
        visual_regression_report_path=visual_regression_report_path,
    )

    return ProductionReviewSummary(
        book_title=book_title,
        pdf_path=pdf_path,
        generation_report_path=generation_report_path,
        preflight_report_path=preflight_report_path,
        visual_regression_report_path=visual_regression_report_path,
        page_count=page_count,
        puzzle_count=puzzle_count,
        preflight_error_count=preflight_error_count,
        preflight_warning_count=preflight_warning_count,
        render_warning_count=render_warning_count,
        render_error_count=render_error_count,
        render_info_count=render_info_count,
        inspection_items=inspection_items,
        recommendation=recommendation,
    )


def write_production_review_summary(summary: ProductionReviewSummary, *, output_dir: str) -> str:
    """Write the production review summary text file and return its path."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    summary_path = build_output_file(output_dir, PRODUCTION_REVIEW_SUMMARY_FILENAME)
    Path(summary_path).write_text(summary.to_text(), encoding="utf-8")
    return summary_path


def _items_from_preflight(issues: Iterable[Any], *, severity: str) -> list[ReviewInspectionItem]:
    items: list[ReviewInspectionItem] = []
    for issue in issues:
        items.append(
            ReviewInspectionItem(
                code="PREFLIGHT",
                severity=severity,
                path=getattr(issue, "path", None),
                message=getattr(issue, "message", None),
            )
        )
    return items


def _items_from_render_quality(warnings: Iterable[Any]) -> list[ReviewInspectionItem]:
    items: list[ReviewInspectionItem] = []
    for warning in warnings:
        items.append(
            ReviewInspectionItem(
                code=str(getattr(warning, "code", "RENDER_QUALITY")),
                severity=str(getattr(warning, "severity", "warning")),
                page_type=getattr(warning, "page_type", None),
                page_number=getattr(warning, "page_number", None),
                puzzle_index=getattr(warning, "puzzle_index", None),
                title=getattr(warning, "title", None),
                path=getattr(warning, "path", None),
                message=getattr(warning, "message", None),
            )
        )
    return items


def _format_inspection_item(item: ReviewInspectionItem) -> str:
    parts = [f"{item.severity.upper()} {item.code}"]
    location = _format_location(item)
    if location:
        parts.append(location)
    if item.path:
        parts.append(item.path)
    if item.message:
        parts.append(item.message)
    return " | ".join(parts)


def _format_location(item: ReviewInspectionItem) -> str:
    pieces = []
    if item.page_type:
        pieces.append(item.page_type)
    if item.page_number is not None:
        pieces.append(f"page {item.page_number}")
    if item.puzzle_index is not None:
        pieces.append(f"puzzle index {item.puzzle_index}")
    if item.title:
        pieces.append(item.title)
    return ", ".join(pieces)


def _build_recommendation(
    *,
    preflight_error_count: int,
    preflight_warning_count: int,
    render_error_count: int,
    render_warning_count: int,
    render_info_count: int,
    visual_regression_report_path: str | None,
) -> str:
    if preflight_error_count or render_error_count:
        return "Fix blocking errors before using this PDF for publication."
    if preflight_warning_count or render_warning_count:
        return "Review the flagged pages/assets before full production or KDP upload."
    if render_info_count:
        return "No blocking issues found; skim the informational render-quality pages before publishing."
    if visual_regression_report_path:
        return "Preview looks clean; compare visual fingerprints if this run is validating layout changes."
    return "No automated issues found. Do a final manual PDF review before publishing."
