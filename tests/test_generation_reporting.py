import json

from wordsearch.domain.book import ThematicGenerationOptions
from wordsearch.domain.page_plan import PagePlan
from wordsearch.generation.book_assembly import RenderedBookImages
from wordsearch.generation.difficulty import DifficultyLevel
from wordsearch.generation.reporting import (
    REPORT_FILENAME,
    REPORT_SCHEMA_VERSION,
    build_thematic_generation_report,
    write_generation_report,
)
from wordsearch.validation.render_quality import RenderQualityReport, RenderQualityWarning


def make_options() -> ThematicGenerationOptions:
    return ThematicGenerationOptions(
        book_title="Report Test Book",
        puzzles_txt_path="wordlists/book_block.txt",
        difficulty=DifficultyLevel.MEDIUM,
        grid_size=14,
        seed=1234,
        clean_output=True,
        preview=True,
        limit=5,
        output_dir="custom_output/report_test",
    )


def make_render_quality_report() -> RenderQualityReport:
    warning = RenderQualityWarning(
        severity="warning",
        code="FACT_TRUNCATED",
        message="Fact was truncated.",
        page_type="puzzle",
        page_number=5,
        puzzle_index=0,
        title="Puzzle 1",
        path="puzzle_1.png",
        details={"line_count": 8, "max_lines_fit": 3},
    )
    return RenderQualityReport(
        schema_version=1,
        warning_count=1,
        by_severity={"warning": 1},
        by_code={"FACT_TRUNCATED": 1},
        warnings=[warning],
    )


def test_build_thematic_generation_report_contains_expected_metadata(tmp_path):
    options = make_options()
    page_plan = PagePlan(
        block_first_page={"Block A": 4, "Block B": 8},
        blocks_in_order=["Block A", "Block B"],
        puzzle_page={0: 5, 1: 6, 2: 9},
        first_solution_page=12,
    )
    rendered_images = RenderedBookImages(
        content_imgs=["title.png", "toc.png", "puzzle.png"],
        solution_imgs=["solution.png"],
    )

    report = build_thematic_generation_report(
        options=options,
        output_dir=str(tmp_path),
        pdf_path=str(tmp_path / "book.pdf"),
        page_plan=page_plan,
        rendered_images=rendered_images,
        puzzle_count=3,
        render_quality_report=make_render_quality_report(),
    )

    assert report.schema_version == REPORT_SCHEMA_VERSION
    assert report.book_title == "Report Test Book"
    assert report.input_path == "wordlists/book_block.txt"
    assert report.difficulty == "MEDIUM"
    assert report.grid_size == 14
    assert report.seed == 1234
    assert report.clean_output is True
    assert report.preview is True
    assert report.limit == 5
    assert report.requested_output_dir == "custom_output/report_test"
    assert report.puzzle_count == 3
    assert report.block_count == 2
    assert report.content_image_count == 3
    assert report.solution_image_count == 1
    assert report.first_solution_page == 12
    assert report.output_dir == str(tmp_path)
    assert report.pdf_path == str(tmp_path / "book.pdf")
    assert report.generated_at_utc
    assert report.render_quality["warning_count"] == 1
    assert report.render_quality["by_code"] == {"FACT_TRUNCATED": 1}
    assert report.render_quality["warnings"][0]["code"] == "FACT_TRUNCATED"


def test_build_thematic_generation_report_defaults_to_empty_render_quality(tmp_path):
    report = build_thematic_generation_report(
        options=make_options(),
        output_dir=str(tmp_path),
        pdf_path=str(tmp_path / "book.pdf"),
        page_plan=PagePlan(
            block_first_page={},
            blocks_in_order=[],
            puzzle_page={0: 4},
            first_solution_page=6,
        ),
        rendered_images=RenderedBookImages(
            content_imgs=["content.png"],
            solution_imgs=["solution.png"],
        ),
        puzzle_count=1,
    )

    assert report.render_quality == {
        "schema_version": 1,
        "warning_count": 0,
        "by_severity": {},
        "by_code": {},
        "warnings": [],
    }


def test_write_generation_report_writes_json_file(tmp_path):
    report = build_thematic_generation_report(
        options=make_options(),
        output_dir=str(tmp_path),
        pdf_path=str(tmp_path / "book.pdf"),
        page_plan=PagePlan(
            block_first_page={},
            blocks_in_order=[],
            puzzle_page={0: 4},
            first_solution_page=6,
        ),
        rendered_images=RenderedBookImages(
            content_imgs=["content.png"],
            solution_imgs=["solution.png"],
        ),
        puzzle_count=1,
        render_quality_report=make_render_quality_report(),
    )

    report_path = write_generation_report(report, output_dir=str(tmp_path))

    assert report_path == str(tmp_path / REPORT_FILENAME)
    payload = json.loads((tmp_path / REPORT_FILENAME).read_text(encoding="utf-8"))
    assert payload["schema_version"] == REPORT_SCHEMA_VERSION
    assert payload["book_title"] == "Report Test Book"
    assert payload["pdf_path"] == str(tmp_path / "book.pdf")
    assert payload["preview"] is True
    assert payload["limit"] == 5
    assert payload["requested_output_dir"] == "custom_output/report_test"
    assert payload["render_quality"]["warning_count"] == 1
