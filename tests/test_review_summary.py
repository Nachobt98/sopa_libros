from types import SimpleNamespace

from wordsearch.generation.review_summary import (
    ProductionReviewSummary,
    build_production_review_summary,
    write_production_review_summary,
)


def test_build_production_review_summary_recommends_fixing_blocking_errors():
    preflight_report = SimpleNamespace(
        actual_page_count=12,
        expected_page_count=12,
        errors=[SimpleNamespace(message="Bad PDF size", path="book.pdf")],
        warnings=[],
    )
    render_quality_report = SimpleNamespace(
        warnings=[
            SimpleNamespace(
                severity="error",
                code="GRID_CELL_SMALL",
                page_type="puzzle",
                page_number=4,
                puzzle_index=0,
                title="Puzzle",
                path="puzzle_1.png",
                message="Grid cells are small.",
            )
        ],
        by_severity={"error": 1},
    )

    summary = build_production_review_summary(
        book_title="Test Book",
        pdf_path="book.pdf",
        generation_report_path="generation_report.json",
        preflight_report_path="preflight_report.json",
        preflight_report=preflight_report,
        render_quality_report=render_quality_report,
        puzzle_count=4,
    )

    assert summary.page_count == 12
    assert summary.preflight_error_count == 1
    assert summary.render_error_count == 1
    assert len(summary.inspection_items) == 2
    assert summary.recommendation == "Fix blocking errors before using this PDF for publication."


def test_summary_text_lists_reports_warnings_and_inspection_items():
    summary = ProductionReviewSummary(
        book_title="Test Book",
        pdf_path="book.pdf",
        generation_report_path="generation_report.json",
        preflight_report_path="preflight_report.json",
        visual_regression_report_path="visual_regression_report.json",
        page_count=10,
        puzzle_count=3,
        preflight_error_count=0,
        preflight_warning_count=1,
        render_warning_count=1,
        render_error_count=0,
        render_info_count=2,
        inspection_items=[],
        recommendation="Review the flagged pages/assets before full production or KDP upload.",
    )

    text = summary.to_text()

    assert "=== Production review summary ===" in text
    assert "Book: Test Book" in text
    assert "Visual regression report: visual_regression_report.json" in text
    assert "- warnings: 1" in text
    assert "Pages/assets to inspect: none flagged." in text
    assert "Review the flagged pages/assets" in text


def test_write_production_review_summary_writes_text_file(tmp_path):
    summary = ProductionReviewSummary(
        book_title="Test Book",
        pdf_path="book.pdf",
        generation_report_path="generation_report.json",
        preflight_report_path="preflight_report.json",
        visual_regression_report_path=None,
        page_count=10,
        puzzle_count=3,
        preflight_error_count=0,
        preflight_warning_count=0,
        render_warning_count=0,
        render_error_count=0,
        render_info_count=0,
        inspection_items=[],
        recommendation="No automated issues found. Do a final manual PDF review before publishing.",
    )

    path = write_production_review_summary(summary, output_dir=str(tmp_path))

    assert path.endswith("production_review_summary.txt")
    assert "No automated issues found" in (tmp_path / "production_review_summary.txt").read_text(encoding="utf-8")
