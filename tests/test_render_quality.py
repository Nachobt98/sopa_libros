from wordsearch.domain.generated_puzzle import GeneratedPuzzle
from wordsearch.domain.grid import PlacedWord
from wordsearch.domain.page_plan import build_page_plan
from wordsearch.domain.puzzle import PuzzleSpec
from wordsearch.validation import render_quality
from wordsearch.validation.render_quality import (
    RenderQualityWarning,
    build_render_quality_report,
)


def make_generated(
    index: int,
    *,
    title="Puzzle Title",
    fact="Short fact.",
    words=None,
    block_name="Block",
    grid_size=14,
):
    words = words or ["WORD", "SEARCH", "PUZZLE"]
    return GeneratedPuzzle(
        spec=PuzzleSpec(index=index, title=title, fact=fact, words=words, block_name=block_name),
        words_for_grid=[word.replace(" ", "") for word in words],
        grid=[["A" for _ in range(grid_size)] for _ in range(grid_size)],
        placed_words=[PlacedWord("WORD", 0, 0, 0, 1)],
    )


def codes(warnings):
    return {warning.code for warning in warnings}


def test_render_quality_report_returns_no_warnings_for_simple_preview():
    generated = [make_generated(0)]
    page_plan = build_page_plan(generated)

    report = build_render_quality_report(
        book_title="Simple Book",
        generated_puzzles=generated,
        page_plan=page_plan,
        content_image_paths=["00_title_page.png", "block_01_block.png", "puzzle_1.png"],
    )

    assert report.warning_count == 0
    assert report.by_code == {}
    assert report.by_severity == {}


def test_analyze_puzzle_title_detects_dense_title():
    warnings = render_quality._analyze_puzzle_title(
        {
            "title_lines": ["Line 1", "Line 2", "Line 3", "Line 4"],
            "title_text": "Dense puzzle title",
        },
        spec_index=0,
        page_number=5,
        title="Dense puzzle title",
        path="puzzle_1.png",
    )

    assert codes(warnings) == {"PUZZLE_TITLE_DENSE"}
    assert warnings[0].severity == "warning"
    assert warnings[0].details["line_count"] == 4


def test_analyze_fun_fact_detects_truncation():
    fact_details = {
        "present": True,
        "char_count": 900,
        "line_count": 12,
        "max_lines_fit": 4,
        "rendered_line_count": 4,
        "truncated": True,
        "used_ratio": 1.0,
    }

    warnings = render_quality._analyze_fun_fact(
        {"fact": fact_details},
        spec_index=0,
        page_number=5,
        title="Puzzle",
        path="puzzle_1.png",
    )

    assert codes(warnings) == {"FACT_TRUNCATED"}
    assert warnings[0].details == fact_details


def test_analyze_fun_fact_detects_tight_card_without_truncation():
    warnings = render_quality._analyze_fun_fact(
        {
            "fact": {
                "present": True,
                "char_count": 260,
                "line_count": 4,
                "max_lines_fit": 4,
                "rendered_line_count": 4,
                "truncated": False,
                "used_ratio": 1.0,
            }
        },
        spec_index=0,
        page_number=5,
        title="Puzzle",
        path="puzzle_1.png",
    )

    assert codes(warnings) == {"FACT_CARD_TIGHT"}
    assert warnings[0].severity == "info"


def test_analyze_word_list_detects_column_overflow_risk():
    warnings = render_quality._analyze_word_list(
        {
            "word_list": {
                "present": True,
                "word_count": 12,
                "fill_ratio": 0.5,
                "forced_layout": False,
                "max_word_width_ratio": 1.2,
                "grid_to_words_compacted": False,
            }
        },
        spec_index=0,
        page_number=5,
        title="Puzzle",
        path="puzzle_1.png",
    )

    assert codes(warnings) == {"WORD_LIST_COLUMN_OVERFLOW_RISK"}
    assert warnings[0].severity == "warning"


def test_analyze_word_list_detects_dense_list_without_overflow():
    warnings = render_quality._analyze_word_list(
        {
            "word_list": {
                "present": True,
                "word_count": 26,
                "fill_ratio": 0.93,
                "forced_layout": False,
                "max_word_width_ratio": 0.75,
                "grid_to_words_compacted": False,
            }
        },
        spec_index=0,
        page_number=5,
        title="Puzzle",
        path="puzzle_1.png",
    )

    assert codes(warnings) == {"WORD_LIST_DENSE"}
    assert warnings[0].severity == "info"


def test_analyze_word_list_detects_spacing_only_when_materially_compacted():
    warnings = render_quality._analyze_word_list(
        {
            "word_list": {
                "present": True,
                "word_count": 31,
                "fill_ratio": 0.96,
                "forced_layout": False,
                "max_word_width_ratio": 0.75,
                "grid_to_words_compacted": True,
            }
        },
        spec_index=0,
        page_number=5,
        title="Puzzle",
        path="puzzle_1.png",
    )

    assert "GRID_WORD_LIST_SPACING_TIGHT" in codes(warnings)


def test_analyze_grid_legibility_detects_small_cells():
    warnings = render_quality._analyze_grid_legibility(
        {
            "cell_size_px": 34,
            "grid_rows": 40,
            "grid_cols": 40,
        },
        spec_index=0,
        page_number=5,
        title="Puzzle",
        path="puzzle_1.png",
    )

    assert codes(warnings) == {"GRID_CELL_SMALL"}
    assert warnings[0].severity == "error"


def test_render_quality_report_groups_warnings_by_code_and_severity(monkeypatch):
    generated = [make_generated(0)]
    page_plan = build_page_plan(generated)
    title_warning = RenderQualityWarning(
        severity="warning",
        code="TITLE_PAGE_DENSE_TITLE",
        message="Dense title.",
        page_type="title_page",
        page_number=1,
    )
    fact_warning = RenderQualityWarning(
        severity="warning",
        code="FACT_TRUNCATED",
        message="Fact truncated.",
        page_type="puzzle",
        page_number=5,
        puzzle_index=0,
    )
    grid_warning = RenderQualityWarning(
        severity="error",
        code="GRID_CELL_SMALL",
        message="Grid too small.",
        page_type="puzzle",
        page_number=5,
        puzzle_index=0,
    )

    monkeypatch.setattr(render_quality, "_analyze_title_page", lambda *args, **kwargs: [title_warning])
    monkeypatch.setattr(render_quality, "_analyze_block_covers", lambda *args, **kwargs: [])
    monkeypatch.setattr(render_quality, "_analyze_puzzle_page", lambda *args, **kwargs: [fact_warning, grid_warning])

    report = build_render_quality_report(
        book_title="Simple Book",
        generated_puzzles=generated,
        page_plan=page_plan,
        content_image_paths=["00_title_page.png", "block_01_block.png", "puzzle_1.png"],
    )

    assert report.warning_count == 3
    assert report.by_code == {
        "TITLE_PAGE_DENSE_TITLE": 1,
        "FACT_TRUNCATED": 1,
        "GRID_CELL_SMALL": 1,
    }
    assert report.by_severity == {"warning": 2, "error": 1}
    payload = report.to_dict()
    assert payload["warnings"][0]["code"] == "TITLE_PAGE_DENSE_TITLE"
