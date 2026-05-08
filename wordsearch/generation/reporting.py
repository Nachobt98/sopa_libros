"""Generation report helpers."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from wordsearch.config.paths import build_output_file
from wordsearch.domain.book import ThematicGenerationOptions
from wordsearch.domain.page_plan import PagePlan
from wordsearch.generation.book_assembly import RenderedBookImages
from wordsearch.validation.render_quality import RenderQualityReport

REPORT_FILENAME = "generation_report.json"
REPORT_SCHEMA_VERSION = 4


@dataclass(frozen=True)
class ThematicGenerationReport:
    """Serializable summary of a successful thematic generation run."""

    schema_version: int
    generated_at_utc: str
    book_title: str
    input_path: str
    difficulty: str
    grid_size: int
    seed: int | None
    clean_output: bool
    preview: bool
    limit: int | None
    requested_output_dir: str | None
    theme_name: str
    format_name: str
    puzzle_count: int
    block_count: int
    content_image_count: int
    solution_image_count: int
    first_solution_page: int
    output_dir: str
    pdf_path: str
    render_quality: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_thematic_generation_report(
    *,
    options: ThematicGenerationOptions,
    output_dir: str,
    pdf_path: str,
    page_plan: PagePlan,
    rendered_images: RenderedBookImages,
    puzzle_count: int,
    render_quality_report: RenderQualityReport | None = None,
) -> ThematicGenerationReport:
    """Build a serializable report for a successful thematic generation run."""
    render_quality = (
        render_quality_report.to_dict()
        if render_quality_report is not None
        else {
            "schema_version": 1,
            "warning_count": 0,
            "by_severity": {},
            "by_code": {},
            "warnings": [],
        }
    )
    return ThematicGenerationReport(
        schema_version=REPORT_SCHEMA_VERSION,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        book_title=options.book_title,
        input_path=options.puzzles_txt_path,
        difficulty=options.difficulty.name,
        grid_size=options.grid_size,
        seed=options.seed,
        clean_output=options.clean_output,
        preview=options.preview,
        limit=options.limit,
        requested_output_dir=options.output_dir,
        theme_name=options.theme_name,
        format_name=options.format_name,
        puzzle_count=puzzle_count,
        block_count=len(page_plan.blocks_in_order),
        content_image_count=len(rendered_images.content_imgs),
        solution_image_count=len(rendered_images.solution_imgs),
        first_solution_page=page_plan.first_solution_page,
        output_dir=output_dir,
        pdf_path=pdf_path,
        render_quality=render_quality,
    )


def write_generation_report(report: ThematicGenerationReport, *, output_dir: str) -> str:
    """Write the generation report JSON and return its path."""
    report_path = build_output_file(output_dir, REPORT_FILENAME)
    Path(report_path).write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return report_path
