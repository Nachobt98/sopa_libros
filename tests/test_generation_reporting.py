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


def make_options() -> ThematicGenerationOptions:
    return ThematicGenerationOptions(
        book_title="Report Test Book",
        puzzles_txt_path="wordlists/book_block.txt",
        difficulty=DifficultyLevel.MEDIUM,
        grid_size=14,
        seed=1234,
        clean_output=True,
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
    )

    assert report.schema_version == REPORT_SCHEMA_VERSION
    assert report.book_title == "Report Test Book"
    assert report.input_path == "wordlists/book_block.txt"
    assert report.difficulty == "MEDIUM"
    assert report.grid_size == 14
    assert report.seed == 1234
    assert report.clean_output is True
    assert report.puzzle_count == 3
    assert report.block_count == 2
    assert report.content_image_count == 3
    assert report.solution_image_count == 1
    assert report.first_solution_page == 12
    assert report.output_dir == str(tmp_path)
    assert report.pdf_path == str(tmp_path / "book.pdf")
    assert report.generated_at_utc


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
    )

    report_path = write_generation_report(report, output_dir=str(tmp_path))

    assert report_path == str(tmp_path / REPORT_FILENAME)
    payload = json.loads((tmp_path / REPORT_FILENAME).read_text(encoding="utf-8"))
    assert payload["schema_version"] == REPORT_SCHEMA_VERSION
    assert payload["book_title"] == "Report Test Book"
    assert payload["pdf_path"] == str(tmp_path / "book.pdf")
