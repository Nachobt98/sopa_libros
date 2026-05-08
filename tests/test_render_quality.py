from wordsearch.domain.generated_puzzle import GeneratedPuzzle
from wordsearch.domain.grid import PlacedWord
from wordsearch.domain.page_plan import build_page_plan
from wordsearch.domain.puzzle import PuzzleSpec
from wordsearch.validation.render_quality import build_render_quality_report


def make_generated(index: int, *, title="Puzzle Title", fact="Short fact.", words=None, block_name="Block", grid_size=14):
    words = words or ["WORD", "SEARCH", "PUZZLE"]
    return GeneratedPuzzle(
        spec=PuzzleSpec(index=index, title=title, fact=fact, words=words, block_name=block_name),
        words_for_grid=[word.replace(" ", "") for word in words],
        grid=[["A" for _ in range(grid_size)] for _ in range(grid_size)],
        placed_words=[PlacedWord("WORD", 0, 0, 0, 1)],
    )


def codes(report):
    return {warning.code for warning in report.warnings}


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


def test_render_quality_detects_dense_book_title():
    generated = [make_generated(0)]
    page_plan = build_page_plan(generated)

    report = build_render_quality_report(
        book_title=" ".join(["Extraordinary"] * 24),
        generated_puzzles=generated,
        page_plan=page_plan,
        content_image_paths=["00_title_page.png", "block_01_block.png", "puzzle_1.png"],
    )

    assert "TITLE_PAGE_DENSE_TITLE" in codes(report) or "TITLE_PAGE_OVERFLOW_RISK" in codes(report)


def test_render_quality_detects_truncated_fact_and_dense_title():
    long_fact = " ".join(["Long contextual detail for this puzzle page"] * 40)
    generated = [make_generated(0, title=" ".join(["Very Long Puzzle Title"] * 10), fact=long_fact)]
    page_plan = build_page_plan(generated)

    report = build_render_quality_report(
        book_title="Simple Book",
        generated_puzzles=generated,
        page_plan=page_plan,
        content_image_paths=["00_title_page.png", "block_01_block.png", "puzzle_1.png"],
    )

    assert "FACT_TRUNCATED" in codes(report)
    assert "PUZZLE_TITLE_DENSE" in codes(report)
    fact_warning = next(warning for warning in report.warnings if warning.code == "FACT_TRUNCATED")
    assert fact_warning.page_number == page_plan.puzzle_page[0]
    assert fact_warning.puzzle_index == 0
    assert fact_warning.path == "puzzle_1.png"
    assert fact_warning.details["truncated"] is True
